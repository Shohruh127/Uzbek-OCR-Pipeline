"""Tests for the cascade pipeline logic."""

import pytest

from src.pipeline.cascade import (
    CONFIDENCE_ACCEPT,
    CONFIDENCE_FALLBACK,
    CascadeDecision,
    CascadeStage,
    OCRResult,
    PageResult,
    run_stage_b,
    run_stage_d,
)


class TestOCRResult:
    """Tests for OCRResult dataclass."""

    def test_creation(self):
        result = OCRResult(text="Hello", confidence=0.95, bbox=(10, 20, 100, 50))
        assert result.text == "Hello"
        assert result.confidence == 0.95
        assert result.bbox == (10, 20, 100, 50)

    def test_default_bbox(self):
        result = OCRResult(text="Test", confidence=0.8)
        assert result.bbox == ()


class TestPageResult:
    """Tests for PageResult dataclass."""

    def test_compute_avg_confidence(self):
        results = [
            OCRResult(text="A", confidence=0.9),
            OCRResult(text="B", confidence=0.8),
            OCRResult(text="C", confidence=0.7),
        ]
        page = PageResult(page_number=1, results=results)
        page.compute_avg_confidence()
        assert page.avg_confidence == pytest.approx(0.8)

    def test_compute_avg_confidence_empty(self):
        page = PageResult(page_number=1, results=[])
        page.compute_avg_confidence()
        assert page.avg_confidence == 0.0


class TestStageB:
    """Tests for Stage B validation logic."""

    def test_accept_high_confidence_no_tables(self):
        results = [
            OCRResult(text="A", confidence=0.95),
            OCRResult(text="B", confidence=0.92),
        ]
        page = PageResult(page_number=1, results=results, tables_detected=False)
        decision = run_stage_b(page)
        assert decision == CascadeDecision.ACCEPT
        assert page.stage == CascadeStage.STAGE_B

    def test_refine_when_tables_detected(self):
        results = [
            OCRResult(text="A", confidence=0.95),
            OCRResult(text="B", confidence=0.92),
        ]
        page = PageResult(page_number=1, results=results, tables_detected=True)
        decision = run_stage_b(page)
        assert decision == CascadeDecision.REFINE
        assert page.stage == CascadeStage.STAGE_C

    def test_refine_low_confidence(self):
        results = [
            OCRResult(text="A", confidence=0.70),
            OCRResult(text="B", confidence=0.60),
        ]
        page = PageResult(page_number=1, results=results, tables_detected=False)
        decision = run_stage_b(page)
        assert decision == CascadeDecision.REFINE
        assert page.stage == CascadeStage.STAGE_C

    def test_human_review_very_low_confidence(self):
        results = [
            OCRResult(text="A", confidence=0.20),
            OCRResult(text="B", confidence=0.30),
        ]
        page = PageResult(page_number=1, results=results, tables_detected=False)
        decision = run_stage_b(page)
        assert decision == CascadeDecision.HUMAN_REVIEW
        assert page.stage == CascadeStage.STAGE_D

    def test_boundary_accept_threshold(self):
        """Confidence exactly at CONFIDENCE_ACCEPT should accept."""
        results = [OCRResult(text="A", confidence=CONFIDENCE_ACCEPT)]
        page = PageResult(page_number=1, results=results, tables_detected=False)
        decision = run_stage_b(page)
        assert decision == CascadeDecision.ACCEPT

    def test_boundary_fallback_threshold(self):
        """Confidence exactly at CONFIDENCE_FALLBACK should refine, not review."""
        results = [OCRResult(text="A", confidence=CONFIDENCE_FALLBACK)]
        page = PageResult(page_number=1, results=results, tables_detected=False)
        decision = run_stage_b(page)
        assert decision == CascadeDecision.REFINE


class TestStageD:
    """Tests for Stage D human review logic."""

    def test_flags_for_review(self):
        page = PageResult(page_number=3, avg_confidence=0.25)
        result = run_stage_d(page)
        assert result.stage == CascadeStage.STAGE_D
        assert result.decision == CascadeDecision.HUMAN_REVIEW


class TestConfidenceThresholds:
    """Tests for confidence threshold values."""

    def test_accept_threshold(self):
        assert CONFIDENCE_ACCEPT == 0.90

    def test_fallback_threshold(self):
        assert CONFIDENCE_FALLBACK == 0.40
