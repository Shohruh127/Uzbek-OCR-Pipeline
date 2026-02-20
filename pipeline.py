"""Entry point for the Uzbek OCR Pipeline."""

import argparse
import sys

from src.preprocessing import preprocess
from src.ocr import extract_text
from src.postprocessing import postprocess


def run_pipeline(image_path: str, lang: str = "uzb") -> str:
    """Run the full OCR pipeline on an image file.

    Args:
        image_path: Path to the input image.
        lang: Tesseract language code (default: 'uzb').

    Returns:
        Extracted and post-processed text.
    """
    preprocessed = preprocess(image_path)
    raw_text = extract_text(preprocessed, lang=lang)
    return postprocess(raw_text)


def main():
    parser = argparse.ArgumentParser(
        description="Uzbek OCR Pipeline – extract text from an image."
    )
    parser.add_argument("image", help="Path to the input image file.")
    parser.add_argument(
        "--lang",
        default="uzb",
        help="Tesseract language code (default: uzb).",
    )
    args = parser.parse_args()

    try:
        result = run_pipeline(args.image, lang=args.lang)
        print(result)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
