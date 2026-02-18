"""Tests for the HOCR generation module."""

from src.cascade import OCRResult
from src.hocr import _format_bbox, _sort_results_reading_order, generate_hocr


class TestSortReadingOrder:
    """Tests for reading order sorting."""

    def test_already_sorted(self):
        results = [
            OCRResult(text="first", confidence=0.9, bbox=(0, 0, 100, 50)),
            OCRResult(text="second", confidence=0.9, bbox=(0, 60, 100, 110)),
        ]
        sorted_r = _sort_results_reading_order(results)
        assert sorted_r[0].text == "first"
        assert sorted_r[1].text == "second"

    def test_reverse_order(self):
        results = [
            OCRResult(text="bottom", confidence=0.9, bbox=(0, 200, 100, 250)),
            OCRResult(text="top", confidence=0.9, bbox=(0, 0, 100, 50)),
        ]
        sorted_r = _sort_results_reading_order(results)
        assert sorted_r[0].text == "top"
        assert sorted_r[1].text == "bottom"

    def test_same_row_left_to_right(self):
        results = [
            OCRResult(text="right", confidence=0.9, bbox=(200, 0, 300, 50)),
            OCRResult(text="left", confidence=0.9, bbox=(0, 0, 100, 50)),
        ]
        sorted_r = _sort_results_reading_order(results)
        assert sorted_r[0].text == "left"
        assert sorted_r[1].text == "right"


class TestFormatBbox:
    """Tests for HOCR bbox formatting."""

    def test_integer_coords(self):
        assert _format_bbox((10, 20, 300, 400)) == "bbox 10 20 300 400"

    def test_float_coords_rounded(self):
        assert _format_bbox((10.4, 20.6, 300.5, 400.1)) == "bbox 10 21 300 400"


class TestGenerateHocr:
    """Tests for full HOCR document generation."""

    def test_valid_xml_structure(self):
        results = [
            OCRResult(text="Hello", confidence=0.95, bbox=(10, 20, 200, 60)),
        ]
        hocr = generate_hocr(results, page_width=2550, page_height=3300)
        assert '<?xml version="1.0"' in hocr
        assert "<html" in hocr
        assert "ocr_page" in hocr
        assert "</html>" in hocr

    def test_contains_word_with_confidence(self):
        results = [
            OCRResult(text="Test", confidence=0.87, bbox=(10, 20, 200, 60)),
        ]
        hocr = generate_hocr(results, page_width=2550, page_height=3300)
        assert "x_wconf 87" in hocr
        assert "Test" in hocr

    def test_bbox_in_output(self):
        results = [
            OCRResult(text="Word", confidence=0.90, bbox=(100, 200, 300, 250)),
        ]
        hocr = generate_hocr(results, page_width=2550, page_height=3300)
        assert "bbox 100 200 300 250" in hocr

    def test_page_bbox(self):
        hocr = generate_hocr([], page_width=2550, page_height=3300)
        assert "bbox 0 0 2550 3300" in hocr

    def test_uzbek_text_escaped(self):
        results = [
            OCRResult(text="O'zbekiston", confidence=0.92, bbox=(10, 10, 200, 50)),
        ]
        hocr = generate_hocr(results, page_width=2550, page_height=3300)
        assert "O&#x27;zbekiston" in hocr or "O'zbekiston" in hocr

    def test_html_special_chars_escaped(self):
        results = [
            OCRResult(text="<test>&", confidence=0.90, bbox=(10, 10, 100, 50)),
        ]
        hocr = generate_hocr(results, page_width=2550, page_height=3300)
        assert "&lt;test&gt;&amp;" in hocr

    def test_empty_results(self):
        hocr = generate_hocr([], page_width=2550, page_height=3300)
        assert "ocr_page" in hocr
        assert 'class="ocrx_word"' not in hocr

    def test_pipeline_version_in_meta(self):
        hocr = generate_hocr([], page_width=100, page_height=100)
        assert "Uzbek-OCR-Pipeline v2.0" in hocr
