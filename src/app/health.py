"""
Health check endpoint.

This module provides a health check route for monitoring
application and database connectivity.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter()


@router.get("/health", tags=["health"])
def healthcheck(db: Session = Depends(get_db)):
    """
    Check application and database health.

    Executes a simple query to verify database connectivity.

    :param db: Database session dependency.
    :type db: Session
    :returns: Health status dictionary with application and database state.
    :rtype: dict
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "up"}
    except Exception:
        return {"status": "degraded", "db": "down"}
