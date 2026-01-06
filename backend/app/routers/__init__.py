"""API routers for LavenderSentinel."""

from fastapi import APIRouter

from app.routers import papers, search, chat, health

# Create main router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

__all__ = ["api_router"]

