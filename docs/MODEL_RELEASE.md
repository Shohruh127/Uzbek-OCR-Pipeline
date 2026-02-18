# Model Release Document

## Model Information

| Field               | Value                          |
|---------------------|--------------------------------|
| Model Name          | PP-OCRv4_rec (Fine-Tuned)      |
| Model Version       | v1.0                           |
| Dictionary          | uz_ru_en_dict.txt              |
| Training Epochs     | 50                             |
| Base Model          | PP-OCRv4_rec (Server)          |
| Release Date        | YYYY-MM-DD                     |

## Performance Metrics

| Metric                    | Value   | Threshold |
|---------------------------|---------|-----------|
| Character Error Rate (CER)| X.XX%   | < 1.0%    |
| Stamp Detection IoU       | X.XX    | > 0.95    |
| Avg Page Confidence       | X.XX%   | > 90%     |

## Golden Test Set Results

| Category        | Pages | CER   | Pass |
|-----------------|-------|-------|------|
| Simple Text     | 40    | X.XX% | ☐    |
| Tables          | 30    | X.XX% | ☐    |
| Stamps/Sigs     | 20    | X.XX% | ☐    |
| Poor Scans      | 10    | X.XX% | ☐    |

## Two-Person Rule Verification

### Builder

- Name: ___________________________
- Date: ___________________________
- Git Commit: ___________________________
- Model SHA256: ___________________________

### Auditor

- Name: ___________________________
- Date: ___________________________
- Verified: ☐ Re-ran evaluation in Docker sandbox
- Verified: ☐ Results match builder's scorecard
- GPG Signature: ___________________________

## Pre-Flight Checklist

- [ ] Git Commit Hash matches Release Tag
- [ ] Model SHA256 matches this signed MODEL_RELEASE.md
- [ ] Base Image SHA256 matches allowlist
- [ ] Network Isolation verified (no outbound traffic)
- [ ] Golden Test Set CER < 1%
- [ ] Stamp Detection IoU > 0.95
