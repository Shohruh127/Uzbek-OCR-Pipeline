"""Tests for the cascade pipeline module."""

from src.cascade import (
    CascadeStage,
    OCRResult,
    PageResult,
    compute_avg_confidence,
    process_page,
    run_stage_a,
    run_stage_b,
)


class TestComputeAvgConfidence:
    """Tests for average confidence computation."""

    def test_empty_list(self):
        assert compute_avg_confidence([]) == 0.0

    def test_single_result(self):
        results = [OCRResult(text="hello", confidence=0.95, bbox=(0, 0, 100, 50))]
        assert compute_avg_confidence(results) == 0.95

    def test_multiple_results(self):
        results = [
            OCRResult(text="a", confidence=0.80, bbox=(0, 0, 50, 25)),
            OCRResult(text="b", confidence=1.00, bbox=(50, 0, 100, 25)),
        ]
        assert compute_avg_confidence(results) == 0.90

    def test_all_zero(self):
        results = [
            OCRResult(text="x", confidence=0.0, bbox=(0, 0, 10, 10)),
        ]
        assert compute_avg_confidence(results) == 0.0


class TestRunStageB:
    """Tests for Stage B (Validation) logic."""

    def test_accept_high_confidence_no_tables(self):
        results = [
            OCRResult(text="text", confidence=0.95, bbox=(0, 0, 100, 50)),
        ]
        stage = run_stage_b(results, tables_detected=False)
        assert stage == CascadeStage.STAGE_B

    def test_reject_with_tables(self):
        results = [
            OCRResult(text="text", confidence=0.95, bbox=(0, 0, 100, 50)),
        ]
        stage = run_stage_b(results, tables_detected=True)
        assert stage == CascadeStage.STAGE_C

    def test_low_confidence_routes_to_human_review(self):
        results = [
            OCRResult(text="?", confidence=0.20, bbox=(0, 0, 100, 50)),
        ]
        stage = run_stage_b(results, tables_detected=False)
        assert stage == CascadeStage.STAGE_D

    def test_medium_confidence_routes_to_structure(self):
        results = [
            OCRResult(text="text", confidence=0.70, bbox=(0, 0, 100, 50)),
        ]
        stage = run_stage_b(results, tables_detected=False)
        assert stage == CascadeStage.STAGE_C

    def test_empty_results_routes_to_human_review(self):
        stage = run_stage_b([], tables_detected=False)
        assert stage == CascadeStage.STAGE_D


class TestRunStageA:
    """Tests for Stage A (Primary OCR) without an actual engine."""

    def test_no_engine_returns_empty(self):
        results = run_stage_a("dummy.png", ocr_engine=None)
        assert results == []


class TestProcessPage:
    """Tests for the full cascade page processing."""

    def test_no_engine_produces_human_review(self):
        result = process_page("dummy.png", page_number=1)
        assert isinstance(result, PageResult)
        assert result.stage == CascadeStage.STAGE_D
        assert result.needs_human_review is True
        assert result.avg_confidence == 0.0

    def test_page_number_preserved(self):
        result = process_page("dummy.png", page_number=42)
        assert result.page_number == 42
