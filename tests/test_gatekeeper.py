"""Tests for the gatekeeper module."""

from unittest.mock import patch

from src.gatekeeper import classify_document, compute_dict_overlap


class TestComputeDictOverlap:
    """Tests for dictionary overlap computation."""

    def test_empty_text(self):
        assert compute_dict_overlap("") == 0.0

    def test_whitespace_only(self):
        assert compute_dict_overlap("   ") == 0.0

    def test_all_known_chars(self):
        # All standard latin letters should be in our dict
        overlap = compute_dict_overlap("Hello World")
        assert overlap > 0.8

    def test_uzbek_chars(self):
        overlap = compute_dict_overlap("Қарор")
        assert overlap > 0.8

    def test_newlines_ignored(self):
        overlap = compute_dict_overlap("A\n\nB\n")
        assert overlap == 1.0


class TestClassifyDocument:
    """Tests for document classification."""

    def test_nonexistent_file(self):
        classification, text = classify_document("/nonexistent/file.pdf")
        assert classification == "scan"
        assert text == ""

    def test_non_pdf_extension(self):
        # Non-PDF should work (just return scan for non-existent)
        classification, text = classify_document("/nonexistent/file.png")
        assert classification == "scan"

    @patch("src.gatekeeper.extract_text_from_pdf")
    def test_empty_text_classified_as_scan(self, mock_extract):
        mock_extract.return_value = ""
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 fake")
            tmp_path = f.name
        try:
            classification, text = classify_document(tmp_path)
            assert classification == "scan"
        finally:
            os.unlink(tmp_path)

    @patch("src.gatekeeper.extract_text_from_pdf")
    @patch("src.gatekeeper.compute_dict_overlap")
    def test_high_overlap_classified_as_digital(self, mock_overlap, mock_extract):
        mock_extract.return_value = "Some text content"
        mock_overlap.return_value = 0.95
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 fake")
            tmp_path = f.name
        try:
            classification, text = classify_document(tmp_path)
            assert classification == "digital"
            assert text == "Some text content"
        finally:
            os.unlink(tmp_path)

    @patch("src.gatekeeper.extract_text_from_pdf")
    @patch("src.gatekeeper.compute_dict_overlap")
    def test_low_overlap_classified_as_scan(self, mock_overlap, mock_extract):
        mock_extract.return_value = "Garbled text"
        mock_overlap.return_value = 0.30
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 fake")
            tmp_path = f.name
        try:
            classification, text = classify_document(tmp_path)
            assert classification == "scan"
        finally:
            os.unlink(tmp_path)
