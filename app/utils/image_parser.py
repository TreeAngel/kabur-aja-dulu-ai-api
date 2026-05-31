"""
Image parser — extracts text from image files using EasyOCR.
Falls back to pytesseract if EasyOCR is unavailable.
"""
from __future__ import annotations

import io

from app.core.logger import logger


def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Extract text from an image (PNG, JPG, JPEG, WEBP) using EasyOCR.
    Falls back to pytesseract if EasyOCR import fails.
    """
    try:
        return _extract_with_easyocr(file_bytes)
    except ImportError:
        logger.warning("EasyOCR not available, falling back to pytesseract.")
        return _extract_with_pytesseract(file_bytes)


def _extract_with_easyocr(file_bytes: bytes) -> str:
    import easyocr  # type: ignore
    import numpy as np
    from PIL import Image

    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img_array = np.array(img)

    reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    results = reader.readtext(img_array, detail=0, paragraph=True)
    text = "\n".join(results)
    logger.info(f"EasyOCR extracted {len(text)} chars from image.")
    return text


def _extract_with_pytesseract(file_bytes: bytes) -> str:
    import pytesseract  # type: ignore
    from PIL import Image

    img = Image.open(io.BytesIO(file_bytes))
    text = pytesseract.image_to_string(img)
    logger.info(f"pytesseract extracted {len(text)} chars from image.")
    return text
