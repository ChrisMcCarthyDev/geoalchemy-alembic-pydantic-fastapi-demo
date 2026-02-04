"""
Database configuration and session management.

This module configures the SQLAlchemy engine and session factory
for connecting to either a SpatiaLite database (development) or
a PostGIS-enabled PostgreSQL database (production).
"""

import ctypes
import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.settings import settings

# Path to local SpatiaLite DLLs (relative to repo root)
SPATIALITE_DIR = (
    Path(__file__).parent.parent.parent / "lib" / "mod_spatialite-5.1.0-win-amd64"
)
SPATIALITE_DLL = SPATIALITE_DIR / "mod_spatialite.dll"

# Preload SpatiaLite DLL on Windows in development
if os.name == "nt" and settings.is_development:
    os.add_dll_directory(str(SPATIALITE_DIR))
    ctypes.CDLL(str(SPATIALITE_DLL))


def _create_engine():
    """
    Create the appropriate database engine based on environment.

    In development, creates a SQLite engine with SpatiaLite extension.
    In production, creates a PostgreSQL engine for PostGIS.

    :returns: Configured SQLAlchemy engine.
    :rtype: Engine
    """
    engine = create_engine(settings.database_url, echo=True)

    if settings.is_development:

        @event.listens_for(engine, "connect")
        def load_spatialite(dbapi_conn, connection_record):
            """Load the SpatiaLite extension on each connection."""
            dbapi_conn.enable_load_extension(True)
            dbapi_conn.load_extension("mod_spatialite")
            dbapi_conn.enable_load_extension(False)
            dbapi_conn.execute("SELECT InitSpatialMetaData(1);")

    return engine


def run_migrations():
    """
    Run Alembic migrations programmatically.

    Only runs in development mode. Uses the alembic.ini config
    from the src directory.
    """
    if not settings.is_development:
        return

    from alembic import command
    from alembic.config import Config

    alembic_ini = Path(__file__).parent.parent / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini))

    command.upgrade(alembic_cfg, "head")


engine = _create_engine()
"""SQLAlchemy engine instance configured from settings."""

SessionLocal = sessionmaker(bind=engine)
"""Session factory for creating database sessions."""

Base = declarative_base()
"""Declarative base class for SQLAlchemy models."""


def get_db():
    """
    Dependency that provides a database session.

    Yields a SQLAlchemy session and ensures it is closed after use.

    :yields: Database session.
    :ytype: Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
