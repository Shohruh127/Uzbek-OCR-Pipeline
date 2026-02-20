"""OCR module: extract Uzbek text from preprocessed images using Tesseract."""

import numpy as np
import pytesseract
from PIL import Image

# Tesseract language code for Uzbek (Latin script).
# Ensure the 'uzb' language data is installed:
#   sudo apt-get install tesseract-ocr-uzb
UZBEK_LANG = "uzb"


def extract_text(image: np.ndarray, lang: str = UZBEK_LANG) -> str:
    """Run Tesseract OCR on a preprocessed image and return the extracted text.

    Args:
        image: A grayscale or binary NumPy array (uint8).
        lang: Tesseract language identifier (default: 'uzb').

    Returns:
        Extracted text as a string.
    """
    pil_image = Image.fromarray(image)
    text = pytesseract.image_to_string(pil_image, lang=lang)
    return text.strip()


def extract_text_with_confidence(image: np.ndarray,
                                 lang: str = UZBEK_LANG) -> list[dict]:
    """Run Tesseract and return per-word text with confidence scores.

    Args:
        image: A grayscale or binary NumPy array (uint8).
        lang: Tesseract language identifier.

    Returns:
        List of dicts with keys: 'text', 'conf', 'left', 'top', 'width', 'height'.
        Note: Tesseract may return a confidence of -1 for unrecognised tokens;
        consumers should treat conf == -1 as "no confidence information available".
    """
    pil_image = Image.fromarray(image)
    data = pytesseract.image_to_data(pil_image, lang=lang,
                                     output_type=pytesseract.Output.DICT)
    results = []
    for i, word in enumerate(data["text"]):
        if word.strip():
            results.append({
                "text": word,
                "conf": int(data["conf"][i]),
                "left": data["left"][i],
                "top": data["top"][i],
                "width": data["width"][i],
                "height": data["height"][i],
            })
    return results
