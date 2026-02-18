"""Tests for the model evaluation script."""

import pytest

from scripts.evaluate_model import compute_cer


class TestComputeCER:
    """Tests for Character Error Rate computation."""

    def test_identical_strings(self):
        assert compute_cer("hello", "hello") == pytest.approx(0.0)

    def test_completely_different(self):
        # "abc" vs "xyz" - 3 substitutions / 3 chars = 1.0
        assert compute_cer("xyz", "abc") == pytest.approx(1.0)

    def test_empty_both(self):
        assert compute_cer("", "") == pytest.approx(0.0)

    def test_empty_prediction(self):
        # All chars are deletions: 5 / 5 = 1.0
        assert compute_cer("", "hello") == pytest.approx(1.0)

    def test_empty_ground_truth(self):
        assert compute_cer("hello", "") == pytest.approx(1.0)

    def test_one_substitution(self):
        # "hallo" vs "hello" - 1 substitution / 5 chars = 0.2
        assert compute_cer("hallo", "hello") == pytest.approx(0.2)

    def test_uzbek_characters(self):
        """CER should work correctly with Uzbek Cyrillic characters."""
        assert compute_cer("Қарор", "Қарор") == pytest.approx(0.0)
        # One character wrong
        assert compute_cer("Карор", "Қарор") == pytest.approx(0.2)

    def test_insertion(self):
        # "helllo" vs "hello" - 1 insertion / 5 chars = 0.2
        assert compute_cer("helllo", "hello") == pytest.approx(0.2)

    def test_deletion(self):
        # "helo" vs "hello" - 1 deletion / 5 chars = 0.2
        assert compute_cer("helo", "hello") == pytest.approx(0.2)
