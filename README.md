# Uzbek-OCR-Pipeline

Sovereign-Grade OCR Pipeline v2.0 for Uzbek (Cyrillic/Latin), Russian, and English documents.

## Overview

A self-hosted, air-gapped OCR system designed for government contracts that handles
Uzbek-specific characters (Қ, Ғ, Ҳ, O') with legally defensible accuracy and zero data leakage.

## Architecture

The pipeline implements a **Cascade (Fail-Fast)** architecture:

1. **Gatekeeper** — Classifies documents as digital (skip OCR) or scan (proceed with OCR)
   using PyMuPDF text extraction and dictionary overlap analysis.
2. **Stage A (Primary)** — Runs fine-tuned PaddleOCR recognition.
3. **Stage B (Validation)** — Accepts results if confidence > 90% and no tables detected.
4. **Stage C (Structure)** — Runs Surya layout analysis for tables; re-OCRs cell crops.
5. **Stage D (Fallback)** — Flags pages with confidence < 40% for human review.

## Project Structure

```
├── src/
│   ├── config.py       # Pipeline configuration and constants
│   ├── gatekeeper.py   # Document classification (digital vs scan)
│   ├── cascade.py      # Multi-stage OCR cascade pipeline
│   ├── coordinates.py  # Pixel-to-PDF coordinate transformation
│   ├── hocr.py         # HOCR 1.0 output generation
│   ├── output.py       # Searchable PDF/A generation via OCRmyPDF
│   └── pipeline.py     # Main pipeline orchestrator
├── config/
│   └── uz_ru_en_dict.txt   # Custom Uzbek/Russian/English character dictionary
├── tests/              # Unit tests for all modules
├── docs/
│   ├── MODEL_RELEASE.md    # Two-person rule governance template
│   └── scorecard.json      # Model evaluation scorecard template
├── Dockerfile          # Air-gapped container (--network=none)
└── requirements.txt    # Pinned Python dependencies
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Process a document (programmatic usage)
python -c "from src.pipeline import process_document; print(process_document('input.pdf'))"
```

## Air-Gapped Deployment

```bash
# Build with network isolation
docker build --network=none -t uzbek-ocr .

# Run with network isolation
docker run --network=none uzbek-ocr
```

## Governance

All model promotions follow the **Two-Person Rule**: a Builder submits the model and
scorecard, an Auditor independently verifies results and signs `MODEL_RELEASE.md` with
their GPG key before CI/CD updates the production symlink.

## Character Set

The custom dictionary (`config/uz_ru_en_dict.txt`) covers:
- **Digits**: 0–9
- **Latin**: A–Z, a–z
- **Russian Cyrillic**: А–Я, а–я
- **Uzbek Cyrillic**: Қ, қ, Ғ, ғ, Ҳ, ҳ, Ў, ў
- **Uzbek Latin**: Apostrophe `'` for digraphs (O', G')
- **Punctuation**: `.,:;!?%№()-/"`
