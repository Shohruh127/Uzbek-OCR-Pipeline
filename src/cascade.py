"""Cascade OCR pipeline implementing the fail-fast architecture.

Implements the Cascade Logic from Phase 3, Section 5.2:
- Stage A (Primary): Run PaddleOCR recognition.
- Stage B (Validation): Check average confidence; accept if > 90% and no tables.
- Stage C (Structure): If confidence < 90% or tables detected, run layout analysis.
- Stage D (Fallback): If confidence < 40%, flag for human review.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from src.config import CONFIDENCE_HIGH, CONFIDENCE_LOW

logger = logging.getLogger(__name__)


class CascadeStage(str, Enum):
    """The stage at which the cascade pipeline concluded."""
    STAGE_A = "primary"
    STAGE_B = "accepted"
    STAGE_C = "structure"
    STAGE_D = "human_review"


@dataclass
class OCRResult:
    """A single OCR result for a text region."""
    text: str
    confidence: float
    bbox: tuple  # (x_min, y_min, x_max, y_max) in image pixels


@dataclass
class PageResult:
    """The result of processing a single page through the cascade."""
    page_number: int
    stage: CascadeStage
    results: List[OCRResult] = field(default_factory=list)
    avg_confidence: float = 0.0
    tables_detected: bool = False
    needs_human_review: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


def compute_avg_confidence(results: List[OCRResult]) -> float:
    """Compute the average confidence score from a list of OCR results.

    Args:
        results: List of OCRResult objects.

    Returns:
        Average confidence as a float between 0.0 and 1.0.
    """
    if not results:
        return 0.0
    return sum(r.confidence for r in results) / len(results)


def run_stage_a(image_path: str, ocr_engine: Optional[Any] = None) -> List[OCRResult]:
    """Stage A (Primary): Run fine-tuned PaddleOCR on the image.

    Args:
        image_path: Path to the page image.
        ocr_engine: Optional PaddleOCR engine instance. If None, returns empty.

    Returns:
        A list of OCRResult objects with text, confidence, and bounding boxes.
    """
    if ocr_engine is None:
        logger.warning(
            "No OCR engine provided; returning empty results for %s", image_path
        )
        return []

    try:
        raw_results = ocr_engine.ocr(image_path, cls=True)
        results = []
        if raw_results and raw_results[0]:
            for line in raw_results[0]:
                box = line[0]
                text, conf = line[1]
                x_coords = [p[0] for p in box]
                y_coords = [p[1] for p in box]
                bbox = (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
                results.append(OCRResult(text=text, confidence=conf, bbox=bbox))
        return results
    except Exception as e:
        logger.error("Stage A failed for %s: %s", image_path, e)
        return []


def run_stage_b(results: List[OCRResult], tables_detected: bool) -> CascadeStage:
    """Stage B (Validation): Check confidence and table detection.

    Rule: If Conf > 90% AND no tables detected -> ACCEPT.

    Args:
        results: OCR results from Stage A.
        tables_detected: Whether tables were detected on the page.

    Returns:
        CascadeStage.STAGE_B if accepted, else the next stage to run.
    """
    avg_conf = compute_avg_confidence(results)

    if avg_conf > CONFIDENCE_HIGH and not tables_detected:
        logger.info("Stage B: Accepted (avg conf=%.2f, no tables)", avg_conf)
        return CascadeStage.STAGE_B

    if avg_conf < CONFIDENCE_LOW:
        logger.info("Stage B: Low confidence (%.2f); routing to Stage D", avg_conf)
        return CascadeStage.STAGE_D

    logger.info(
        "Stage B: Needs structure analysis (avg conf=%.2f, tables=%s)",
        avg_conf,
        tables_detected,
    )
    return CascadeStage.STAGE_C


def run_stage_c(
    image_path: str,
    initial_results: List[OCRResult],
    ocr_engine: Optional[Any] = None,
    layout_engine: Optional[Any] = None,
) -> List[OCRResult]:
    """Stage C (Structure): Run layout analysis and re-OCR table cells.

    Trigger: Conf < 90% OR table detected.
    Action: Run Surya for layout analysis, then re-run PaddleOCR on cell crops.

    Args:
        image_path: Path to the page image.
        initial_results: Results from Stage A.
        ocr_engine: Optional PaddleOCR engine for cell re-OCR.
        layout_engine: Optional Surya layout engine.

    Returns:
        Refined list of OCRResult objects.
    """
    if layout_engine is None:
        logger.warning("No layout engine provided; returning Stage A results.")
        return initial_results

    logger.info("Stage C: Running layout analysis on %s", image_path)
    # Layout analysis would identify table cells and re-crop for PaddleOCR
    # This is a placeholder for the actual Surya integration
    return initial_results


def process_page(
    image_path: str,
    page_number: int = 1,
    ocr_engine: Optional[Any] = None,
    layout_engine: Optional[Any] = None,
    tables_detected: bool = False,
) -> PageResult:
    """Process a single page through the full cascade pipeline.

    Args:
        image_path: Path to the page image file.
        page_number: The page number (1-indexed).
        ocr_engine: Optional PaddleOCR engine instance.
        layout_engine: Optional Surya layout analysis engine.
        tables_detected: Whether tables have been detected on this page.

    Returns:
        A PageResult with the final stage, results, and metadata.
    """
    # Stage A: Primary OCR
    results = run_stage_a(image_path, ocr_engine)
    avg_conf = compute_avg_confidence(results)

    # Stage B: Validation
    stage = run_stage_b(results, tables_detected)

    if stage == CascadeStage.STAGE_B:
        return PageResult(
            page_number=page_number,
            stage=CascadeStage.STAGE_B,
            results=results,
            avg_confidence=avg_conf,
            tables_detected=tables_detected,
        )

    if stage == CascadeStage.STAGE_D:
        return PageResult(
            page_number=page_number,
            stage=CascadeStage.STAGE_D,
            results=results,
            avg_confidence=avg_conf,
            tables_detected=tables_detected,
            needs_human_review=True,
        )

    # Stage C: Structure analysis
    refined_results = run_stage_c(image_path, results, ocr_engine, layout_engine)
    refined_avg_conf = compute_avg_confidence(refined_results)

    # After Stage C, check if we still need human review
    if refined_avg_conf < CONFIDENCE_LOW:
        return PageResult(
            page_number=page_number,
            stage=CascadeStage.STAGE_D,
            results=refined_results,
            avg_confidence=refined_avg_conf,
            tables_detected=tables_detected,
            needs_human_review=True,
        )

    return PageResult(
        page_number=page_number,
        stage=CascadeStage.STAGE_C,
        results=refined_results,
        avg_confidence=refined_avg_conf,
        tables_detected=tables_detected,
    )
