"""Main FastAPI application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.session import get_db_manager

# Configure logging first
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.
    
    Args:
        app: FastAPI application
        
    Yields:
        None
    """
    # Startup
    logger.info("application_startup")
    
    # Initialize database
    db_manager = get_db_manager()
    await db_manager.create_tables()
    logger.info("database_initialized")
    
    yield
    
    # Shutdown
    logger.info("application_shutdown")
    await db_manager.close()


# Create FastAPI application
app = FastAPI(
    title="AI Research Agent",
    description="Automated market research and competitive analysis agent",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["research"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.
    
    Returns:
        Welcome message
    """
    return {
        "message": "AI Research Agent API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )
