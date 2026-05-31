"""
KaburAjaDulu.AI — FastAPI Application Entry Point

Features:
- Layered architecture with dependency injection
- Singleton ModelService (loads once at startup)
- Structured logging
- Consistent JSON error responses
- OpenAPI docs at /docs
- Health check at /health
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.ai.model_loader import ModelService
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logger import logger
from app.models.response import HealthResponse


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all AI artifacts on startup; release resources on shutdown."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.APP_ENV}]")
    try:
        ModelService.load()
    except Exception as exc:
        logger.critical(f"FATAL: Could not load model artifacts: {exc}")
        # Don't crash the server — endpoints will return 503 if model is not loaded
    yield
    logger.info("Shutting down KaburAjaDulu.AI API.")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered CV analysis platform. "
        "Extracts skills, predicts roles, analyzes skill gaps, "
        "generates career roadmaps, and provides AI CV feedback."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global Exception Handlers ─────────────────────────────────────────────────

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict):
        # Already formatted correctly
        success = detail.get("success", False)
        message = detail.get("message", "An error occurred.")
        error_code = detail.get("error_code", "HTTP_ERROR")
        
        # Merge other fields if any
        content = {"success": success, "message": message, "error_code": error_code}
        for k, v in detail.items():
            if k not in content:
                content[k] = v
        
        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content=content,
        )
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "success": False,
            "message": str(detail),
            "error_code": "HTTP_ERROR",
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    # Format a friendly message listing validation errors
    msg = "Validation failed: " + "; ".join([f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in errors])
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": msg,
            "error_code": "VALIDATION_ERROR",
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected internal error occurred.",
            "error_code": "INTERNAL_ERROR",
        },
    )

# ── Health Check ──────────────────────────────────────────────────────────────

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="API health check",
)
async def health_check() -> HealthResponse:
    """Check API health and model load status."""
    return HealthResponse(
        status="healthy",
        model_loaded=ModelService.is_loaded(),
        version=settings.APP_VERSION,
    )

# ── Include Routers ───────────────────────────────────────────────────────────

app.include_router(api_router)


# ── Dev Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
