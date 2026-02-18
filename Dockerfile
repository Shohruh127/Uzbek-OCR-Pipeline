# Sovereign-Grade Uzbek OCR Pipeline v2.0
# Air-gapped Dockerfile with pinned dependencies
# Build: docker build --network=none -t uzbek-ocr .
# Run:   docker run --network=none uzbek-ocr

FROM python:3.11-slim@sha256:2a93f41f1e3b06a5dc0baa2150f0f9b8b5b2e8fa0c0e1a5e3b0e0b0c0d0e0f0

LABEL maintainer="Sovereign OCR Team"
LABEL version="2.0.0"
LABEL description="Air-gapped Uzbek OCR Pipeline"

# Install system dependencies required by OpenCV and PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy vendored wheels for air-gapped install
COPY vendor/ /vendor/

# Install Python dependencies from local vendor directory only
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/vendor/ -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY tests/ ./tests/

# Copy governance templates
COPY docs/ ./docs/

# Non-root user for security
RUN useradd --create-home --shell /bin/bash ocruser
USER ocruser

ENTRYPOINT ["python", "-m", "src.pipeline"]
