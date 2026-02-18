"""Tests for the configuration module."""

import os

from src.config import (
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    DICT_OVERLAP_THRESHOLD,
    DICT_PATH,
    IMAGE_DPI,
    PDF_DPI,
    USE_SPACE_CHAR,
    get_paddleocr_rec_config,
    load_character_set,
)


class TestConfig:
    """Tests for pipeline configuration constants and functions."""

    def test_dpi_constants(self):
        assert IMAGE_DPI == 300
        assert PDF_DPI == 72

    def test_confidence_thresholds(self):
        assert CONFIDENCE_HIGH == 0.90
        assert CONFIDENCE_LOW == 0.40
        assert CONFIDENCE_HIGH > CONFIDENCE_LOW

    def test_dict_overlap_threshold(self):
        assert DICT_OVERLAP_THRESHOLD == 0.80

    def test_use_space_char(self):
        assert USE_SPACE_CHAR is True

    def test_dict_path_exists(self):
        assert os.path.exists(DICT_PATH), f"Dictionary file not found: {DICT_PATH}"

    def test_load_character_set(self):
        from src.config import _CHAR_SET
        # Reset cached set
        import src.config
        src.config._CHAR_SET = None

        chars = load_character_set()
        assert isinstance(chars, set)
        assert len(chars) > 0

    def test_character_set_contains_uzbek_cyrillic(self):
        import src.config
        src.config._CHAR_SET = None
        chars = load_character_set()
        for ch in ["Қ", "қ", "Ғ", "ғ", "Ҳ", "ҳ", "Ў", "ў"]:
            assert ch in chars, f"Missing Uzbek Cyrillic char: {ch}"

    def test_character_set_contains_russian(self):
        import src.config
        src.config._CHAR_SET = None
        chars = load_character_set()
        for ch in ["А", "Б", "В", "а", "б", "в", "Я", "я"]:
            assert ch in chars, f"Missing Russian char: {ch}"

    def test_character_set_contains_latin(self):
        import src.config
        src.config._CHAR_SET = None
        chars = load_character_set()
        for ch in ["A", "B", "Z", "a", "b", "z"]:
            assert ch in chars, f"Missing Latin char: {ch}"

    def test_character_set_contains_digits(self):
        import src.config
        src.config._CHAR_SET = None
        chars = load_character_set()
        for ch in "0123456789":
            assert ch in chars, f"Missing digit: {ch}"

    def test_character_set_contains_punctuation(self):
        import src.config
        src.config._CHAR_SET = None
        chars = load_character_set()
        for ch in [".", ",", ":", ";", "!", "?", "%", "№", "(", ")", "-"]:
            assert ch in chars, f"Missing punctuation: {ch}"

    def test_character_set_contains_apostrophe(self):
        """The apostrophe is critical for Uzbek Latin (O', G')."""
        import src.config
        src.config._CHAR_SET = None
        chars = load_character_set()
        assert "'" in chars, "Missing apostrophe for Uzbek Latin digraphs"

    def test_paddleocr_rec_config(self):
        config = get_paddleocr_rec_config()
        assert isinstance(config, dict)
        assert config["use_space_char"] is True
        assert "rec_char_dict_path" in config
        assert config["rec_char_dict_path"].endswith("uz_ru_en_dict.txt")
