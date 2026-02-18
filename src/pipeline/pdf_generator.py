"""Searchable PDF/A generation using OCRmyPDF.

Wraps OCRmyPDF to produce archival-quality searchable PDFs
from scanned documents using HOCR text layers generated
by the Uzbek OCR Pipeline.
"""

import logging
import subprocess

logger = logging.getLogger(__name__)


def generate_searchable_pdf(input_pdf, output_pdf, hocr_file=None):
    """Generate a searchable PDF/A from a scanned PDF.

    Uses OCRmyPDF with the HOCR renderer for text layer injection.

    Args:
        input_pdf: Path to the input scanned PDF.
        output_pdf: Path for the output searchable PDF/A.
        hocr_file: Optional path to pre-generated HOCR file.
                   If provided, uses --hocr-file flag.

    Returns:
        True if successful, False otherwise.
    """
    cmd = [
        "ocrmypdf",
        "--pdf-renderer",
        "hocr",
        "--output-type",
        "pdfa",
    ]

    if hocr_file:
        cmd.extend(["--hocr-file", hocr_file])

    cmd.extend([input_pdf, output_pdf])

    logger.info("Running OCRmyPDF: %s", " ".join(cmd))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info("Searchable PDF generated: %s", output_pdf)
        return True
    except subprocess.CalledProcessError as e:
        logger.error("OCRmyPDF failed: %s\n%s", e.returncode, e.stderr)
        return False
    except FileNotFoundError:
        logger.error("ocrmypdf command not found. Is it installed?")
        return False
