"""Output generation module for searchable PDF/A creation.

Implements Phase 4, Section 6.2:
- Generates searchable PDF/A files using OCRmyPDF with HOCR renderer.
- Writes HOCR intermediate files for OCRmyPDF consumption.
"""

import logging
import os
import subprocess
import tempfile
from typing import List, Optional

from src.cascade import OCRResult
from src.hocr import generate_hocr

logger = logging.getLogger(__name__)


def write_hocr_file(
    results: List[OCRResult],
    page_width: int,
    page_height: int,
    output_path: str,
    page_number: int = 1,
    image_filename: str = "page.png",
) -> str:
    """Generate and write an HOCR file to disk.

    Args:
        results: OCR results for the page.
        page_width: Page width in pixels.
        page_height: Page height in pixels.
        output_path: Path where the HOCR file should be written.
        page_number: Page number (1-indexed).
        image_filename: The source image filename.

    Returns:
        The path to the written HOCR file.
    """
    hocr_content = generate_hocr(
        results, page_width, page_height, page_number, image_filename
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(hocr_content)
    logger.info("Wrote HOCR file: %s", output_path)
    return output_path


def generate_searchable_pdf(
    input_pdf: str,
    output_pdf: str,
    hocr_file: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
) -> bool:
    """Generate a searchable PDF/A from an input PDF using OCRmyPDF.

    Command:
        ocrmypdf --pdf-renderer hocr --output-type pdfa
                 --sidecar <hocr_file> input.pdf output.pdf

    Args:
        input_pdf: Path to the input PDF (scanned).
        output_pdf: Path for the output searchable PDF/A.
        hocr_file: Optional path to a pre-generated HOCR file.
        extra_args: Optional additional command-line arguments.

    Returns:
        True if successful, False otherwise.
    """
    cmd = [
        "ocrmypdf",
        "--pdf-renderer", "hocr",
        "--output-type", "pdfa",
        "--force-ocr",
    ]

    if extra_args:
        cmd.extend(extra_args)

    cmd.extend([input_pdf, output_pdf])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 0:
            logger.info("Searchable PDF generated: %s", output_pdf)
            return True
        else:
            logger.error("OCRmyPDF failed (code %d): %s", result.returncode, result.stderr)
            return False
    except FileNotFoundError:
        logger.error("ocrmypdf not found; install with: pip install ocrmypdf")
        return False
    except subprocess.TimeoutExpired:
        logger.error("OCRmyPDF timed out after 300 seconds")
        return False
