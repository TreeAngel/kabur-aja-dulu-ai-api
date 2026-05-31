"""
PDF parser — extracts raw text from PDF files using pdfplumber.
"""
from __future__ import annotations

import io

import pdfplumber

from app.core.logger import logger


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF file given its raw bytes.
    Returns concatenated text from all pages.
    """
    try:
        text_parts: list[str] = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                    logger.debug(f"PDF page {page_num}: extracted {len(page_text)} chars")
                else:
                    logger.debug(f"PDF page {page_num}: no text found (may be image-based)")

        full_text = "\n".join(text_parts)
        logger.info(f"PDF extraction complete: {len(full_text)} total chars from {len(pdf.pages if hasattr(pdf, 'pages') else [])} pages")
        return full_text
    except Exception as exc:
        logger.error(f"PDF extraction failed: {exc}")
        raise ValueError(f"Could not extract text from PDF: {exc}") from exc
