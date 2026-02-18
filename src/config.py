"""Pipeline configuration and constants for the Uzbek OCR Pipeline."""

import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Dictionary path
DICT_PATH = PROJECT_ROOT / "config" / "uz_ru_en_dict.txt"

# DPI settings for coordinate transformation
IMAGE_DPI = 300
PDF_DPI = 72

# Cascade confidence thresholds
CONFIDENCE_HIGH = 0.90   # Stage B: Accept if above this
CONFIDENCE_LOW = 0.40    # Stage D: Flag for human review if below this

# Dictionary overlap threshold for digital PDF gatekeeper
DICT_OVERLAP_THRESHOLD = 0.80

# Use space character in PaddleOCR
USE_SPACE_CHAR = True

# Supported character set (loaded from dict file)
_CHAR_SET = None


def load_character_set() -> set:
    """Load the custom character set from uz_ru_en_dict.txt.

    Returns:
        A set of characters supported by the OCR pipeline.
    """
    global _CHAR_SET
    if _CHAR_SET is not None:
        return _CHAR_SET

    chars = set()
    dict_path = str(DICT_PATH)
    if os.path.exists(dict_path):
        with open(dict_path, "r", encoding="utf-8") as f:
            for line in f:
                char = line.rstrip("\n")
                if char:
                    chars.add(char)
    _CHAR_SET = chars
    return _CHAR_SET


def get_paddleocr_rec_config() -> dict:
    """Return the PaddleOCR recognition config with Uzbek dictionary.

    Returns:
        A dict of configuration keys for PaddleOCR recognition.
    """
    return {
        "rec_char_dict_path": str(DICT_PATH),
        "use_space_char": USE_SPACE_CHAR,
        "rec_model_dir": None,  # Set to fine-tuned model path when available
        "rec_algorithm": "SVTR_LCNet",
    }
