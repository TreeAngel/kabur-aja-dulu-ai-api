"""
API v1 router — aggregates all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import skills, roles, roadmap, cv

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(skills.router)
api_router.include_router(roles.router)
api_router.include_router(roadmap.router)
api_router.include_router(cv.router)
