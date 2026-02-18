# Golden Test Set

100 representative pages for model evaluation. This set **MUST NOT** change once established.

## Composition

- 40% Simple Text (Standard Contracts)
- 30% Tables (Financials, Schedules)
- 20% Stamps/Signatures (Official seals)
- 10% Poor Scans (Fax/Mobile photos)

## Success Metrics

- CER < 1%
- Stamp Detection IoU > 0.95

## Files

Place golden test set images and ground truth files here.

**Format:** `<image_file>\t<ground_truth_text>`

**Examples:**

| File | Ground Truth |
|---|---|
| `simple_001.png` | Ўзбекистон Республикаси Давлат харидлари |
| `table_001.png` | (structured table ground truth) |
| `stamp_001.png` | EXCLUSION_ZONE |
| `poor_001.png` | Шартнома рақами: 123/2024 |
