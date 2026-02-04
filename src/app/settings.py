"""
Application settings and configuration.

This module defines the application settings using Pydantic,
loading configuration from environment variables and .env files.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    :cvar ENVIRONMENT: Runtime environment (development or production).
    :cvar SPATIALITE_PATH: Path to SpatiaLite database file for development.
    :cvar POSTGRES_USER: PostgreSQL username.
    :cvar POSTGRES_PASSWORD: PostgreSQL password.
    :cvar POSTGRES_HOST: PostgreSQL server hostname.
    :cvar POSTGRES_PORT: PostgreSQL server port.
    :cvar POSTGRES_DB: PostgreSQL database name.
    """

    ENVIRONMENT: str = Field(default="development")
    SPATIALITE_PATH: str = Field(default="./geo.db")

    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: str = Field(default="5432")
    POSTGRES_DB: str = Field(default="postgres")

    @property
    def is_development(self) -> bool:
        """
        Check if running in development mode.

        :returns: True if development environment.
        :rtype: bool
        """
        return self.ENVIRONMENT.lower() == "development"

    @property
    def database_url(self) -> str:
        """
        Construct the database connection URL.

        Returns SpatiaLite path for development, PostgreSQL for production.

        :returns: SQLAlchemy-compatible database connection string.
        :rtype: str
        """
        if self.is_development:
            return f"sqlite:///{self.SPATIALITE_PATH}"

        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
