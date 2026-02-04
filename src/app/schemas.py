"""
Pydantic schemas for geospatial point data.

This module defines the request and response schemas for the points API,
handling serialisation between WKT strings and PostGIS geometry types.
"""

from datetime import datetime
from typing import Optional

from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from pydantic import BaseModel, Field, field_validator


class ExamplePointCreate(BaseModel):
    """
    Schema for creating a new geospatial point.

    :cvar geom: WKT representation of a Point geometry.
    :cvar value: Numeric value to associate with the point.
    """

    geom: str = Field(
        ..., description="WKT Point geometry", examples=["POINT(51.51999 -0.10684)"]
    )
    value: float = Field(
        ..., description="Numeric value for this point", examples=[42.5]
    )


class ExamplePointModel(BaseModel):
    """
    Schema for reading a geospatial point from the database.

    Handles conversion from PostGIS WKBElement to WKT string for JSON
    serialisation.

    :cvar id: Primary key identifier.
    :cvar created_at: Timestamp of record creation.
    :cvar geom: WKT representation of the Point geometry.
    :cvar value: Numeric value associated with the point.
    """

    id: int
    created_at: Optional[datetime]
    geom: str = Field(
        ..., description="WKT Point geometry", examples=["POINT(51.51999 -0.10684)"]
    )
    value: float = Field(
        ..., description="Numeric value for this point", examples=[42.5]
    )

    model_config = {"from_attributes": True}

    @field_validator("geom", mode="before")
    @classmethod
    def convert_wkb_to_wkt(cls, v):
        """
        Convert PostGIS WKBElement to WKT string.

        :param v: Geometry value, either WKBElement or string.
        :type v: WKBElement | str
        :returns: WKT string representation of the geometry.
        :rtype: str
        """
        if isinstance(v, WKBElement):
            return to_shape(v).wkt
        return v
