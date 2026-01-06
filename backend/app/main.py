"""FastAPI application entry point for LavenderSentinel."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.database import init_db, close_db
from app.routers import api_router
from app.core.exceptions import LavenderSentinelError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")
    
    # Initialize database
    await init_db()
    print("Database initialized")
    
    # Initialize CocoIndex (optional, can be done lazily)
    try:
        from app.indexing.pipeline import paper_indexer
        paper_indexer.initialize()
        print("CocoIndex initialized")
    except Exception as e:
        print(f"CocoIndex initialization skipped: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await close_db()
    print("Database connections closed")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="A system that automatically collects, indexes, and summarizes research papers with LLM-assisted conversation",
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Exception handlers
    @app.exception_handler(LavenderSentinelError)
    async def lavender_exception_handler(
        request: Request,
        exc: LavenderSentinelError,
    ) -> JSONResponse:
        """Handle custom LavenderSentinel exceptions."""
        return JSONResponse(
            status_code=400,
            content={
                "error": exc.message,
                "details": exc.details,
            },
        )
    
    # Include API router
    app.include_router(api_router, prefix=settings.api_prefix)
    
    # Root endpoint
    @app.get("/")
    async def root() -> dict:
        """Root endpoint with API information."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": f"{settings.api_prefix}/docs" if settings.debug else "disabled",
            "health": f"{settings.api_prefix}/health",
        }
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )

