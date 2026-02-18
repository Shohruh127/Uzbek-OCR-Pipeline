"""Tests for coordinate transformation utilities."""

import pytest

from src.utils.coordinates import bbox_pixels_to_pdf, pdf_to_pixels, pixels_to_pdf_points


class TestPixelsToPdfPoints:
    """Tests for pixels_to_pdf_points function."""

    def test_origin(self):
        x, y = pixels_to_pdf_points(0, 0, image_dpi=300)
        assert x == 0.0
        assert y == 0.0

    def test_standard_300dpi(self):
        # At 300 DPI, 300 pixels = 1 inch = 72 points
        x, y = pixels_to_pdf_points(300, 300, image_dpi=300)
        assert x == pytest.approx(72.0)
        assert y == pytest.approx(72.0)

    def test_standard_150dpi(self):
        # At 150 DPI, 150 pixels = 1 inch = 72 points
        x, y = pixels_to_pdf_points(150, 150, image_dpi=150)
        assert x == pytest.approx(72.0)
        assert y == pytest.approx(72.0)

    def test_fractional_coordinates(self):
        x, y = pixels_to_pdf_points(100, 200, image_dpi=300)
        assert x == pytest.approx(100 * 72.0 / 300)
        assert y == pytest.approx(200 * 72.0 / 300)

    def test_default_dpi(self):
        x, y = pixels_to_pdf_points(300, 600)
        assert x == pytest.approx(72.0)
        assert y == pytest.approx(144.0)


class TestBboxPixelsToPdf:
    """Tests for bbox_pixels_to_pdf function."""

    def test_origin_adjustment(self):
        """PDF uses bottom-left origin; images use top-left."""
        # A box at the very top of a 3000-pixel-tall image
        # should map to the bottom of the PDF coordinate space
        bbox = (0, 0, 300, 300)  # top-left corner in image
        page_height = 3000
        x1, y1, x2, y2 = bbox_pixels_to_pdf(bbox, page_height, image_dpi=300)

        # In PDF coords, y1 should be near the top (high value)
        # y1 = (3000 - 300) * 72/300 = 2700 * 0.24 = 648
        # y2 = (3000 - 0) * 72/300 = 3000 * 0.24 = 720
        assert x1 == pytest.approx(0.0)
        assert y1 == pytest.approx(648.0)
        assert x2 == pytest.approx(72.0)
        assert y2 == pytest.approx(720.0)

    def test_full_page_bbox(self):
        """Full page bbox should map to full PDF page."""
        bbox = (0, 0, 2550, 3300)  # 8.5x11 inches at 300 DPI
        page_height = 3300
        x1, y1, x2, y2 = bbox_pixels_to_pdf(bbox, page_height, image_dpi=300)

        assert x1 == pytest.approx(0.0)
        assert y1 == pytest.approx(0.0)
        assert x2 == pytest.approx(612.0)  # 8.5 * 72
        assert y2 == pytest.approx(792.0)  # 11 * 72

    def test_bottom_of_image(self):
        """Box at bottom of image should map to top of PDF (low y)."""
        page_height = 3000
        bbox = (0, 2700, 300, 3000)  # bottom of image
        x1, y1, x2, y2 = bbox_pixels_to_pdf(bbox, page_height, image_dpi=300)

        assert y1 == pytest.approx(0.0)
        assert y2 == pytest.approx(72.0)


class TestPdfToPixels:
    """Tests for pdf_to_pixels function."""

    def test_roundtrip_300dpi(self):
        """Converting to PDF points and back should give original pixels."""
        original_x, original_y = 450, 900
        pdf_x, pdf_y = pixels_to_pdf_points(original_x, original_y, image_dpi=300)
        back_x, back_y = pdf_to_pixels(pdf_x, pdf_y, image_dpi=300)
        assert back_x == pytest.approx(original_x)
        assert back_y == pytest.approx(original_y)

    def test_origin(self):
        x, y = pdf_to_pixels(0, 0, image_dpi=300)
        assert x == 0.0
        assert y == 0.0

    def test_one_inch(self):
        # 72 PDF points = 1 inch = 300 pixels at 300 DPI
        x, y = pdf_to_pixels(72, 72, image_dpi=300)
        assert x == pytest.approx(300.0)
        assert y == pytest.approx(300.0)
