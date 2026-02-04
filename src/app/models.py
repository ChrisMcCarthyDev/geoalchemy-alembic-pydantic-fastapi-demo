"""
SQLAlchemy models for geospatial point data.

This module defines the database models for storing geospatial point
data using GeoAlchemy2 and PostGIS.
"""

from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Float, Integer

from app.db import Base


class ExamplePoint(Base):
    """
    SQLAlchemy model representing a geospatial point with an associated value.

    This model stores point geometries in WGS84 (SRID 4326) coordinate
    reference system along with a numeric value and creation timestamp.

    :cvar id: Primary key identifier.
    :cvar created_at: Timestamp of record creation, defaults to current time.
    :cvar geom: PostGIS Point geometry in WGS84 (SRID 4326).
    :cvar value: Numeric value associated with the point.
    """

    __tablename__ = "example_point"

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
    value = Column(Float, nullable=False)
