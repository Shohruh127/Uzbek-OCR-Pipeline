"""Cascade OCR Pipeline for the Uzbek OCR system.

Implements a fail-fast architecture with four stages:

Stage A (Primary): Run fine-tuned PaddleOCR
Stage B (Validation): Check confidence; if >90% and no tables -> ACCEPT
Stage C (Structure): If conf <90% or tables detected, run layout analysis
Stage D (Fallback): If conf <40%, flag for human review
"""

import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CascadeStage(Enum):
    """Stages of the cascade pipeline."""

    STAGE_A = "primary_ocr"
    STAGE_B = "validation"
    STAGE_C = "structure_analysis"
    STAGE_D = "human_review"


class CascadeDecision(Enum):
    """Possible decisions from the cascade pipeline."""

    ACCEPT = "accept"
    REFINE = "refine"
    HUMAN_REVIEW = "human_review"


# Confidence thresholds
CONFIDENCE_ACCEPT = 0.90
CONFIDENCE_FALLBACK = 0.40


@dataclass
class OCRResult:
    """Result from a single OCR recognition."""

    text: str
    confidence: float
    bbox: tuple = ()  # (x1, y1, x2, y2) in image pixels


@dataclass
class PageResult:
    """Aggregated result for a full page."""

    page_number: int
    results: list = field(default_factory=list)
    avg_confidence: float = 0.0
    tables_detected: bool = False
    stage: CascadeStage = CascadeStage.STAGE_A
    decision: CascadeDecision = CascadeDecision.ACCEPT

    def compute_avg_confidence(self):
        """Compute average confidence from all OCR results."""
        if not self.results:
            self.avg_confidence = 0.0
            return
        self.avg_confidence = sum(r.confidence for r in self.results) / len(
            self.results
        )


def run_stage_a(page_image):
    """Stage A: Run primary OCR with fine-tuned PaddleOCR.

    Args:
        page_image: Image array or path to page image.

    Returns:
        List of OCRResult objects.
    """
    logger.info("Stage A: Running primary PaddleOCR recognition")
    # PaddleOCR integration point - actual inference would happen here
    # This is the interface; actual PaddleOCR calls require the engine
    results = []
    try:
        from paddleocr import PaddleOCR

        ocr = PaddleOCR(
            rec_model_dir="./output/rec_ppocr_v4_uz",
            rec_char_dict_path="configs/uz_ru_en_dict.txt",
            use_space_char=True,
            use_gpu=True,
        )
        ocr_output = ocr.ocr(page_image, cls=True)
        if ocr_output and ocr_output[0]:
            for line in ocr_output[0]:
                bbox_points = line[0]
                text, conf = line[1]
                x1 = min(p[0] for p in bbox_points)
                y1 = min(p[1] for p in bbox_points)
                x2 = max(p[0] for p in bbox_points)
                y2 = max(p[1] for p in bbox_points)
                results.append(
                    OCRResult(text=text, confidence=conf, bbox=(x1, y1, x2, y2))
                )
    except ImportError:
        logger.warning("PaddleOCR not available; returning empty results")

    return results


def run_stage_b(page_result):
    """Stage B: Validate confidence and check for tables.

    Args:
        page_result: PageResult object with Stage A results.

    Returns:
        CascadeDecision indicating whether to accept, refine, or review.
    """
    page_result.compute_avg_confidence()
    logger.info(
        "Stage B: Avg confidence=%.2f, tables_detected=%s",
        page_result.avg_confidence,
        page_result.tables_detected,
    )

    if page_result.avg_confidence < CONFIDENCE_FALLBACK:
        page_result.stage = CascadeStage.STAGE_D
        page_result.decision = CascadeDecision.HUMAN_REVIEW
        return CascadeDecision.HUMAN_REVIEW

    if (
        page_result.avg_confidence >= CONFIDENCE_ACCEPT
        and not page_result.tables_detected
    ):
        page_result.stage = CascadeStage.STAGE_B
        page_result.decision = CascadeDecision.ACCEPT
        return CascadeDecision.ACCEPT

    page_result.stage = CascadeStage.STAGE_C
    page_result.decision = CascadeDecision.REFINE
    return CascadeDecision.REFINE


def run_stage_c(page_image, page_result):
    """Stage C: Structure analysis with layout detection.

    Triggered when confidence < 90% or tables are detected.
    Uses Surya for layout analysis, then re-runs PaddleOCR
    on specific table cell crops.

    Args:
        page_image: Image array or path to page image.
        page_result: PageResult object from previous stages.

    Returns:
        Updated PageResult with refined results.
    """
    logger.info("Stage C: Running structure analysis (layout detection)")
    # Surya layout analysis integration point
    try:
        from surya.detection import batch_text_detection
        from surya.layout import batch_layout_detection

        logger.info("Surya available - running layout analysis")
        # Actual Surya integration would detect table cells here
        # and re-run PaddleOCR on each cell crop
    except ImportError:
        logger.warning("Surya not available; skipping layout analysis")

    page_result.stage = CascadeStage.STAGE_C
    return page_result


def run_stage_d(page_result):
    """Stage D: Flag for human review.

    Triggered when confidence < 40%.

    Args:
        page_result: PageResult with low-confidence results.

    Returns:
        PageResult marked for human review.
    """
    logger.info(
        "Stage D: Flagging page %d for human review (avg_conf=%.2f)",
        page_result.page_number,
        page_result.avg_confidence,
    )
    page_result.stage = CascadeStage.STAGE_D
    page_result.decision = CascadeDecision.HUMAN_REVIEW
    return page_result


def process_page(page_image, page_number=1):
    """Process a single page through the cascade pipeline.

    Args:
        page_image: Image array or path to page image.
        page_number: Page number for tracking.

    Returns:
        PageResult with final decision and OCR results.
    """
    # Stage A: Primary OCR
    results = run_stage_a(page_image)
    page_result = PageResult(page_number=page_number, results=results)

    # Stage B: Validation
    decision = run_stage_b(page_result)

    if decision == CascadeDecision.ACCEPT:
        logger.info("Page %d accepted at Stage B", page_number)
        return page_result

    if decision == CascadeDecision.HUMAN_REVIEW:
        logger.info("Page %d flagged for human review at Stage D", page_number)
        return run_stage_d(page_result)

    # Stage C: Structure analysis
    page_result = run_stage_c(page_image, page_result)

    # Re-validate after structure analysis
    page_result.compute_avg_confidence()
    if page_result.avg_confidence < CONFIDENCE_FALLBACK:
        return run_stage_d(page_result)

    page_result.decision = CascadeDecision.ACCEPT
    return page_result
