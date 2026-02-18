"""Tests for HOCR generation."""

import pytest

from src.pipeline.cascade import OCRResult, PageResult
from src.pipeline.hocr_generator import generate_hocr, sort_results_reading_order


class TestSortResultsReadingOrder:
    """Tests for sort_results_reading_order function."""

    def test_already_sorted(self):
        results = [
            OCRResult(text="First", confidence=0.9, bbox=(0, 0, 100, 20)),
            OCRResult(text="Second", confidence=0.9, bbox=(0, 30, 100, 50)),
        ]
        sorted_r = sort_results_reading_order(results)
        assert sorted_r[0].text == "First"
        assert sorted_r[1].text == "Second"

    def test_reverse_order(self):
        results = [
            OCRResult(text="Second", confidence=0.9, bbox=(0, 30, 100, 50)),
            OCRResult(text="First", confidence=0.9, bbox=(0, 0, 100, 20)),
        ]
        sorted_r = sort_results_reading_order(results)
        assert sorted_r[0].text == "First"
        assert sorted_r[1].text == "Second"

    def test_left_to_right_same_line(self):
        results = [
            OCRResult(text="Right", confidence=0.9, bbox=(200, 0, 300, 20)),
            OCRResult(text="Left", confidence=0.9, bbox=(0, 0, 100, 20)),
        ]
        sorted_r = sort_results_reading_order(results)
        assert sorted_r[0].text == "Left"
        assert sorted_r[1].text == "Right"


class TestGenerateHocr:
    """Tests for generate_hocr function."""

    def test_generates_valid_xml(self):
        results = [
            OCRResult(text="Тест", confidence=0.95, bbox=(100, 200, 300, 240)),
        ]
        page = PageResult(page_number=1, results=results)
        hocr = generate_hocr(page, page_width=2550, page_height=3300)

        assert "<?xml" in hocr
        assert "ocr_page" in hocr
        assert "ocrx_word" in hocr

    def test_contains_text(self):
        results = [
            OCRResult(text="Ўзбекистон", confidence=0.92, bbox=(100, 200, 500, 240)),
        ]
        page = PageResult(page_number=1, results=results)
        hocr = generate_hocr(page, page_width=2550, page_height=3300)

        assert "Ўзбекистон" in hocr

    def test_contains_confidence(self):
        results = [
            OCRResult(text="Test", confidence=0.95, bbox=(100, 200, 300, 240)),
        ]
        page = PageResult(page_number=1, results=results)
        hocr = generate_hocr(page, page_width=2550, page_height=3300)

        assert "x_wconf 95" in hocr

    def test_contains_bbox(self):
        results = [
            OCRResult(text="Test", confidence=0.9, bbox=(100, 200, 300, 240)),
        ]
        page = PageResult(page_number=1, results=results)
        hocr = generate_hocr(page, page_width=2550, page_height=3300)

        assert "bbox 100 200 300 240" in hocr

    def test_escapes_html_entities(self):
        results = [
            OCRResult(
                text='Price < 100 & "quoted"',
                confidence=0.9,
                bbox=(100, 200, 300, 240),
            ),
        ]
        page = PageResult(page_number=1, results=results)
        hocr = generate_hocr(page, page_width=2550, page_height=3300)

        assert "&lt;" in hocr
        assert "&amp;" in hocr
        assert "&quot;" in hocr

    def test_empty_results(self):
        page = PageResult(page_number=1, results=[])
        hocr = generate_hocr(page, page_width=2550, page_height=3300)

        assert "ocr_page" in hocr
        # Should still be valid XML structure
        assert "</div>" in hocr
