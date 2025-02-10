import datetime as dt
import uuid
from typing import (
    Optional,
    TYPE_CHECKING,
)

import geojson_pydantic
import geoalchemy2
import pydantic
import sqlalchemy
import sqlmodel

from . import fields
from . import base

if TYPE_CHECKING:
    from . import coverages

    def get_season(self, value: str):
        if value.lower() in ("djf",):
            result = self.WINTER
        elif value.lower() in ("mam",):
            result = self.SPRING
        elif value.lower() in ("jja",):
            result = self.SUMMER
        elif value.lower() in ("son",):
            result = self.AUTUMN
        else:
            result = []
        return result


class StationBase(sqlmodel.SQLModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    id: pydantic.UUID4 = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    geom: fields.WkbElement = sqlmodel.Field(
        sa_column=sqlalchemy.Column(
            geoalchemy2.Geometry(
                srid=4326,
                geometry_type="POINT",
                spatial_index=True,
            )
        )
    )
    code: str = sqlmodel.Field(unique=True)
    active_since: Optional[dt.date] = None
    active_until: Optional[dt.date] = None


class Station(StationBase, table=True):
    altitude_m: Optional[float] = sqlmodel.Field(default=None)
    name: str = ""
    type_: str = ""

    monthly_measurements: list["MonthlyMeasurement"] = sqlmodel.Relationship(
        back_populates="station",
        sa_relationship_kwargs={
            # ORM relationship config, which explicitly includes the
            # `delete` and `delete-orphan` options because we want the ORM
            # to try to delete monthly measurements when their related station
            # is deleted
            "cascade": "all, delete-orphan",
            # expect that the RDBMS handles cascading deletes
            "passive_deletes": True,
        },
    )
    monthly_variables: list["Variable"] = sqlmodel.Relationship(
        sa_relationship_kwargs={
            "primaryjoin": (
                "and_(Station.id == MonthlyMeasurement.station_id, "
                "Variable.id == MonthlyMeasurement.variable_id)"
            ),
            "secondary": "monthlymeasurement",
            "viewonly": True,
        }
    )
    seasonal_measurements: list["SeasonalMeasurement"] = sqlmodel.Relationship(
        back_populates="station",
        sa_relationship_kwargs={
            # ORM relationship config, which explicitly includes the
            # `delete` and `delete-orphan` options because we want the ORM
            # to try to delete seasonal measurements when their related station
            # is deleted
            "cascade": "all, delete-orphan",
            # expect that the RDBMS handles cascading deletes
            "passive_deletes": True,
        },
    )
    seasonal_variables: list["Variable"] = sqlmodel.Relationship(
        sa_relationship_kwargs={
            "primaryjoin": (
                "and_(Station.id == SeasonalMeasurement.station_id, "
                "Variable.id == SeasonalMeasurement.variable_id)"
            ),
            "secondary": "seasonalmeasurement",
            "viewonly": True,
        }
    )
    yearly_measurements: list["YearlyMeasurement"] = sqlmodel.Relationship(
        back_populates="station",
        sa_relationship_kwargs={
            # ORM relationship config, which explicitly includes the
            # `delete` and `delete-orphan` options because we want the ORM
            # to try to delete yearly measurements when their related station
            # is deleted
            "cascade": "all, delete-orphan",
            # expect that the RDBMS handles cascading deletes
            "passive_deletes": True,
        },
    )
    yearly_variables: list["Variable"] = sqlmodel.Relationship(
        sa_relationship_kwargs={
            "primaryjoin": (
                "and_(Station.id == YearlyMeasurement.station_id, "
                "Variable.id == YearlyMeasurement.variable_id)"
            ),
            "secondary": "yearlymeasurement",
            "viewonly": True,
        }
    )

    def __hash__(self):
        return hash(self.id)


class StationCreate(sqlmodel.SQLModel):
    code: str
    geom: geojson_pydantic.Point
    altitude_m: Optional[float] = None
    name: Optional[str] = ""
    type_: Optional[str] = ""
    active_since: Optional[dt.date] = None
    active_until: Optional[dt.date] = None

    def __hash__(self):
        return hash(
            "".join(
                (
                    self.code,
                    self.geom.model_dump_json(),
                    str(self.altitude_m) or "",
                    self.name,
                    self.type_,
                    self.active_since.isoformat()
                    if self.active_since is not None
                    else "",
                    self.active_until.isoformat()
                    if self.active_until is not None
                    else "",
                )
            )
        )


class StationUpdate(sqlmodel.SQLModel):
    code: Optional[str] = None
    geom: Optional[geojson_pydantic.Point] = None
    altitude_m: Optional[float] = None
    name: Optional[str] = None
    type_: Optional[str] = None
    active_since: Optional[dt.date] = None
    active_until: Optional[dt.date] = None


class VariableBase(sqlmodel.SQLModel):
    id: pydantic.UUID4 = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = sqlmodel.Field(unique=True)
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None
    unit_english: Optional[str] = None
    unit_italian: Optional[str] = None


class Variable(VariableBase, table=True):
    related_coverage_configurations: list[
        "coverages.CoverageConfiguration"
    ] = sqlmodel.Relationship(back_populates="related_observation_variable")
    monthly_measurements: list["MonthlyMeasurement"] = sqlmodel.Relationship(
        back_populates="variable",
        sa_relationship_kwargs={
            # ORM relationship config, which explicitly includes the
            # `delete` and `delete-orphan` options because we want the ORM
            # to try to delete monthly measurements when their related variable
            # is deleted
            "cascade": "all, delete-orphan",
            # expect that the RDBMS handles cascading deletes
            "passive_deletes": True,
        },
    )
    seasonal_measurements: list["SeasonalMeasurement"] = sqlmodel.Relationship(
        back_populates="variable",
        sa_relationship_kwargs={
            # ORM relationship config, which explicitly includes the
            # `delete` and `delete-orphan` options because we want the ORM
            # to try to delete seasonal measurements when their related variable
            # is deleted
            "cascade": "all, delete-orphan",
            # expect that the RDBMS handles cascading deletes
            "passive_deletes": True,
        },
    )
    yearly_measurements: list["YearlyMeasurement"] = sqlmodel.Relationship(
        back_populates="variable",
        sa_relationship_kwargs={
            # ORM relationship config, which explicitly includes the
            # `delete` and `delete-orphan` options because we want the ORM
            # to try to delete yearly measurements when their related variable
            # is deleted
            "cascade": "all, delete-orphan",
            # expect that the RDBMS handles cascading deletes
            "passive_deletes": True,
        },
    )

    def __hash__(self):
        return hash(self.id)


class VariableCreate(sqlmodel.SQLModel):
    name: str
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None
    unit_english: Optional[str] = None
    unit_italian: Optional[str] = None


class VariableUpdate(sqlmodel.SQLModel):
    name: Optional[str] = None
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None
    unit_english: Optional[str] = None
    unit_italian: Optional[str] = None


class MonthlyMeasurementBase(sqlmodel.SQLModel):
    value: float
    date: dt.date


class MonthlyMeasurement(MonthlyMeasurementBase, table=True):
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            [
                "station_id",
            ],
            [
                "station.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete a monthly measurement if its related station is deleted
        ),
        sqlalchemy.ForeignKeyConstraint(
            [
                "variable_id",
            ],
            [
                "variable.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete a monthly measurement if its related station is deleted
        ),
    )
    id: pydantic.UUID4 = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    station_id: pydantic.UUID4
    variable_id: pydantic.UUID4

    station: Station = sqlmodel.Relationship(
        back_populates="monthly_measurements",
        sa_relationship_kwargs={
            # retrieve the related resource immediately, by means of a SQL JOIN - this
            # is instead of the default lazy behavior of only retrieving related
            # records when they are accessed by the ORM
            "lazy": "joined",
        },
    )
    variable: Variable = sqlmodel.Relationship(
        back_populates="monthly_measurements",
        sa_relationship_kwargs={
            # retrieve the related resource immediately, by means of a SQL JOIN - this
            # is instead of the default lazy behavior of only retrieving related
            # records when they are accessed by the ORM
            "lazy": "joined",
        },
    )


class MonthlyMeasurementCreate(sqlmodel.SQLModel):
    station_id: pydantic.UUID4
    variable_id: pydantic.UUID4
    value: float
    date: dt.date


class MonthlyMeasurementUpdate(sqlmodel.SQLModel):
    value: Optional[float] = None
    date: Optional[dt.date] = None


class SeasonalMeasurement(sqlmodel.SQLModel, table=True):
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            [
                "station_id",
            ],
            [
                "station.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete a measurement if its related station is deleted
        ),
        sqlalchemy.ForeignKeyConstraint(
            [
                "variable_id",
            ],
            [
                "variable.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete a measurement if its related station is deleted
        ),
    )
    id: pydantic.UUID4 = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    station_id: pydantic.UUID4
    variable_id: pydantic.UUID4
    value: float
    year: int
    season: base.Season

    station: Station = sqlmodel.Relationship(
        back_populates="seasonal_measurements",
        sa_relationship_kwargs={
            # retrieve the related resource immediately, by means of a SQL JOIN - this
            # is instead of the default lazy behavior of only retrieving related
            # records when they are accessed by the ORM
            "lazy": "joined",
        },
    )
    variable: Variable = sqlmodel.Relationship(
        back_populates="seasonal_measurements",
        sa_relationship_kwargs={
            # retrieve the related resource immediately, by means of a SQL JOIN - this
            # is instead of the default lazy behavior of only retrieving related
            # records when they are accessed by the ORM
            "lazy": "joined",
        },
    )


class SeasonalMeasurementCreate(sqlmodel.SQLModel):
    station_id: pydantic.UUID4
    variable_id: pydantic.UUID4
    value: float
    year: int
    season: base.Season


class SeasonalMeasurementUpdate(sqlmodel.SQLModel):
    value: Optional[float] = None
    year: Optional[int] = None
    season: Optional[base.Season] = None


class YearlyMeasurement(sqlmodel.SQLModel, table=True):
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            [
                "station_id",
            ],
            [
                "station.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete a measurement if its related station is deleted
        ),
        sqlalchemy.ForeignKeyConstraint(
            [
                "variable_id",
            ],
            [
                "variable.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete a measurement if its related station is deleted
        ),
    )
    id: pydantic.UUID4 = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    station_id: pydantic.UUID4
    variable_id: pydantic.UUID4
    value: float
    year: int

    station: Station = sqlmodel.Relationship(
        back_populates="yearly_measurements",
        sa_relationship_kwargs={
            # retrieve the related resource immediately, by means of a SQL JOIN - this
            # is instead of the default lazy behavior of only retrieving related
            # records when they are accessed by the ORM
            "lazy": "joined",
        },
    )
    variable: Variable = sqlmodel.Relationship(
        back_populates="yearly_measurements",
        sa_relationship_kwargs={
            # retrieve the related resource immediately, by means of a SQL JOIN - this
            # is instead of the default lazy behavior of only retrieving related
            # records when they are accessed by the ORM
            "lazy": "joined",
        },
    )


class YearlyMeasurementCreate(sqlmodel.SQLModel):
    station_id: pydantic.UUID4
    variable_id: pydantic.UUID4
    value: float
    year: int


class YearlyMeasurementUpdate(sqlmodel.SQLModel):
    value: Optional[float] = None
    year: Optional[int] = None
