"""Image preprocessing utilities for the Uzbek OCR pipeline."""

import cv2
import numpy as np
from PIL import Image


def load_image(path: str) -> np.ndarray:
    """Load an image from disk and return it as a BGR NumPy array."""
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {path}")
    return image


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert a BGR image to grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def denoise(image: np.ndarray) -> np.ndarray:
    """Apply Gaussian blur to reduce noise."""
    return cv2.GaussianBlur(image, (3, 3), 0)


def binarize(image: np.ndarray) -> np.ndarray:
    """Apply Otsu's thresholding to produce a binary image."""
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def deskew(image: np.ndarray) -> np.ndarray:
    """Correct skew in a grayscale or binary image.

    The function treats dark pixels (value < 128) as foreground, which is the
    standard output of Otsu's binarization on document images.
    """
    coords = np.column_stack(np.where(image < 128))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)


def preprocess(path: str) -> np.ndarray:
    """Full preprocessing pipeline: load → grayscale → denoise → binarize → deskew."""
    image = load_image(path)
    gray = to_grayscale(image)
    denoised = denoise(gray)
    binary = binarize(denoised)
    return deskew(binary)
