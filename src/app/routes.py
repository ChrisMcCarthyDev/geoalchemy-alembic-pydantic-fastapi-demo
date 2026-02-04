"""
API routes for geospatial point operations.

This module defines the FastAPI routes for creating and retrieving
geospatial points.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import (
    create_example_point,
    get_all_example_points,
    get_example_points_in_bbox,
)
from app.db import get_db
from app.schemas import ExamplePointCreate, ExamplePointModel

router = APIRouter()


@router.post(
    "/points",
    summary="Create a new geospatial point.",
    description=(
        "Create a new geospatial point in WGS84 (SRID 4326) along with a numeric "
        "value and creation timestamp."
    ),
    response_model=ExamplePointModel,
)
def create_point(payload: ExamplePointCreate, db: Session = Depends(get_db)):
    """
    Create a new geospatial point.

    Expects a WKT point string in the form ``POINT(longitude latitude)`` and a
    numeric value. The geometry is stored in PostGIS as SRID 4326.

    :param payload: Point data including WKT geometry and value.
    :type payload: ExamplePointCreate
    :param db: Database session dependency.
    :type db: Session
    :returns: The created point record.
    :rtype: ExamplePointModel
    """
    return create_example_point(db, payload)


@router.get(
    "/points",
    summary="Retrieve all geospatial points.",
    description="Return all stored geospatial points.",
    response_model=list[ExamplePointModel],
)
def read_points(db: Session = Depends(get_db)):
    """
    Retrieve all geospatial points.

    :param db: Database session dependency.
    :type db: Session
    :returns: List of all point records.
    :rtype: list[ExamplePointModel]
    """
    return get_all_example_points(db)


@router.get(
    "/points/bbox",
    summary="Retrieve points within a bounding box.",
    description="Filter points by min/max latitude/longitude (WGS84 / SRID 4326).",
    response_model=list[ExamplePointModel],
)
def read_points_in_bbox(
    min_lat: Annotated[float, Query(description="Minimum latitude", ge=-90, le=90)],
    max_lat: Annotated[float, Query(description="Maximum latitude", ge=-90, le=90)],
    min_lon: Annotated[float, Query(description="Minimum longitude", ge=-180, le=180)],
    max_lon: Annotated[float, Query(description="Maximum longitude", ge=-180, le=180)],
    db: Session = Depends(get_db),
):
    """
    Retrieve points within a bounding box.

    The bounding box is defined by minimum/maximum latitude and longitude.
    Points are returned when their geometry intersects the envelope.

    :param min_lat: Minimum latitude (south bound).
    :type min_lat: float
    :param max_lat: Maximum latitude (north bound).
    :type max_lat: float
    :param min_lon: Minimum longitude (west bound).
    :type min_lon: float
    :param max_lon: Maximum longitude (east bound).
    :type max_lon: float
    :param db: Database session dependency.
    :type db: Session
    :returns: List of points inside/intersecting the bounding box.
    :rtype: list[ExamplePointModel]
    :raises fastapi.HTTPException: If bounds are invalid.
    """
    if min_lat > max_lat:
        raise HTTPException(status_code=422, detail="min_lat must be <= max_lat")
    if min_lon > max_lon:
        raise HTTPException(status_code=422, detail="min_lon must be <= max_lon")

    return get_example_points_in_bbox(
        db=db,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
    )
