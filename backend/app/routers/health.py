"""Health check endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings


router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
    environment: str


class DetailedHealthResponse(HealthResponse):
    """Detailed health check response with component status."""

    database: str
    vector_db: str
    redis: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check() -> DetailedHealthResponse:
    """Detailed health check with component status."""
    # TODO: Implement actual health checks for each component
    return DetailedHealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        database="connected",
        vector_db="connected",
        redis="connected",
    )

