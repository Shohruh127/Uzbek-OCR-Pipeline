# Uzbek-OCR-Pipeline

Sovereign-Grade OCR Pipeline (v2.0) for government contracts — handles Uzbek (Cyrillic/Latin), Russian, and English with legally defensible accuracy and zero data leakage.

## Overview

A self-hosted, air-gapped OCR system designed for government document processing (e.g., xarid.uzex.uz) with the following mandates:

- **Sovereignty**: All processing on air-gapped infrastructure. No third-party APIs.
- **Accuracy**: Handles Uzbek nuances (Қ, Ғ, Ҳ, O') with <1% Character Error Rate.
- **Legal Defensibility**: Traceable, reproducible, and verifiable via audit logs.

## Architecture

```
Input PDF/Image
      │
      ▼
┌─────────────┐
│  Gatekeeper  │──► Digital text? Dict overlap > 80%? → Skip OCR
└──────┬──────┘
       │ (Scanned)
       ▼
┌──────────────────────────────────────────────────┐
│              Cascade Pipeline                     │
│                                                   │
│  Stage A: PaddleOCR (Fine-tuned, uz_ru_en_dict)  │
│      │                                            │
│  Stage B: Confidence check                        │
│      ├── Conf ≥ 90% & No Tables → ACCEPT         │
│      ├── Conf < 40% → Stage D                    │
│      └── Otherwise → Stage C                     │
│                                                   │
│  Stage C: Surya Layout Analysis + Re-OCR cells   │
│                                                   │
│  Stage D: Flag for Human Review                   │
└──────────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│ HOCR + PDF/A │──► Searchable PDF via OCRmyPDF
└─────────────┘
```

## Project Structure

```
├── Dockerfile              # Air-gapped build (vendor/ based, --network=none)
├── MODEL_RELEASE.md        # Two-Person Rule release template
├── requirements.txt        # Python dependencies
├── configs/
│   ├── uz_ru_en_dict.txt       # Custom character dictionary (Uzbek/Russian/English)
│   ├── rec_ppocr_v4_uz.yml     # PaddleOCR fine-tuning config
│   └── scorecard_schema.json   # Model evaluation scorecard schema
├── src/
│   ├── pipeline/
│   │   ├── gatekeeper.py       # Digital text layer detection & skip logic
│   │   ├── cascade.py          # 4-stage fail-fast OCR pipeline
│   │   ├── hocr_generator.py   # HOCR 1.0 output generation
│   │   └── pdf_generator.py    # Searchable PDF/A via OCRmyPDF
│   └── utils/
│       ├── coordinates.py      # Pixel ↔ PDF point coordinate transforms
│       └── dictionary.py       # Character dictionary loading & overlap
├── scripts/
│   └── evaluate_model.py       # Model evaluation against Golden Test Set
├── golden_test_set/            # 100 fixed evaluation pages
├── tests/                      # Unit tests
└── vendor/                     # Vendored Python wheels for air-gap
```

## Quick Start

### Air-Gapped Build

```bash
# Download wheels to vendor/ (on a connected machine)
pip download -r requirements.txt -d vendor/

# Build with network isolation
docker build --network=none -t uzbek-ocr:2.0 .

# Run
docker run --network=none -v ./data:/app/data uzbek-ocr:2.0
```

### Development

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

### Model Evaluation

```bash
python scripts/evaluate_model.py \
    --model_dir ./output/rec_ppocr_v4_uz \
    --test_dir ./golden_test_set \
    --output scorecard.json
```

## Governance: Two-Person Rule

No model is promoted to production without cryptographic signatures from both a **Builder** and an **Auditor**. See [MODEL_RELEASE.md](MODEL_RELEASE.md) for the full workflow.

## Character Dictionary

The custom dictionary (`configs/uz_ru_en_dict.txt`) supports:

| Category | Characters |
|---|---|
| Digits | 0–9 |
| Latin | A–Z, a–z |
| Russian Cyrillic | А–Я, а–я |
| Uzbek Cyrillic | Қ, қ, Ғ, ғ, Ҳ, ҳ, Ў, ў |
| Uzbek Latin | O', o', G', g' (via apostrophe) |
| Punctuation | . , : ; ! ? % № ( ) - ' " / |

## Technical Stack

| Component | Technology | Role |
|---|---|---|
| Text Recognition | PaddleOCR v4 (Fine-Tuned) | Single Source of Truth |
| Layout Analysis | Surya | Table Structure Detection |
| PDF Generation | OCRmyPDF + HOCR | PDF/A Archival |
| Human Review | Label Studio | Correction UI |
| Container | Docker | Air-Gapped Runtime |
