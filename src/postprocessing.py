"""Post-processing utilities for raw OCR output."""

import re


# Common OCR substitution errors for Latin-script Uzbek.
# Patterns are designed to avoid replacing legitimate digits:
#   - '0' is replaced only when it is NOT surrounded by digits on both sides.
#   - '|' is always replaced since it is not a valid character in Uzbek Latin text.
#   - '1' is replaced only when adjacent to at least one letter.
_WORD_SUBSTITUTIONS = [
    (re.compile(r"(?<!\d)0(?!\d)"), "O"),
    (re.compile(r"\|"), "I"),
    (re.compile(r"(?<=[A-Za-z])1|1(?=[A-Za-z])"), "l"),
]


def fix_common_errors(text: str) -> str:
    """Replace common OCR misrecognitions in Uzbek Latin-script text.

    Substitutions avoid altering legitimate numbers (e.g. '2024' is preserved).
    """
    for pattern, replacement in _WORD_SUBSTITUTIONS:
        text = pattern.sub(replacement, text)
    return text


def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespace characters into a single space."""
    return re.sub(r"\s+", " ", text).strip()


def remove_non_uzbek(text: str) -> str:
    """Remove characters that are not part of the Uzbek Latin alphabet or punctuation."""
    # Uzbek Latin alphabet + apostrophe (for Oʻ / Gʻ) + standard punctuation
    allowed = r"[^A-Za-zÀ-öø-ÿŌōŪūʼʻ\s.,!?;:'\"\-]"
    return re.sub(allowed, "", text)


def postprocess(text: str) -> str:
    """Full post-processing pipeline: fix errors → remove noise → normalize whitespace."""
    text = fix_common_errors(text)
    text = remove_non_uzbek(text)
    text = normalize_whitespace(text)
    return text
