"""
FastAPI application entrypoint.

This module creates and configures the FastAPI application instance,
registers routers, and provides the uvicorn runner for development.
"""

from logging import DEBUG

import uvicorn
from fastapi import FastAPI

from app.health import router as health_router
from app.routes import router as points_router
from app.settings import settings


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Registers health check and points API routers.

    :returns: Configured FastAPI application instance.
    :rtype: FastAPI
    """
    app = FastAPI(
        title="GeoAlchemy Alembic FastAPI Example",
        # lifespan=lifespan,
        root_path="/api",
        docs_url="/docs",
        redoc_url="/redoc",
        debug=settings.is_development,
    )
    app.include_router(health_router)
    app.include_router(points_router)
    return app


app = create_app()


def main():
    """
    Run the application using uvicorn.

    Starts the development server with hot reload enabled
    based on application settings.
    """
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=DEBUG,
    )


if __name__ == "__main__":
    main()
