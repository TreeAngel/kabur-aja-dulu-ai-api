"""
Skill Extraction Service — Rule-based NLP using industry_skills.json.
Matches skills from cleaned CV text using regex word-boundary matching.

Reference: Notebook Section 6 — Rule-Based NLP Skill Extraction.

Note: industry_skills.json is a flat list of skill strings.
"""
from __future__ import annotations

import re

from app.ai.model_loader import ModelService
from app.core.logger import logger
from app.utils.text_cleaner import clean_text


def extract_skills(cv_text: str) -> list[str]:
    """
    Extract skills from raw CV text using rule-based matching.

    Steps:
    1. clean_text()
    2. Load industry_skills list from ModelService
    3. Iterate all skills and match with regex word-boundary
    4. Return unique matched skills (sorted)
    """
    cleaned = clean_text(cv_text)
    industry_skills = ModelService.get_industry_skills()

    # industry_skills.json is a flat list of skill strings
    if isinstance(industry_skills, list):
        all_skills: list[str] = industry_skills
    elif isinstance(industry_skills, dict):
        # Fallback for dict format: flatten all values
        all_skills = []
        for skills in industry_skills.values():
            if isinstance(skills, list):
                all_skills.extend(skills)
    else:
        all_skills = []

    matched: set[str] = set()

    for skill in all_skills:
        # Build a regex pattern that handles multi-word skills and special chars
        # Escape the skill string, then wrap with word boundaries
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, cleaned, re.IGNORECASE):
            matched.add(skill)

    result = sorted(matched)
    logger.info(f"Skill extraction: {len(result)} skills found from {len(cleaned)} chars")
    return result
