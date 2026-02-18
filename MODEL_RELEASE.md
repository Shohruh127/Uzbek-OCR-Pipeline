# MODEL RELEASE

## Model Information

- **Model Name**: PP-OCRv4_rec_uz
- **Version**: (to be filled)
- **Release Date**: (to be filled)
- **Git Commit Hash**: (to be filled)

## Model Checksum

```
SHA256: (to be filled by builder)
```

## Evaluation Results

- **Overall CER**: (to be filled)
- **Uzbek Cyrillic CER**: (to be filled)
- **Uzbek Latin CER**: (to be filled)
- **Russian CER**: (to be filled)
- **Stamp Detection IoU**: (to be filled)

## Pass Criteria

- [ ] CER < 1% on Golden Test Set
- [ ] Stamp Detection IoU > 0.95
- [ ] All category breakdowns within tolerance

## Two-Person Rule Verification

### Builder

- **Name**: (to be filled)
- **Date**: (to be filled)
- **Action**: Trained and evaluated the model

```
-----BEGIN PGP SIGNATURE-----
(Builder's GPG signature here)
-----END PGP SIGNATURE-----
```

### Auditor

- **Name**: (to be filled)
- **Date**: (to be filled)
- **Action**: Independently verified results in Docker sandbox

```
-----BEGIN PGP SIGNATURE-----
(Auditor's GPG signature here)
-----END PGP SIGNATURE-----
```

## Pre-Flight Checklist

- [ ] Git Commit Hash matches Release Tag
- [ ] Model SHA256 matches this document
- [ ] Base Image SHA256 matches allowlist
- [ ] Network Isolation verified (no outbound traffic)
- [ ] Evaluation reproduced in Docker sandbox
- [ ] Two-Person Rule signatures verified
