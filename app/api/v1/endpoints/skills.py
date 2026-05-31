"""
Skills endpoints:
  POST /api/v1/skills/extract    — Rule-based skill extraction
  POST /api/v1/skills/gap-analysis — Skill gap against industry top skills
"""
from fastapi import APIRouter, HTTPException, status

from app.ai.model_loader import ModelService
from app.core.logger import logger
from app.models.request import ExtractSkillsRequest, SkillGapRequest
from app.models.response import ExtractSkillsResponse, ErrorResponse, SkillGapResponse
from app.services.skill_extraction_service import extract_skills
from app.services.skill_gap_service import analyze_skill_gap

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.post(
    "/extract",
    response_model=ExtractSkillsResponse,
    summary="Extract skills from CV text",
    responses={500: {"model": ErrorResponse}},
)
async def extract_skills_endpoint(body: ExtractSkillsRequest) -> ExtractSkillsResponse:
    """
    Extract skills from raw CV text using rule-based NLP and industry_skills.json.
    """
    if not ModelService.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"success": False, "message": "Model not loaded", "error_code": "MODEL_ERROR"},
        )
    try:
        skills = extract_skills(body.cv_text)
        return ExtractSkillsResponse(
            success=True,
            message=f"Successfully extracted {len(skills)} skill(s).",
            skills_extracted=skills,
        )
    except Exception as exc:
        logger.error(f"Skill extraction error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(exc), "error_code": "EXTRACTION_ERROR"},
        )


@router.post(
    "/gap-analysis",
    response_model=SkillGapResponse,
    summary="Analyze skill gap for a given role",
    responses={500: {"model": ErrorResponse}},
)
async def skill_gap_endpoint(body: SkillGapRequest) -> SkillGapResponse:
    """
    Compare user's skills against industry top skills for the specified role.
    Returns match score and missing skills.
    """
    if not ModelService.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"success": False, "message": "Model not loaded", "error_code": "MODEL_ERROR"},
        )
    try:
        result = analyze_skill_gap(role=body.role, user_skills=body.skills)
        return SkillGapResponse(
            success=True,
            message="Skill gap analysis complete.",
            role=body.role,
            match_score=result["match_score"],
            skills_dimiliki=result["skills_dimiliki"],
            top_skill_tidak_dimiliki=result["top_skill_tidak_dimiliki"],
        )
    except Exception as exc:
        logger.error(f"Skill gap error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(exc), "error_code": "SKILL_GAP_ERROR"},
        )
