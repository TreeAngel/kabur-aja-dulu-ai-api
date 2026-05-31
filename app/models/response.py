"""
Pydantic v2 response models for all endpoints.
Every response includes success, message, and optional error_code.
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


# ── Base ─────────────────────────────────────────────────────────────────────

class BaseResponse(BaseModel):
    success: bool
    message: str = "OK"
    error_code: str | None = None


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str


# ── Skills ────────────────────────────────────────────────────────────────────

class ExtractSkillsResponse(BaseResponse):
    skills_extracted: list[str] = Field(default_factory=list)


# ── Role Prediction ───────────────────────────────────────────────────────────

class PredictRoleResponse(BaseResponse):
    role: str | None = None
    confidence: float | None = None


# ── Skill Gap ─────────────────────────────────────────────────────────────────

class SkillGapResponse(BaseResponse):
    role: str | None = None
    match_score: int | None = None
    skills_dimiliki: list[str] = Field(default_factory=list)
    top_skill_tidak_dimiliki: list[str] = Field(default_factory=list)


# ── Roadmap ───────────────────────────────────────────────────────────────────

class RoadmapResponse(BaseResponse):
    roadmap: dict[str, str] = Field(default_factory=dict)


# ── CV Feedback ───────────────────────────────────────────────────────────────

class CVFeedbackResponse(BaseResponse):
    ats_score: int | None = None
    readability_score: int | None = None
    ats_feedback: str | None = None
    layout_feedback: str | None = None
    keyword_feedback: str | None = None
    improvements: list[str] = Field(default_factory=list)


# ── Error ─────────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str | None = None
