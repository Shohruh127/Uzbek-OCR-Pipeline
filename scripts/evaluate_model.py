#!/usr/bin/env python3
"""Model evaluation script for the Uzbek OCR Pipeline.

Evaluates a trained recognition model against the Golden Test Set
and produces a scorecard.json file.

Usage:
    python scripts/evaluate_model.py \
        --model_dir ./output/rec_ppocr_v4_uz \
        --test_dir ./golden_test_set \
        --output scorecard.json
"""

import argparse
import hashlib
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def compute_cer(predicted, ground_truth):
    """Compute Character Error Rate using edit distance.

    Args:
        predicted: Predicted text string.
        ground_truth: Ground truth text string.

    Returns:
        Float CER value (0.0 = perfect, 1.0 = completely wrong).
    """
    if not ground_truth:
        return 0.0 if not predicted else 1.0

    # Dynamic programming edit distance
    m, n = len(predicted), len(ground_truth)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if predicted[i - 1] == ground_truth[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    return dp[m][n] / n


def compute_file_sha256(filepath):
    """Compute SHA256 hash of a file.

    Args:
        filepath: Path to the file.

    Returns:
        Hex digest string.
    """
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_git_commit_hash():
    """Get the current git commit hash.

    Returns:
        Git commit hash string or 'unknown'.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def generate_scorecard(
    model_dir, test_dir, evaluator="automated", model_name="PP-OCRv4_rec_uz"
):
    """Generate an evaluation scorecard.

    Args:
        model_dir: Path to the trained model directory.
        test_dir: Path to the golden test set directory.
        evaluator: Name of the person running evaluation.
        model_name: Name of the model being evaluated.

    Returns:
        Dictionary containing the scorecard data.
    """
    scorecard = {
        "model_name": model_name,
        "model_version": "",
        "evaluation_date": datetime.now(timezone.utc).isoformat(),
        "git_commit_hash": get_git_commit_hash(),
        "model_sha256": "",
        "evaluator": evaluator,
        "golden_test_set_version": "1.0",
        "metrics": {
            "overall_cer": None,
            "overall_accuracy": None,
            "uzbek_cyrillic_cer": None,
            "uzbek_latin_cer": None,
            "russian_cer": None,
            "english_cer": None,
            "stamp_detection_iou": None,
            "table_detection_iou": None,
        },
        "category_breakdown": {
            "simple_text": {"count": 40, "cer": None, "accuracy": None},
            "tables": {"count": 30, "cer": None, "accuracy": None},
            "stamps_signatures": {"count": 20, "detection_iou": None},
            "poor_scans": {"count": 10, "cer": None, "accuracy": None},
        },
        "pass_criteria": {
            "cer_threshold": 0.01,
            "stamp_iou_threshold": 0.95,
            "all_passed": False,
        },
        "builder_signature": "",
        "auditor_signature": "",
    }

    # Check for model files to compute SHA256
    model_file = os.path.join(model_dir, "best_accuracy.pdparams")
    if os.path.exists(model_file):
        scorecard["model_sha256"] = compute_file_sha256(model_file)

    return scorecard


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate OCR model against Golden Test Set"
    )
    parser.add_argument(
        "--model_dir",
        required=True,
        help="Path to trained model directory",
    )
    parser.add_argument(
        "--test_dir",
        default="./golden_test_set",
        help="Path to golden test set directory",
    )
    parser.add_argument(
        "--output",
        default="scorecard.json",
        help="Output scorecard file path",
    )
    parser.add_argument(
        "--evaluator",
        default="automated",
        help="Name of the evaluator",
    )

    args = parser.parse_args()

    if not os.path.isdir(args.model_dir):
        logger.error("Model directory not found: %s", args.model_dir)
        sys.exit(1)

    scorecard = generate_scorecard(
        model_dir=args.model_dir,
        test_dir=args.test_dir,
        evaluator=args.evaluator,
    )

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(scorecard, f, indent=2, ensure_ascii=False)

    logger.info("Scorecard written to %s", args.output)


if __name__ == "__main__":
    main()
