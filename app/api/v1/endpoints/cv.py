"""
CV endpoint:
  POST /api/v1/cv/feedback  — Upload CV (PDF/image), get AI feedback
"""
from app.services.feedback_service import generate_cv_feedback
from fastapi import APIRouter, HTTPException, UploadFile, File, status, Query

from app.core.logger import logger
from app.models.response import CVFeedbackResponse, ErrorResponse
# from app.services.feedback_service import generate_cv_feedback
# from app.utils.pdf_parser import extract_text_from_pdf
# from app.utils.image_parser import extract_text_from_image
# from app.utils.text_cleaner import clean_text

router = APIRouter(prefix="/cv", tags=["CV"])

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
}

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}


@router.post(
    "/feedback",
    response_model=CVFeedbackResponse,
    summary="Upload CV and get AI feedback",
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def cv_feedback_endpoint(
    file: UploadFile = File(..., description="CV file (PDF, PNG, JPG, JPEG, WEBP)"),
    language: str = Query("English", description="Language for the feedback."),
) -> CVFeedbackResponse:
    """
    Accept a CV file upload (PDF or image), extract its text, and return
    structured AI feedback via Gemini covering ATS, layout, keywords, and improvements.
    """
    # Validate file type
    filename = file.filename or ""
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": f"Unsupported file type: {suffix}. Allowed: pdf, png, jpg, jpeg, webp",
                "error_code": "INVALID_FILE_TYPE",
            },
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "Uploaded file is empty.",
                "error_code": "EMPTY_FILE"
            },
        )

    # Extract text
    # try:
    #     if suffix == ".pdf":
    #         raw_text = extract_text_from_pdf(file_bytes)
    #     else:
    #         raw_text = extract_text_from_image(file_bytes)
    # except ValueError as exc:
    #     logger.error(f"Text extraction failed: {exc}")
    #     raise HTTPException(
    #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         detail={"success": False, "message": str(exc), "error_code": "EXTRACTION_ERROR"},
    #     )

    # if not raw_text.strip():
    #     raise HTTPException(
    #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         detail={
    #             "success": False,
    #             "message": "No readable text found in the uploaded file.",
    #             "error_code": "NO_TEXT_FOUND",
    #         },
    #     )

    # Generate AI feedback
    try:
        feedback = await generate_cv_feedback(file_bytes, file.content_type, language=language)
        return CVFeedbackResponse(
            success=True,
            message="CV feedback generated successfully.",
            ats_score=feedback.get("ats_score", 0),
            readability_score=feedback.get("readability_score", 0),
            ats_feedback=feedback.get("ats_feedback", ""),
            layout_feedback=feedback.get("layout_feedback", ""),
            keyword_feedback=feedback.get("keyword_feedback", ""),
            improvements=feedback.get("improvements", []),
        )
    except RuntimeError as exc:
        logger.error(f"Gemini CV feedback error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"success": False, "message": str(exc), "error_code": "GEMINI_ERROR"},
        )
    except Exception as exc:
        logger.error(f"CV feedback unexpected error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(exc), "error_code": "FEEDBACK_ERROR"},
        )
