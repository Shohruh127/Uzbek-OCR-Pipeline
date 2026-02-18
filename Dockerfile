# Sovereign Uzbek OCR Pipeline - Air-Gapped Dockerfile
# All dependencies served from local vendor/ directory
# Must be built and run with --network=none

FROM python:3.11-slim@sha256:6b1fa21a60ef4a213f97e468e8e55dcca0a3c2d8e04f7b5a68e0e95d2b433d53

LABEL maintainer="Uzbek OCR Pipeline Team"
LABEL version="2.0"
LABEL description="Sovereign-Grade Uzbek OCR Pipeline - Air-Gapped Build"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for OCR processing
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        ghostscript \
        unpaper \
        pngquant \
        tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy vendored wheels and requirements
COPY vendor/ /vendor/
COPY requirements.txt .

# Install Python dependencies from local vendor directory only
RUN pip install --no-index --find-links=/vendor/ -r requirements.txt

# Copy application source
COPY src/ ./src/
COPY configs/ ./configs/
COPY scripts/ ./scripts/

# Create directories for runtime data
RUN mkdir -p /app/data/input /app/data/output /app/data/hocr /app/logs

# Default command
CMD ["python", "-m", "src.pipeline.cascade"]
