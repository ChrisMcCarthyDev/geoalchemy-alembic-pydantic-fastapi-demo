"""
CRUD operations for ExamplePoint model.

This module provides database operations for creating and retrieving
spatial point data stored in PostGIS.
"""

from geoalchemy2.shape import from_shape
from shapely import wkt
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ExamplePoint
from app.schemas import ExamplePointCreate


def create_example_point(db: Session, data: ExamplePointCreate) -> ExamplePoint:
    """
    Create a new point in the database.

    Converts WKT geometry string to PostGIS-compatible format and
    persists the point with its associated value.

    :param db: SQLAlchemy database session.
    :param data: Pydantic schema containing point geometry and value.
    :return: The created ExamplePoint instance with populated id and created_at.
    :raises sqlalchemy.exc.SQLAlchemyError: If database operation fails.
    """
    point_geom = from_shape(wkt.loads(data.geom), srid=4326)
    db_obj = ExamplePoint(geom=point_geom, value=data.value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_all_example_points(db: Session) -> list[ExamplePoint]:
    """
    Retrieve all points from the database.

    :param db: SQLAlchemy database session.
    :return: List of all ExamplePoint instances.
    """
    return db.execute(select(ExamplePoint)).scalars().all()


def get_example_points_in_bbox(
    db: Session,
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float,
) -> list[ExamplePoint]:
    """
    Retrieve points intersecting a bounding box (WGS84 / SRID 4326).

    Uses a PostGIS envelope and ST_Intersects, which is index-friendly with
    a GiST/SP-GiST index on the geometry column.

    :param db: SQLAlchemy database session.
    :param min_lat: Minimum latitude (south bound).
    :param max_lat: Maximum latitude (north bound).
    :param min_lon: Minimum longitude (west bound).
    :param max_lon: Maximum longitude (east bound).
    :return: List of ExamplePoint instances inside/intersecting the bbox.
    """
    envelope = func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)

    stmt = (
        select(ExamplePoint)
        .where(func.ST_Intersects(ExamplePoint.geom, envelope))
        .order_by(ExamplePoint.id)
    )

    return db.execute(stmt).scalars().all()
