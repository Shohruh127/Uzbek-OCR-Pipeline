"""Coordinate transformation between image pixels and PDF points.

Implements the coordinate math from Phase 3, Section 5.3:
- Maps image coordinates (pixels at IMAGE_DPI) to PDF coordinates (points at 72 DPI).
- Handles the origin mismatch: image origin is top-left, PDF origin is bottom-left.
"""

from typing import List, Tuple

from src.config import IMAGE_DPI, PDF_DPI


def pixel_to_pdf_x(x_pixel: float, dpi: int = IMAGE_DPI) -> float:
    """Convert an x-coordinate from image pixels to PDF points.

    Formula: X_pdf = X_pixel * (72 / DPI)

    Args:
        x_pixel: The x-coordinate in image pixels.
        dpi: The image resolution in DPI (default: 300).

    Returns:
        The x-coordinate in PDF points.
    """
    return x_pixel * (PDF_DPI / dpi)


def pixel_to_pdf_y(
    y_pixel: float, image_height_pixels: float, dpi: int = IMAGE_DPI
) -> float:
    """Convert a y-coordinate from image pixels to PDF points.

    Adjusts for origin mismatch: image is top-left origin, PDF is bottom-left.
    Formula: Y_pdf = (image_height - Y_pixel) * (72 / DPI)

    Args:
        y_pixel: The y-coordinate in image pixels (from top).
        image_height_pixels: The total height of the image in pixels.
        dpi: The image resolution in DPI (default: 300).

    Returns:
        The y-coordinate in PDF points (from bottom).
    """
    return (image_height_pixels - y_pixel) * (PDF_DPI / dpi)


def pixel_bbox_to_pdf_bbox(
    bbox: Tuple[float, float, float, float],
    image_height_pixels: float,
    dpi: int = IMAGE_DPI,
) -> Tuple[float, float, float, float]:
    """Convert a bounding box from image pixel coordinates to PDF point coordinates.

    Input bbox format: (x_min, y_min, x_max, y_max) in pixels (top-left origin).
    Output bbox format: (x_min, y_min, x_max, y_max) in PDF points (bottom-left origin).

    Args:
        bbox: A 4-tuple of (x_min, y_min, x_max, y_max) in image pixels.
        image_height_pixels: The total height of the image in pixels.
        dpi: The image resolution in DPI (default: 300).

    Returns:
        A 4-tuple of (x_min, y_min, x_max, y_max) in PDF points.
    """
    x_min, y_min, x_max, y_max = bbox
    pdf_x_min = pixel_to_pdf_x(x_min, dpi)
    pdf_x_max = pixel_to_pdf_x(x_max, dpi)
    # Note: y_min (top in image) becomes y_max in PDF (bottom-left origin)
    pdf_y_min = pixel_to_pdf_y(y_max, image_height_pixels, dpi)
    pdf_y_max = pixel_to_pdf_y(y_min, image_height_pixels, dpi)
    return (pdf_x_min, pdf_y_min, pdf_x_max, pdf_y_max)


def transform_ocr_results(
    results: List[dict],
    image_height_pixels: float,
    dpi: int = IMAGE_DPI,
) -> List[dict]:
    """Transform a list of OCR result bounding boxes from pixel to PDF coordinates.

    Each result dict must contain a 'bbox' key with (x_min, y_min, x_max, y_max).

    Args:
        results: List of dicts with 'bbox' and 'text' keys.
        image_height_pixels: The total image height in pixels.
        dpi: The image resolution in DPI.

    Returns:
        A new list of dicts with 'pdf_bbox' added to each entry.
    """
    transformed = []
    for r in results:
        entry = dict(r)
        entry["pdf_bbox"] = pixel_bbox_to_pdf_bbox(
            r["bbox"], image_height_pixels, dpi
        )
        transformed.append(entry)
    return transformed
