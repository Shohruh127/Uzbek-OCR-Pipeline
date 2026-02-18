"""HOCR generation module.

Implements HOCR 1.0 output from Phase 4, Section 6.1:
- Sorts recognized text blocks top-to-bottom, left-to-right.
- Injects bbox coordinates (in image pixels for HOCR standard).
- Embeds confidence scores in the x_wconf attribute.
"""

import html
from typing import List

from src.cascade import OCRResult


def _sort_results_reading_order(results: List[OCRResult]) -> List[OCRResult]:
    """Sort OCR results in reading order: top-to-bottom, left-to-right.

    Args:
        results: List of OCRResult objects.

    Returns:
        Sorted list of OCRResult objects.
    """
    return sorted(results, key=lambda r: (r.bbox[1], r.bbox[0]))


def _format_bbox(bbox: tuple) -> str:
    """Format a bounding box tuple for HOCR title attribute.

    Args:
        bbox: (x_min, y_min, x_max, y_max) in image pixels.

    Returns:
        HOCR-formatted bbox string, e.g. 'bbox 100 200 300 250'.
    """
    return "bbox {} {} {} {}".format(
        int(round(bbox[0])),
        int(round(bbox[1])),
        int(round(bbox[2])),
        int(round(bbox[3])),
    )


def generate_hocr(
    results: List[OCRResult],
    page_width: int,
    page_height: int,
    page_number: int = 1,
    image_filename: str = "page.png",
) -> str:
    """Generate an HOCR 1.0 document from OCR results.

    Args:
        results: List of OCRResult objects for the page.
        page_width: Page width in pixels.
        page_height: Page height in pixels.
        page_number: Page number (1-indexed).
        image_filename: The source image filename.

    Returns:
        A string containing the complete HOCR XML document.
    """
    sorted_results = _sort_results_reading_order(results)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\"",
        '  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="uz" lang="uz">',
        "<head>",
        '  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />',
        "  <title>OCR Output</title>",
        '  <meta name="ocr-system" content="Uzbek-OCR-Pipeline v2.0" />',
        '  <meta name="ocr-capabilities"'
        ' content="ocr_page ocr_line ocrx_word" />',
        "</head>",
        "<body>",
        '  <div class="ocr_page" id="page_{}" title="image &quot;{}&quot;; {}">'
        .format(
            page_number,
            html.escape(image_filename, quote=True),
            _format_bbox((0, 0, page_width, page_height)),
        ),
    ]

    for idx, result in enumerate(sorted_results, start=1):
        conf_int = int(round(result.confidence * 100))
        bbox_str = _format_bbox(result.bbox)
        escaped_text = html.escape(result.text)

        lines.append(
            '    <span class="ocrx_word" id="word_{}_{}"'
            ' title="{};x_wconf {}">{}</span>'.format(
                page_number,
                idx,
                bbox_str,
                conf_int,
                escaped_text,
            )
        )

    lines.append("  </div>")
    lines.append("</body>")
    lines.append("</html>")

    return "\n".join(lines)
