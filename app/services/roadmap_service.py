"""
Roadmap Generation Service — uses Gemini AI to produce a career roadmap.
Loads the prompt template from prompts/roadmap_prompt.txt.
"""
from __future__ import annotations

import re
from pathlib import Path

from app.ai.gemini_client import generate_text
from app.core.logger import logger

PROMPT_PATH = Path("prompts/roadmap_prompt.txt")


def _load_prompt_template() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    # Fallback inline placeholder
    return (
        "You are a senior career mentor.\n\n"
        "Role:\n{role}\n\n"
        "Detected Skills:\n{skills}\n\n"
        "CV Summary:\n{cv_text}\n\n"
        "Generate a numbered career development roadmap (at least 5 steps) "
        "tailored to help this person grow into the specified role. "
        "Format: return ONLY a JSON object like {\"1\": \"step\", \"2\": \"step\", ...}"
    )


async def generate_roadmap(
    cv_text: str,
    skills_extracted: list[str],
    role: str,
    language: str,
) -> dict[str, str]:
    """
    Generate a career roadmap via Gemini.
    Returns a dict mapping step number (string) to step description.
    """
    template = _load_prompt_template()
    prompt = (
        template.replace("{role}", role)
        .replace("{skills}", ", ".join(skills_extracted))
        .replace("{cv_text}", cv_text[:2000])
        .replace("{language}", language)
    )

    logger.info(f"Generating roadmap for role: {role!r}")
    raw_text = await generate_text(prompt)
    logger.debug(f"Gemini roadmap raw response: {raw_text[:300]}")

    roadmap = _parse_roadmap(raw_text)
    return roadmap


def _parse_roadmap(raw: str) -> dict[str, str]:
    """
    Try to parse Gemini's response as a JSON roadmap dict.
    Falls back to line-by-line parsing if JSON is malformed.
    """
    import json

    # Try JSON extraction
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Fallback: parse numbered lines
    roadmap: dict[str, str] = {}
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    step = 1
    for line in lines:
        # Match lines like "1. ...", "1) ...", "Step 1: ..."
        match = re.match(r"^(?:step\s*)?\d+[\.\):\-]\s*(.+)", line, re.IGNORECASE)
        if match:
            roadmap[str(step)] = match.group(1).strip()
            step += 1

    if not roadmap:
        # Last resort: just split into chunks
        for i, line in enumerate(lines[:8], start=1):
            roadmap[str(i)] = line

    return roadmap
