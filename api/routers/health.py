from fastapi import APIRouter

from api.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check."""
    return {"status": "ok", "environment": settings.app_env}
