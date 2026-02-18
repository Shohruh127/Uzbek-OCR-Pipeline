"""Tests for dictionary utilities."""

import os
import tempfile

import pytest

from src.utils.dictionary import compute_dictionary_overlap, load_dictionary


class TestLoadDictionary:
    """Tests for load_dictionary function."""

    def test_load_default_dictionary(self):
        """The default dictionary file should load successfully."""
        dict_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "configs",
            "uz_ru_en_dict.txt",
        )
        chars = load_dictionary(dict_path)
        assert len(chars) > 0

    def test_contains_digits(self):
        dict_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "configs",
            "uz_ru_en_dict.txt",
        )
        chars = load_dictionary(dict_path)
        for d in "0123456789":
            assert d in chars

    def test_contains_uzbek_cyrillic(self):
        """Dictionary must contain Uzbek-specific Cyrillic characters."""
        dict_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "configs",
            "uz_ru_en_dict.txt",
        )
        chars = load_dictionary(dict_path)
        uzbek_chars = ["Қ", "қ", "Ғ", "ғ", "Ҳ", "ҳ", "Ў", "ў"]
        for c in uzbek_chars:
            assert c in chars, f"Missing Uzbek character: {c}"

    def test_contains_russian_cyrillic(self):
        """Dictionary must contain Russian Cyrillic characters."""
        dict_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "configs",
            "uz_ru_en_dict.txt",
        )
        chars = load_dictionary(dict_path)
        assert "А" in chars
        assert "Я" in chars
        assert "а" in chars
        assert "я" in chars

    def test_contains_latin(self):
        dict_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "configs",
            "uz_ru_en_dict.txt",
        )
        chars = load_dictionary(dict_path)
        assert "A" in chars
        assert "z" in chars

    def test_contains_punctuation(self):
        dict_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "configs",
            "uz_ru_en_dict.txt",
        )
        chars = load_dictionary(dict_path)
        assert "." in chars
        assert "," in chars
        assert "№" in chars

    def test_contains_apostrophe(self):
        """Dictionary must contain apostrophe for O' digraphs."""
        dict_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "configs",
            "uz_ru_en_dict.txt",
        )
        chars = load_dictionary(dict_path)
        assert "'" in chars

    def test_skips_comments(self):
        """Comments starting with # should be skipped."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("# This is a comment\n")
            f.write("A\n")
            f.write("B\n")
            f.write("\n")
            f.write("# Another comment\n")
            f.write("C\n")

        try:
            chars = load_dictionary(f.name)
            assert chars == {"A", "B", "C"}
        finally:
            os.unlink(f.name)


class TestComputeDictionaryOverlap:
    """Tests for compute_dictionary_overlap function."""

    def test_full_overlap(self):
        chars = {"A", "B", "C"}
        assert compute_dictionary_overlap("ABC", chars) == pytest.approx(1.0)

    def test_no_overlap(self):
        chars = {"A", "B", "C"}
        assert compute_dictionary_overlap("XYZ", chars) == pytest.approx(0.0)

    def test_partial_overlap(self):
        chars = {"A", "B", "C"}
        assert compute_dictionary_overlap("ABXY", chars) == pytest.approx(0.5)

    def test_empty_text(self):
        chars = {"A", "B"}
        assert compute_dictionary_overlap("", chars) == pytest.approx(0.0)

    def test_whitespace_only(self):
        chars = {"A", "B"}
        assert compute_dictionary_overlap("   ", chars) == pytest.approx(0.0)

    def test_ignores_whitespace(self):
        chars = {"A", "B", "C"}
        assert compute_dictionary_overlap("A B C", chars) == pytest.approx(1.0)
