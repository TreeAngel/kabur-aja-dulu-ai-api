"""
Roadmap endpoint:
  POST /api/v1/roadmap/generate  — AI-powered career roadmap via Gemini
"""
from fastapi import APIRouter, HTTPException, status

from app.core.logger import logger
from app.models.request import RoadmapRequest
from app.models.response import ErrorResponse, RoadmapResponse
from app.services.roadmap_service import generate_roadmap

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])


@router.post(
    "/generate",
    response_model=RoadmapResponse,
    summary="Generate AI career roadmap",
    responses={500: {"model": ErrorResponse}},
)
async def generate_roadmap_endpoint(body: RoadmapRequest) -> RoadmapResponse:
    """
    Generate a personalized career development roadmap using Gemini AI,
    based on the user's CV, extracted skills, and predicted role.
    """
    try:
        roadmap = await generate_roadmap(
            cv_text=body.cv_text,
            skills_extracted=body.skills_extracted,
            role=body.role,
        )
        return RoadmapResponse(
            success=True,
            message="Career roadmap generated successfully.",
            roadmap=roadmap,
        )
    except RuntimeError as exc:
        logger.error(f"Roadmap generation error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"success": False, "message": str(exc), "error_code": "GEMINI_ERROR"},
        )
    except Exception as exc:
        logger.error(f"Roadmap unexpected error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(exc), "error_code": "ROADMAP_ERROR"},
        )
