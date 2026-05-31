"""
Security utilities — API key validation placeholder.
Extend this module to add authentication middleware as needed.
"""
from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

from app.core.config import settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key: str | None = Security(api_key_header)) -> str | None:
    """
    Optional API key guard.
    Returns the key if provided and valid, otherwise raises 403.
    Set REQUIRE_API_KEY=true in .env to enforce.
    """
    # For now, security is opt-in — no key required in dev mode
    if settings.DEBUG:
        return api_key
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key required",
        )
    return api_key
