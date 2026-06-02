"""
Gemini AI client — wraps google-generativeai for text generation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logger import logger

_client: Optional[genai.Client] = None

DEFAULT_MODEL = "gemini-3.1-flash-lite"

def _init_client() -> genai.Client:
    global _client

    if _client is not None:
        return _client

    api_key = settings.GEMINI_API_KEY

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )

    _client = genai.Client(api_key=api_key)

    logger.info("Gemini client initialized.")

    return _client


async def generate_text(
    prompt: str,
    model_name: str = DEFAULT_MODEL,
) -> str:
    """
    Text-only generation.
    """

    client = _init_client()

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        return response.text or ""

    except Exception as exc:
        logger.exception("Gemini text generation failed")

        raise RuntimeError(
            f"Gemini generation failed: {exc}"
        ) from exc


async def generate_from_file(
    file_bytes: bytes,
    mime_type: str,
    prompt: str,
    model_name: str = DEFAULT_MODEL,
) -> str:
    """
    PDF / Image + Prompt generation.
    Supports:
    - pdf
    - png
    - jpg
    - jpeg
    - webp
    """

    client = _init_client()

    try:
        file_parts = types.Part.from_bytes(
            data=file_bytes,
            mime_type=mime_type
        )

        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, file_parts],
        )

        return response.text or ""

    except Exception as exc:
        logger.exception("Gemini file generation failed")

        raise RuntimeError(
            f"Gemini file generation failed: {exc}"
        ) from exc
