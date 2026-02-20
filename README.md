# Uzbek-OCR-Pipeline

An end-to-end OCR pipeline for extracting text from images written in the Uzbek language (Latin script).

## Features

- Image preprocessing: grayscale conversion, denoising, binarization, and deskewing
- OCR via [Tesseract](https://github.com/tesseract-ocr/tesseract) with Uzbek language support
- Post-processing: common error correction and whitespace normalization

## Requirements

- Python 3.10+
- Tesseract OCR with the `uzb` language pack

### Install Tesseract (Ubuntu/Debian)

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-uzb
```

### Install Python dependencies

```bash
pip install -r requirements.txt
```

## Usage

```bash
python pipeline.py path/to/image.png
```

### Optional arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--lang` | `uzb`   | Tesseract language code |

## Project structure

```
.
├── pipeline.py          # CLI entry point
├── requirements.txt
└── src/
    ├── preprocessing.py # Image preprocessing
    ├── ocr.py           # Tesseract OCR wrapper
    ├── postprocessing.py # Text cleanup
```

## Running tests

```bash
python -m pytest tests/
```
