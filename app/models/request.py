"""
Pydantic v2 request models for all endpoints.
"""
from pydantic import BaseModel, Field


class ExtractSkillsRequest(BaseModel):
    cv_text: str = Field(..., min_length=1, description="Raw CV text to extract skills from.")


class PredictRoleRequest(BaseModel):
    skills: list[str] = Field(..., min_items=1, description="List of extracted skills.")


class SkillGapRequest(BaseModel):
    role: str = Field(..., min_length=1, description="Target role name.")
    skills: list[str] = Field(..., min_items=1, description="User's current skill list.")


class RoadmapRequest(BaseModel):
    cv_text: str = Field(..., min_length=1, description="Raw CV text.")
    skills_extracted: list[str] = Field(..., description="Skills extracted from CV.")
    role: str = Field(..., min_length=1, description="Predicted or chosen role.")
    language: str = Field("English", description="Language for the roadmap.")
