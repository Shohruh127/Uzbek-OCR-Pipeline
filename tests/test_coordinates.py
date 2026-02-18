"""Tests for the coordinate transformation module."""

import math

from src.config import IMAGE_DPI, PDF_DPI
from src.coordinates import (
    pixel_bbox_to_pdf_bbox,
    pixel_to_pdf_x,
    pixel_to_pdf_y,
    transform_ocr_results,
)


class TestPixelToPdfX:
    """Tests for x-coordinate conversion."""

    def test_zero(self):
        assert pixel_to_pdf_x(0) == 0.0

    def test_known_value(self):
        # 300 pixels at 300 DPI = 1 inch = 72 points
        result = pixel_to_pdf_x(300, dpi=300)
        assert math.isclose(result, 72.0, rel_tol=1e-9)

    def test_formula(self):
        x = 150
        expected = x * (72 / 300)
        assert math.isclose(pixel_to_pdf_x(x), expected, rel_tol=1e-9)

    def test_custom_dpi(self):
        x = 600
        dpi = 600
        expected = x * (72 / dpi)
        assert math.isclose(pixel_to_pdf_x(x, dpi=dpi), expected, rel_tol=1e-9)


class TestPixelToPdfY:
    """Tests for y-coordinate conversion (includes origin flip)."""

    def test_top_of_image(self):
        # y=0 at top of image -> should map to max PDF y
        image_height = 3000
        result = pixel_to_pdf_y(0, image_height)
        expected = image_height * (72 / 300)
        assert math.isclose(result, expected, rel_tol=1e-9)

    def test_bottom_of_image(self):
        # y=image_height at bottom -> should map to 0 in PDF
        image_height = 3000
        result = pixel_to_pdf_y(image_height, image_height)
        assert math.isclose(result, 0.0, rel_tol=1e-9)

    def test_middle_of_image(self):
        image_height = 3000
        y = 1500
        expected = (image_height - y) * (72 / 300)
        assert math.isclose(
            pixel_to_pdf_y(y, image_height), expected, rel_tol=1e-9
        )


class TestBboxConversion:
    """Tests for full bounding box conversion."""

    def test_full_page_bbox(self):
        image_h = 3300  # 11 inches at 300 DPI
        bbox = (0, 0, 2550, 3300)  # Full US Letter at 300 DPI
        pdf_bbox = pixel_bbox_to_pdf_bbox(bbox, image_h)
        # x_min should be 0
        assert math.isclose(pdf_bbox[0], 0.0, abs_tol=1e-6)
        # y_min should be 0 (bottom-left in PDF)
        assert math.isclose(pdf_bbox[1], 0.0, abs_tol=1e-6)
        # x_max = 2550 * 72/300 = 612
        assert math.isclose(pdf_bbox[2], 612.0, rel_tol=1e-6)
        # y_max = 3300 * 72/300 = 792
        assert math.isclose(pdf_bbox[3], 792.0, rel_tol=1e-6)

    def test_y_axis_flipped(self):
        image_h = 3000
        bbox = (100, 200, 500, 400)
        pdf_bbox = pixel_bbox_to_pdf_bbox(bbox, image_h)
        # In PDF, y_min comes from the BOTTOM of the image bbox (y_max=400)
        # pdf_y_min = (3000 - 400) * 72/300 = 2600 * 0.24 = 624
        # pdf_y_max = (3000 - 200) * 72/300 = 2800 * 0.24 = 672
        assert pdf_bbox[1] < pdf_bbox[3]  # y_min < y_max in PDF


class TestTransformOCRResults:
    """Tests for batch transformation of OCR results."""

    def test_adds_pdf_bbox(self):
        results = [
            {"bbox": (100, 200, 300, 250), "text": "Hello"},
            {"bbox": (100, 300, 300, 350), "text": "World"},
        ]
        transformed = transform_ocr_results(results, image_height_pixels=3300)
        for t in transformed:
            assert "pdf_bbox" in t
            assert len(t["pdf_bbox"]) == 4

    def test_preserves_original_data(self):
        results = [{"bbox": (0, 0, 100, 50), "text": "Test", "confidence": 0.95}]
        transformed = transform_ocr_results(results, image_height_pixels=3300)
        assert transformed[0]["text"] == "Test"
        assert transformed[0]["confidence"] == 0.95
        assert transformed[0]["bbox"] == (0, 0, 100, 50)

    def test_empty_results(self):
        assert transform_ocr_results([], image_height_pixels=3300) == []
