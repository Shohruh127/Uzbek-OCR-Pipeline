"""Coordinate transformation utilities for OCR pipeline.

Handles conversion between image pixel coordinates (at scan DPI)
and PDF point coordinates (72 DPI), including origin adjustment
(image top-left vs PDF bottom-left).
"""


def pixels_to_pdf_points(x_pixel, y_pixel, image_dpi=300):
    """Convert image pixel coordinates to PDF point coordinates.

    PDF points are 1/72 inch. Image pixels depend on scan DPI.

    Args:
        x_pixel: X coordinate in pixels.
        y_pixel: Y coordinate in pixels.
        image_dpi: Resolution of the scanned image (default: 300).

    Returns:
        Tuple of (x_pdf, y_pdf) in PDF points.
    """
    scale = 72.0 / image_dpi
    x_pdf = x_pixel * scale
    y_pdf = y_pixel * scale
    return x_pdf, y_pdf


def bbox_pixels_to_pdf(bbox, page_height_pixels, image_dpi=300):
    """Convert a bounding box from image pixels to PDF coordinates.

    Adjusts for the origin difference: images use top-left origin,
    PDFs use bottom-left origin.

    Args:
        bbox: Tuple of (x1, y1, x2, y2) in image pixels where
              (x1, y1) is top-left and (x2, y2) is bottom-right.
        page_height_pixels: Total height of the page in pixels.
        image_dpi: Resolution of the scanned image (default: 300).

    Returns:
        Tuple of (x1_pdf, y1_pdf, x2_pdf, y2_pdf) in PDF points
        with bottom-left origin.
    """
    x1, y1, x2, y2 = bbox
    scale = 72.0 / image_dpi

    x1_pdf = x1 * scale
    x2_pdf = x2 * scale

    # Flip Y axis: PDF origin is bottom-left, image origin is top-left
    y1_pdf = (page_height_pixels - y2) * scale
    y2_pdf = (page_height_pixels - y1) * scale

    return x1_pdf, y1_pdf, x2_pdf, y2_pdf


def pdf_to_pixels(x_pdf, y_pdf, image_dpi=300):
    """Convert PDF point coordinates back to image pixel coordinates.

    Args:
        x_pdf: X coordinate in PDF points.
        y_pdf: Y coordinate in PDF points.
        image_dpi: Resolution of the target image (default: 300).

    Returns:
        Tuple of (x_pixel, y_pixel) in image pixels.
    """
    scale = image_dpi / 72.0
    x_pixel = x_pdf * scale
    y_pixel = y_pdf * scale
    return x_pixel, y_pixel
