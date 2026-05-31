"""
Roles endpoint:
  POST /api/v1/roles/predict  — Deep learning role classification
"""
from fastapi import APIRouter, HTTPException, status

from app.ai.model_loader import ModelService
from app.core.logger import logger
from app.models.request import PredictRoleRequest
from app.models.response import ErrorResponse, PredictRoleResponse
from app.services.role_prediction_service import predict_role

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post(
    "/predict",
    response_model=PredictRoleResponse,
    summary="Predict industry role from skills",
    responses={500: {"model": ErrorResponse}},
)
async def predict_role_endpoint(body: PredictRoleRequest) -> PredictRoleResponse:
    """
    Classify the most likely industry role from a list of skills
    using the trained Keras deep learning model.
    """
    if not ModelService.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"success": False, "message": "Model not loaded", "error_code": "MODEL_ERROR"},
        )
    try:
        role, confidence = predict_role(body.skills)
        return PredictRoleResponse(
            success=True,
            message="Role prediction successful.",
            role=role,
            confidence=confidence,
        )
    except Exception as exc:
        logger.error(f"Role prediction error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(exc), "error_code": "PREDICTION_ERROR"},
        )
