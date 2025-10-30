from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from dotenv import load_dotenv
import os

from app.api.v1 import routes, admin_users, contact_routes, lead_routes, task_routes, auth_routes
from app.core.config import settings
# from app.core.deps import get_query_token
from app.core.security import require_roles

ENVIRONMENT = os.getenv("ENVIRONMENT")

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Application factory pattern for better testability"""

    app = FastAPI(
        title="CRM Backend API",
        description="A comprehensive CRM system backend",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    )

    # Add security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "message": "CRM backend is running",
            "version": "1.0.0"
        }
    
    # Include routers with organized structure
    include_routers(app)

    return app

def include_routers(app: FastAPI) -> None:
    """Centralized router configuration with proper prefixes and tags."""

    # Authentication routes (no prefix needed)
    app.include_router(
        auth_routes.router,
        prefix="/auth",
        tags=["Authentication"]
    )

    # API v1 routes with common prefix
    api_prefix = "/api/v1"

    routers_config = [
        {
            "router": routes.router,
            "prefix": f"{api_prefix}/general",
            "tags": ["General"]
        },
        {
            "router": admin_users.router,
            "prefix": f"{api_prefix}/admin/users",
            "tags": ["Admin - Users"],
        },
        {
            "router": contact_routes.router,
            "prefix": f"{api_prefix}/contacts",
            "tags": ["Contacts"]
        },
        {
            "router": lead_routes.router,
            "prefix": f"{api_prefix}/leads",
            "tags": ["Leads"]
        },
        {
            "router": task_routes.router,
            "prefix": f"{api_prefix}/tasks",
            "tags": ["Tasks"]
        }
    ]

    # Include all routers with their configurations
    for config in routers_config:
        app.include_router(**config)

# Create app instance
app = create_app()

# Optional: Add startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    logger.info("CRM Backend starting UP...")
    # Initialize database connections, cache, etc.

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("CRM Backend shutting down...")
    # Close database connections, cleanUp, etc.