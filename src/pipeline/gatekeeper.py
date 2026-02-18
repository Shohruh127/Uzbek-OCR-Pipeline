"""Gatekeeper module for the Uzbek OCR Pipeline.

The Gatekeeper determines whether a document needs OCR processing
by checking for an existing digital text layer in PDF files.

Logic:
1. Check if PDF has extractable text using PyMuPDF.
2. If extractable text exists and dictionary overlap > 80%, skip OCR.
3. Otherwise, proceed to the cascade pipeline.
"""

import logging

logger = logging.getLogger(__name__)

# Threshold for dictionary overlap to accept digital text
DICTIONARY_OVERLAP_THRESHOLD = 0.80


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF using PyMuPDF (fitz).

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Tuple of (text, page_count) where text is the concatenated
        text from all pages.
    """
    import fitz  # PyMuPDF

    text_parts = []
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts), page_count


def should_skip_ocr(pdf_path, dictionary_chars, threshold=None):
    """Determine if OCR can be skipped for a given PDF.

    Args:
        pdf_path: Path to the PDF file.
        dictionary_chars: Set of valid characters from the dictionary.
        threshold: Dictionary overlap threshold (default: 0.80).

    Returns:
        Tuple of (skip_ocr, reason) where skip_ocr is a boolean
        and reason is a human-readable explanation.
    """
    from src.utils.dictionary import compute_dictionary_overlap

    if threshold is None:
        threshold = DICTIONARY_OVERLAP_THRESHOLD

    try:
        text, page_count = extract_text_from_pdf(pdf_path)
    except Exception as e:
        logger.warning("Failed to extract text from %s: %s", pdf_path, e)
        return False, f"Text extraction failed: {e}"

    if not text or not text.strip():
        return False, "No extractable text found (scanned document)"

    overlap = compute_dictionary_overlap(text, dictionary_chars)
    logger.info(
        "PDF %s: %d pages, dictionary overlap: %.2f%%",
        pdf_path,
        page_count,
        overlap * 100,
    )

    if overlap > threshold:
        return True, (
            f"Digital text layer found with {overlap:.1%} dictionary overlap "
            f"(threshold: {threshold:.0%})"
        )

    return False, (
        f"Digital text has low dictionary overlap: {overlap:.1%} "
        f"(threshold: {threshold:.0%})"
    )
