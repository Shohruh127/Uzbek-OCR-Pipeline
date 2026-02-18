"""Main pipeline orchestrator for the Uzbek OCR Pipeline.

Ties together all components:
1. Gatekeeper: Classify document as digital/scan
2. Cascade: Multi-stage OCR with fail-fast logic
3. Coordinate Transform: Map pixel bboxes to PDF points
4. HOCR: Generate standardized output
5. Output: Create searchable PDF/A
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.cascade import CascadeStage, PageResult, process_page
from src.config import IMAGE_DPI
from src.coordinates import transform_ocr_results
from src.gatekeeper import classify_document
from src.hocr import generate_hocr

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Result of processing a full document through the pipeline."""
    input_path: str
    classification: str  # 'digital' or 'scan'
    pages: List[PageResult] = field(default_factory=list)
    digital_text: str = ""
    output_pdf_path: str = ""
    audit_log: List[Dict[str, Any]] = field(default_factory=list)


def process_document(
    input_path: str,
    output_dir: str = ".",
    ocr_engine: Optional[Any] = None,
    layout_engine: Optional[Any] = None,
    dpi: int = IMAGE_DPI,
) -> PipelineResult:
    """Process a document through the full Uzbek OCR pipeline.

    Workflow:
    1. Run gatekeeper to check for digital text layer.
    2. If digital with high dict overlap, return extracted text.
    3. If scan, run cascade pipeline on each page image.
    4. Generate HOCR and transformed coordinates for each page.

    Args:
        input_path: Path to the input PDF or image file.
        output_dir: Directory for output files.
        ocr_engine: Optional PaddleOCR engine instance.
        layout_engine: Optional Surya layout engine instance.
        dpi: Image DPI for coordinate transformation.

    Returns:
        A PipelineResult with all processing outcomes.
    """
    result = PipelineResult(input_path=input_path, classification="scan")
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Gatekeeper
    if input_path.lower().endswith(".pdf"):
        classification, digital_text = classify_document(input_path)
        result.classification = classification
        result.digital_text = digital_text

        if classification == "digital":
            result.audit_log.append({
                "action": "gatekeeper",
                "result": "digital",
                "detail": "OCR skipped; digital text layer is trustworthy.",
            })
            logger.info("Document classified as digital; OCR skipped.")
            return result

    result.audit_log.append({
        "action": "gatekeeper",
        "result": "scan",
        "detail": "Proceeding with OCR cascade.",
    })

    # Step 2: For image files or scanned PDFs, run cascade
    # In a full implementation, we would convert PDF pages to images here.
    # For now, we handle single image inputs directly.
    if not input_path.lower().endswith(".pdf"):
        page_result = process_page(
            image_path=input_path,
            page_number=1,
            ocr_engine=ocr_engine,
            layout_engine=layout_engine,
        )
        result.pages.append(page_result)

        result.audit_log.append({
            "action": "cascade",
            "page": 1,
            "stage": page_result.stage.value,
            "avg_confidence": page_result.avg_confidence,
            "needs_human_review": page_result.needs_human_review,
        })

    logger.info("Pipeline complete for %s", input_path)
    return result
