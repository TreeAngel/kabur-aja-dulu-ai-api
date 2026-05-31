"""
CV Feedback Service — uses Gemini AI to analyze a CV and return structured feedback.
Loads the prompt template from prompts/cv_feedback_prompt.txt.
"""
from __future__ import annotations

import re
from pathlib import Path

from app.ai.gemini_client import generate_from_file
from app.core.logger import logger

PROMPT_PATH = Path("prompts/cv_feedback_prompt.txt")


def _load_prompt_template() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return (
        "Analyze this CV and provide structured feedback.\n\n"
        "CV Text:\n{cv_text}\n\n"
        "Please provide:\n"
        "1. ATS feedback (how well the CV is optimized for Applicant Tracking Systems)\n"
        "2. Layout feedback (structure, readability, formatting)\n"
        "3. Missing keywords that should be added\n"
        "4. Specific improvement suggestions (list at least 3)\n\n"
        "Format your response as a JSON object with keys: "
        "ats_feedback, layout_feedback, keyword_feedback, improvements (array of strings)."
    )


async def generate_cv_feedback(
    file_bytes: bytes,
    mime_type: str,
    language: str,
) -> dict:
    """
    Send CV text to Gemini and parse structured feedback.
    Returns dict with ats_feedback, layout_feedback, keyword_feedback, improvements.
    """
    template = _load_prompt_template()
    prompt = template.replace("{language}", language)

    logger.info("Generating CV feedback via Gemini.")
    raw_text = await generate_from_file(
        file_bytes=file_bytes,
        mime_type=mime_type,
        prompt=prompt,
    )
    logger.debug(f"Gemini CV feedback raw: {raw_text[:300]}")

    return _parse_feedback(raw_text)


def _parse_feedback(raw: str) -> dict:
    """Parse Gemini response into structured feedback dict."""
    import json

    # Try JSON extraction
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return {
                "ats_feedback": data.get("ats_feedback", ""),
                "layout_feedback": data.get("layout_feedback", ""),
                "keyword_feedback": data.get("keyword_feedback", ""),
                "improvements": data.get("improvements", []),
            }
        except json.JSONDecodeError:
            pass

    # Fallback: return raw text split into sections
    logger.warning("Could not parse Gemini feedback as JSON — returning raw text.")
    return {
        "ats_feedback": raw,
        "layout_feedback": "",
        "keyword_feedback": "",
        "improvements": [],
    }
