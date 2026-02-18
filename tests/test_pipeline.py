"""Tests for the main pipeline orchestrator."""

from unittest.mock import patch

from src.pipeline import PipelineResult, process_document


class TestProcessDocument:
    """Tests for the full pipeline orchestrator."""

    def test_nonexistent_pdf_classified_as_scan(self):
        result = process_document("/nonexistent/file.pdf", output_dir="/tmp/test_out")
        assert isinstance(result, PipelineResult)
        assert result.classification == "scan"

    @patch("src.pipeline.classify_document")
    def test_digital_pdf_skips_ocr(self, mock_classify):
        mock_classify.return_value = ("digital", "Extracted text here")
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 fake")
            tmp_path = f.name
        try:
            result = process_document(tmp_path, output_dir="/tmp/test_out")
            assert result.classification == "digital"
            assert result.digital_text == "Extracted text here"
            assert len(result.pages) == 0
        finally:
            os.unlink(tmp_path)

    def test_image_file_runs_cascade(self):
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"fake image data")
            tmp_path = f.name
        try:
            result = process_document(tmp_path, output_dir="/tmp/test_out")
            assert result.classification == "scan"
            assert len(result.pages) == 1
            assert result.pages[0].needs_human_review is True  # No engine
        finally:
            os.unlink(tmp_path)

    def test_audit_log_populated(self):
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"fake image data")
            tmp_path = f.name
        try:
            result = process_document(tmp_path, output_dir="/tmp/test_out")
            assert len(result.audit_log) > 0
            assert any(e["action"] == "gatekeeper" for e in result.audit_log)
        finally:
            os.unlink(tmp_path)
