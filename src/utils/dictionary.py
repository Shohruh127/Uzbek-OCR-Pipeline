"""Dictionary utilities for the Uzbek OCR Pipeline.

Provides functions for loading the custom character dictionary
and computing dictionary overlap for the Gatekeeper module.
"""

import os

# Default dictionary path relative to project root
DEFAULT_DICT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "configs", "uz_ru_en_dict.txt"
)


def load_dictionary(dict_path=None):
    """Load the character dictionary from file.

    Args:
        dict_path: Path to dictionary file. Uses default if None.

    Returns:
        Set of characters in the dictionary.
    """
    if dict_path is None:
        dict_path = DEFAULT_DICT_PATH

    chars = set()
    with open(dict_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith("#"):
                chars.add(line)
    return chars


def compute_dictionary_overlap(text, dictionary_chars):
    """Compute the fraction of text characters covered by the dictionary.

    Used by the Gatekeeper to decide whether digital PDF text is
    sufficiently recognizable to skip OCR.

    Args:
        text: The extracted text string.
        dictionary_chars: Set of valid characters from the dictionary.

    Returns:
        Float between 0.0 and 1.0 representing the overlap ratio.
        Returns 0.0 if text is empty.
    """
    if not text:
        return 0.0

    # Only count non-whitespace characters for overlap
    text_chars = [c for c in text if not c.isspace()]
    if not text_chars:
        return 0.0

    matched = sum(1 for c in text_chars if c in dictionary_chars)
    return matched / len(text_chars)
