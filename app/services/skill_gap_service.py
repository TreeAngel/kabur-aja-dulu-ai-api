"""
Skill Gap Analysis Service.

Flow (mirrors Notebook Section 18):
  detected_skills + predicted_role
    → look up top skill industri untuk role tsb dari industry_skills.json
    → compare
    → matched / missing / gap score

Note: industry_skills.json is a flat list of skills (not role-categorized).
All skills in the list are used as the industry benchmark.
"""
from __future__ import annotations

from app.ai.model_loader import ModelService
from app.core.logger import logger

# How many top skills to consider from industry_skills list
TOP_N_SKILLS = 15


def analyze_skill_gap(
    role: str,
    user_skills: list[str],
) -> dict:
    """
    Compare user_skills against the top industry skills from industry_skills.json.

    Since industry_skills.json is a flat list, we use the top N skills
    as the benchmark for all roles.

    Returns a dict with:
        - skills_dimiliki: matched skills
        - top_skill_tidak_dimiliki: missing top skills
        - match_score: percentage (0-100)
    """
    industry_skills = ModelService.get_industry_skills()

    # industry_skills.json is a flat list of skills
    if isinstance(industry_skills, list):
        top_skills: list[str] = industry_skills[:TOP_N_SKILLS]
    elif isinstance(industry_skills, dict):
        # Fallback: if it's a dict, try to find by role or flatten all values
        top_skills = _find_role_skills_from_dict(role, industry_skills)
    else:
        logger.warning("Unexpected industry_skills format.")
        top_skills = []

    if not top_skills:
        logger.warning(f"No industry skills available for gap analysis.")
        return {
            "skills_dimiliki": [],
            "top_skill_tidak_dimiliki": [],
            "match_score": 0,
        }

    # Normalize for case-insensitive comparison
    user_lower = {s.lower() for s in user_skills}
    top_lower_map = {s.lower(): s for s in top_skills}

    matched_original = [top_lower_map[s] for s in top_lower_map if s in user_lower]
    missing_original = [top_lower_map[s] for s in top_lower_map if s not in user_lower]

    match_score = round((len(matched_original) / len(top_skills)) * 100) if top_skills else 0

    logger.info(
        f"Skill gap for role={role!r}: {match_score}% match "
        f"({len(matched_original)}/{len(top_skills)} top skills)"
    )

    return {
        "skills_dimiliki": matched_original,
        "top_skill_tidak_dimiliki": missing_original,
        "match_score": match_score,
    }


def _find_role_skills_from_dict(role: str, industry_skills: dict) -> list[str]:
    """Case-insensitive lookup for role in industry_skills dict keys."""
    role_lower = role.lower()
    for key, skills in industry_skills.items():
        if role_lower in key.lower() or key.lower() in role_lower:
            return skills if isinstance(skills, list) else []
    # Fallback: flatten all
    all_skills: list[str] = []
    for skills in industry_skills.values():
        if isinstance(skills, list):
            all_skills.extend(skills)
    return all_skills[:TOP_N_SKILLS]
