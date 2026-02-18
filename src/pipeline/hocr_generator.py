"""HOCR generation module for the Uzbek OCR Pipeline.

Generates HOCR 1.0 compliant output from OCR results,
suitable for use with OCRmyPDF to create searchable PDF/A documents.

HOCR embeds bounding box coordinates and confidence scores
for each recognized word.
"""

import html
import logging

from src.utils.coordinates import bbox_pixels_to_pdf

logger = logging.getLogger(__name__)

HOCR_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="uz" lang="uz">
<head>
    <title>OCR Output</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="ocr-system" content="Uzbek-OCR-Pipeline v2.0" />
    <meta name="ocr-capabilities" content="ocr_page ocr_carea ocr_line ocrx_word" />
</head>
<body>
"""

HOCR_FOOTER = """</body>
</html>
"""


def sort_results_reading_order(results):
    """Sort OCR results in reading order (top-to-bottom, left-to-right).

    Args:
        results: List of OCRResult objects with bbox attributes.

    Returns:
        Sorted list of OCRResult objects.
    """
    return sorted(results, key=lambda r: (r.bbox[1], r.bbox[0]) if r.bbox else (0, 0))


def _format_bbox(bbox):
    """Format a bounding box as HOCR bbox string.

    Args:
        bbox: Tuple of (x1, y1, x2, y2) in pixels.

    Returns:
        HOCR bbox attribute string, e.g., 'bbox 100 200 300 400'.
    """
    return "bbox {} {} {} {}".format(
        int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    )


def generate_hocr(page_result, page_width, page_height, image_dpi=300):
    """Generate HOCR XML for a single page.

    Args:
        page_result: PageResult object containing OCR results.
        page_width: Page width in pixels.
        page_height: Page height in pixels.
        image_dpi: Resolution of the scanned image.

    Returns:
        String containing HOCR XML content.
    """
    sorted_results = sort_results_reading_order(page_result.results)

    page_bbox = _format_bbox((0, 0, page_width, page_height))
    lines = [HOCR_HEADER]
    lines.append(
        f'<div class="ocr_page" id="page_{page_result.page_number}" '
        f'title="{page_bbox}; image; ppageno {page_result.page_number - 1}">'
    )
    lines.append(f'  <div class="ocr_carea" id="block_{page_result.page_number}_1">')

    for idx, result in enumerate(sorted_results, 1):
        if not result.bbox:
            continue

        word_bbox = _format_bbox(result.bbox)
        conf = int(result.confidence * 100)
        escaped_text = html.escape(result.text)

        lines.append(
            f'    <span class="ocr_line" id="line_{page_result.page_number}_{idx}" '
            f'title="{word_bbox}">'
        )
        lines.append(
            f'      <span class="ocrx_word" '
            f'id="word_{page_result.page_number}_{idx}" '
            f'title="{word_bbox}; x_wconf {conf}">{escaped_text}</span>'
        )
        lines.append("    </span>")

    lines.append("  </div>")
    lines.append("</div>")
    lines.append(HOCR_FOOTER)

    return "\n".join(lines)


def write_hocr(page_result, output_path, page_width, page_height, image_dpi=300):
    """Write HOCR file for a single page.

    Args:
        page_result: PageResult object containing OCR results.
        output_path: Path to write the HOCR file.
        page_width: Page width in pixels.
        page_height: Page height in pixels.
        image_dpi: Resolution of the scanned image.
    """
    hocr_content = generate_hocr(page_result, page_width, page_height, image_dpi)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(hocr_content)
    logger.info("HOCR written to %s", output_path)
