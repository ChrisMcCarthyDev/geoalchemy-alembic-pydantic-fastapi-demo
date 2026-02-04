"""
Alembic environment configuration.

This module configures Alembic to use either SpatiaLite (development)
or PostGIS (production) based on the ENVIRONMENT setting.
"""

import ctypes
import os
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, pool

from alembic import context
from app.db import Base
from app.models import ExamplePoint  # noqa: F401 to register models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Grab .env from repo root
dot_env_path = Path(__file__).parent.parent.parent / ".env"

# Load .env file
load_dotenv(dotenv_path=dot_env_path)

# Determine environment and set database URL accordingly
environment = os.environ.get("ENVIRONMENT", "development").lower()
is_development = environment == "development"

if is_development:
    spatialite_path = os.environ.get("SPATIALITE_PATH", "./geo.db")
    database_url = f"sqlite:///{spatialite_path}"
else:
    database_url = (
        f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
        f"@localhost:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
    )

config.set_main_option("sqlalchemy.url", database_url)

# Path to local SpatiaLite DLLs (relative to repo root)
SPATIALITE_DIR = (
    Path(__file__).parent.parent.parent / "lib" / "mod_spatialite-5.1.0-win-amd64"
)
SPATIALITE_DLL = SPATIALITE_DIR / "mod_spatialite.dll"

# Preload SpatiaLite DLL on Windows in development
if os.name == "nt" and is_development:
    os.add_dll_directory(str(SPATIALITE_DIR))
    ctypes.CDLL(str(SPATIALITE_DLL))

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

# SpatiaLite internal tables to exclude from autogenerate
SPATIALITE_TABLES = {
    "spatial_ref_sys",
    "spatial_ref_sys_aux",
    "geometry_columns",
    "geometry_columns_auth",
    "geometry_columns_field_infos",
    "geometry_columns_statistics",
    "geometry_columns_time",
    "views_geometry_columns",
    "views_geometry_columns_auth",
    "views_geometry_columns_field_infos",
    "views_geometry_columns_statistics",
    "virts_geometry_columns",
    "virts_geometry_columns_auth",
    "virts_geometry_columns_field_infos",
    "virts_geometry_columns_statistics",
    "spatialite_history",
    "sql_statements_log",
    "data_licenses",
    "ElementaryGeometries",
    "SpatialIndex",
    "KNN2",
}


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter objects for autogenerate.

    Excludes SpatiaLite internal metadata tables from migration generation.
    """
    if type_ == "table" and name in SPATIALITE_TABLES:
        return False
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    # Load SpatiaLite extension in development
    if is_development:

        @event.listens_for(connectable, "connect")
        def load_spatialite(dbapi_conn, connection_record):
            """Load the SpatiaLite extension on each connection."""
            dbapi_conn.enable_load_extension(True)
            dbapi_conn.load_extension("mod_spatialite")
            dbapi_conn.enable_load_extension(False)
            dbapi_conn.execute("SELECT InitSpatialMetaData(1);")

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
