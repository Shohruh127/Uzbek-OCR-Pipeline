"""Gatekeeper module: determines whether OCR is needed for a document.

Implements the "Gatekeeper" classifier from Phase 3, Section 5.1:
- Checks if a PDF has an extractable digital text layer (via PyMuPDF).
- Computes dictionary overlap to decide if the text is trustworthy.
- If the text is digital and overlap > 80%, OCR is skipped.
"""

import logging
from pathlib import Path
from typing import Tuple

from src.config import DICT_OVERLAP_THRESHOLD, load_character_set

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract digital text from a PDF using PyMuPDF.

    Args:
        pdf_path: Path to the input PDF file.

    Returns:
        Concatenated text from all pages, or empty string if extraction fails.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.warning("PyMuPDF not installed; cannot extract digital text.")
        return ""

    text_parts = []
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
    except Exception as e:
        logger.error("Failed to extract text from %s: %s", pdf_path, e)
        return ""
    return "\n".join(text_parts)


def compute_dict_overlap(text: str) -> float:
    """Compute the fraction of characters in text that are in our dictionary.

    Args:
        text: The extracted text string.

    Returns:
        A float between 0.0 and 1.0 representing the overlap ratio.
    """
    if not text.strip():
        return 0.0

    char_set = load_character_set()
    if not char_set:
        return 0.0

    total = 0
    matched = 0
    for ch in text:
        if ch in ("\n", "\r", "\t"):
            continue
        total += 1
        if ch in char_set:
            matched += 1

    if total == 0:
        return 0.0
    return matched / total


def classify_document(pdf_path: str) -> Tuple[str, str]:
    """Classify a document as 'digital' (skip OCR) or 'scan' (needs OCR).

    Args:
        pdf_path: Path to the input PDF file.

    Returns:
        A tuple of (classification, extracted_text):
        - classification: 'digital' if OCR can be skipped, 'scan' otherwise.
        - extracted_text: The text extracted from the digital layer (may be empty).
    """
    if not Path(pdf_path).exists():
        logger.error("File does not exist: %s", pdf_path)
        return ("scan", "")

    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        logger.info("No digital text layer found; classifying as scan.")
        return ("scan", "")

    overlap = compute_dict_overlap(text)
    logger.info("Dictionary overlap: %.2f%%", overlap * 100)

    if overlap > DICT_OVERLAP_THRESHOLD:
        logger.info("Digital text layer is trustworthy; skipping OCR.")
        return ("digital", text)

    logger.info("Digital text layer has low dictionary overlap; treating as scan.")
    return ("scan", text)
