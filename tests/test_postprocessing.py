"""Tests for the postprocessing module (no external dependencies required)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.postprocessing import fix_common_errors, normalize_whitespace, postprocess


def test_fix_common_errors_zero_to_O():
    assert fix_common_errors("0'zbekiston") == "O'zbekiston"


def test_fix_common_errors_pipe_to_I():
    assert fix_common_errors("|nson") == "Inson"


def test_normalize_whitespace_collapses_spaces():
    assert normalize_whitespace("salom   dunyo") == "salom dunyo"


def test_normalize_whitespace_strips_edges():
    assert normalize_whitespace("  salom  ") == "salom"


def test_postprocess_full_pipeline():
    result = postprocess("  0'zbek   |nson  ")
    assert "O'zbek" in result
    assert "Inson" in result
    assert "  " not in result
