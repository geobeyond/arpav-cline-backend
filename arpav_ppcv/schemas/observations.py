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
from sqlalchemy.orm import relationship as sla_relationship

from . import (
    base,
    fields,
    static,
)
from ..config import get_translations

if TYPE_CHECKING:
    import babel

    from ..config import ArpavPpcvSettings
    from .climaticindicators import ClimaticIndicator
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


# FIXME: Remove this for ObservationStation
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


# FIXME: Replace this with ObservationStation
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
    monthly_climatic_indicators: list["ClimaticIndicator"] = sqlmodel.Relationship(
        sa_relationship_kwargs={
            "primaryjoin": (
                "and_(Station.id == MonthlyMeasurement.station_id, "
                "ClimaticIndicator.id == MonthlyMeasurement.climatic_indicator_id)"
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
    seasonal_climatic_indicators: list["ClimaticIndicator"] = sqlmodel.Relationship(
        sa_relationship_kwargs={
            "primaryjoin": (
                "and_(Station.id == SeasonalMeasurement.station_id, "
                "ClimaticIndicator.id == SeasonalMeasurement.climatic_indicator_id)"
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
    yearly_climatic_indicators: list["ClimaticIndicator"] = sqlmodel.Relationship(
        sa_relationship_kwargs={
            "primaryjoin": (
                "and_(Station.id == YearlyMeasurement.station_id, "
                "ClimaticIndicator.id == YearlyMeasurement.climatic_indicator_id)"
            ),
            "secondary": "yearlymeasurement",
            "viewonly": True,
        }
    )

    def __hash__(self):
        return hash(self.id)


# FIXME: Replace this with ObservationStation
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


# FIXME: Replace this with ObservationStation
class StationUpdate(sqlmodel.SQLModel):
    code: Optional[str] = None
    geom: Optional[geojson_pydantic.Point] = None
    altitude_m: Optional[float] = None
    name: Optional[str] = None
    type_: Optional[str] = None
    active_since: Optional[dt.date] = None
    active_until: Optional[dt.date] = None


# # # TODO: Replace this with climatic_indicator
# class VariableBase(sqlmodel.SQLModel):
#     id: pydantic.UUID4 = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
#     name: str = sqlmodel.Field(unique=True)
#     display_name_english: Optional[str] = None
#     display_name_italian: Optional[str] = None
#     description_english: Optional[str] = None
#     description_italian: Optional[str] = None
#     unit_english: Optional[str] = None
#     unit_italian: Optional[str] = None
#
#
# # # TODO: Replace this with climatic_indicator
# class Variable(VariableBase, table=True):
#     related_coverage_configurations: list[
#         "coverages.CoverageConfiguration"
#     ] = sqlmodel.Relationship(back_populates="related_observation_variable")
#     monthly_measurements: list["MonthlyMeasurement"] = sqlmodel.Relationship(
#         back_populates="variable",
#         sa_relationship_kwargs={
#             # ORM relationship config, which explicitly includes the
#             # `delete` and `delete-orphan` options because we want the ORM
#             # to try to delete monthly measurements when their related variable
#             # is deleted
#             "cascade": "all, delete-orphan",
#             # expect that the RDBMS handles cascading deletes
#             "passive_deletes": True,
#         },
#     )
#     seasonal_measurements: list["SeasonalMeasurement"] = sqlmodel.Relationship(
#         back_populates="variable",
#         sa_relationship_kwargs={
#             # ORM relationship config, which explicitly includes the
#             # `delete` and `delete-orphan` options because we want the ORM
#             # to try to delete seasonal measurements when their related variable
#             # is deleted
#             "cascade": "all, delete-orphan",
#             # expect that the RDBMS handles cascading deletes
#             "passive_deletes": True,
#         },
#     )
#     yearly_measurements: list["YearlyMeasurement"] = sqlmodel.Relationship(
#         back_populates="variable",
#         sa_relationship_kwargs={
#             # ORM relationship config, which explicitly includes the
#             # `delete` and `delete-orphan` options because we want the ORM
#             # to try to delete yearly measurements when their related variable
#             # is deleted
#             "cascade": "all, delete-orphan",
#             # expect that the RDBMS handles cascading deletes
#             "passive_deletes": True,
#         },
#     )
#
#     def __hash__(self):
#         return hash(self.id)
#
#
# # TODO: Replace this with climatic_indicator
# class VariableCreate(sqlmodel.SQLModel):
#     name: str
#     display_name_english: Optional[str] = None
#     display_name_italian: Optional[str] = None
#     description_english: Optional[str] = None
#     description_italian: Optional[str] = None
#     unit_english: Optional[str] = None
#     unit_italian: Optional[str] = None
#
#
# # TODO: Replace this with climatic_indicator
# class VariableUpdate(sqlmodel.SQLModel):
#     name: Optional[str] = None
#     display_name_english: Optional[str] = None
#     display_name_italian: Optional[str] = None
#     description_english: Optional[str] = None
#     description_italian: Optional[str] = None
#     unit_english: Optional[str] = None
#     unit_italian: Optional[str] = None


# FIXME: Replace this with ObservationMeasurement
class MonthlyMeasurementBase(sqlmodel.SQLModel):
    value: float
    date: dt.date


# FIXME: Replace this with ObservationMeasurement
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
                "climatic_indicator_id",
            ],
            [
                "climaticindicator.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete a monthly measurement if its related climatic_indicator is deleted
        ),
    )
    id: pydantic.UUID4 = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    station_id: pydantic.UUID4
    climatic_indicator_id: int

    station: Station = sqlmodel.Relationship(
        back_populates="monthly_measurements",
        sa_relationship_kwargs={
            # retrieve the related resource immediately, by means of a SQL JOIN - this
            # is instead of the default lazy behavior of only retrieving related
            # records when they are accessed by the ORM
            "lazy": "joined",
        },
    )


# FIXME: Replace this with ObservationMeasurement
class MonthlyMeasurementCreate(sqlmodel.SQLModel):
    station_id: pydantic.UUID4
    climatic_indicator_id: int
    value: float
    date: dt.date


# FIXME: Replace this with ObservationMeasurement
class MonthlyMeasurementUpdate(sqlmodel.SQLModel):
    value: Optional[float] = None
    date: Optional[dt.date] = None


# FIXME: Replace this with ObservationMeasurement
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
                "climatic_indicator_id",
            ],
            [
                "climaticindicator.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete a measurement if its related climatic_indicator is deleted
        ),
    )
    id: pydantic.UUID4 = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    station_id: pydantic.UUID4
    climatic_indicator_id: int
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


# FIXME: Replace this with ObservationMeasurement
class SeasonalMeasurementCreate(sqlmodel.SQLModel):
    station_id: pydantic.UUID4
    climatic_indicator_id: int
    value: float
    year: int
    season: base.Season


# FIXME: Replace this with ObservationMeasurement
class SeasonalMeasurementUpdate(sqlmodel.SQLModel):
    value: Optional[float] = None
    year: Optional[int] = None
    season: Optional[base.Season] = None


# FIXME: Replace this with ObservationMeasurement
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
                "climatic_indicator_id",
            ],
            [
                "climaticindicator.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete a measurement if its climatic_indicator station is deleted
        ),
    )
    id: pydantic.UUID4 = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    station_id: pydantic.UUID4
    climatic_indicator_id: int
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


# FIXME: Replace this with ObservationMeasurement
class YearlyMeasurementCreate(sqlmodel.SQLModel):
    station_id: pydantic.UUID4
    climatic_indicator_id: int
    value: float
    year: int


# FIXME: Replace this with ObservationMeasurement
class YearlyMeasurementUpdate(sqlmodel.SQLModel):
    value: Optional[float] = None
    year: Optional[int] = None


class ObservationStationClimaticIndicatorLink(sqlmodel.SQLModel, table=True):
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            [
                "observation_station_id",
            ],
            [
                "observationstation.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related observation station gets deleted
        ),
        sqlalchemy.ForeignKeyConstraint(
            [
                "climatic_indicator_id",
            ],
            [
                "climaticindicator.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related climatic indicator gets deleted
        ),
    )
    observation_station_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )
    climatic_indicator_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )


class ObservationStation(sqlmodel.SQLModel, table=True):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    name: str = ""
    managed_by: static.ObservationStationManager
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
    altitude_m: Optional[float] = sqlmodel.Field(default=None)
    active_since: Optional[dt.date] = None
    active_until: Optional[dt.date] = None

    measurements: list["ObservationMeasurement"] = sqlmodel.Relationship(
        back_populates="observation_station",
        sa_relationship_kwargs={
            # ORM relationship config, which explicitly includes the
            # `delete` and `delete-orphan` options because we want the ORM
            # to try to delete observation measurements when their related station
            # is deleted
            "cascade": "all, delete-orphan",
            # expect that the RDBMS handles cascading deletes
            "passive_deletes": True,
        },
    )
    # this relationship is defined by using the fallback sqlalchemy relationship
    # method - this is in order to be able to specify the link table as a
    # string (a facility that sqlalchemy offers, but not sqlmodel) and avoid circular
    # dependencies which would otherwise occur if using sqlmodel's `link_model`
    # approach
    climatic_indicators: list["ClimaticIndicator"] = sqlmodel.Relationship(
        sa_relationship=sla_relationship(
            secondary="observationstationclimaticindicatorlink",
            back_populates="observation_stations",
        )
    )

    @staticmethod
    def get_display_name(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation station")

    @staticmethod
    def get_description(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation station description")


class ObservationStationCreate(sqlmodel.SQLModel):
    name: Optional[str] = ""
    managed_by: static.ObservationStationManager
    geom: geojson_pydantic.Point
    code: str
    altitude_m: Optional[float] = None
    active_since: Optional[dt.date] = None
    active_until: Optional[dt.date] = None
    climatic_indicators: Optional[list[int]] = None

    def __hash__(self):
        return hash(
            "".join(
                (
                    self.name,
                    self.managed_by,
                    self.geom.model_dump_json(),
                    self.code,
                    str(self.altitude_m) or "",
                    self.active_since.isoformat()
                    if self.active_since is not None
                    else "",
                    self.active_until.isoformat()
                    if self.active_until is not None
                    else "",
                )
            )
        )


class ObservationStationUpdate(sqlmodel.SQLModel):
    name: Optional[str] = None
    managed_by: Optional[static.ObservationStationManager] = None
    geom: Optional[geojson_pydantic.Point] = None
    code: Optional[str] = None
    altitude_m: Optional[float] = None
    active_since: Optional[dt.date] = None
    active_until: Optional[dt.date] = None
    climatic_indicators: Optional[list[int]] = None


class ObservationMeasurement(sqlmodel.SQLModel, table=True):
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            [
                "observation_station_id",
            ],
            [
                "observationstation.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete a measurement if its related station is deleted
        ),
        sqlalchemy.ForeignKeyConstraint(
            [
                "climatic_indicator_id",
            ],
            [
                "climaticindicator.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete a measurement if its climatic_indicator station is deleted
        ),
    )
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    value: float
    date: dt.date
    measurement_aggregation_type: static.MeasurementAggregationType
    climatic_indicator_id: int
    observation_station_id: int

    observation_station: ObservationStation = sqlmodel.Relationship(
        back_populates="measurements",
        sa_relationship_kwargs={
            # retrieve the related resource immediately, by means of a SQL JOIN - this
            # is instead of the default lazy behavior of only retrieving related
            # records when they are accessed by the ORM
            "lazy": "joined",
        },
    )
    climatic_indicator: "ClimaticIndicator" = sqlmodel.Relationship(
        back_populates="measurements",
        sa_relationship_kwargs={
            # retrieve the related resource immediately, by means of a SQL JOIN - this
            # is instead of the default lazy behavior of only retrieving related
            # records when they are accessed by the ORM
            "lazy": "joined",
        },
    )


class ObservationMeasurementCreate(sqlmodel.SQLModel):
    value: float
    date: dt.date
    measurement_aggregation_type: static.MeasurementAggregationType
    observation_station_id: int
    climatic_indicator_id: int

    @pydantic.computed_field
    @property
    def identifier(self) -> str:
        return "-".join((str(self.climatic_indicator_id), self.date.strftime("%Y%m%D")))


class ObservationMeasurementUpdate(sqlmodel.SQLModel):
    value: Optional[float] = None
    date: Optional[dt.date] = None
    measurement_aggregation_type: Optional[static.MeasurementAggregationType] = None
    observation_station_id: Optional[pydantic.UUID4] = None
    climatic_indicator_id: Optional[int] = None


class ObservationSeriesConfiguration(sqlmodel.SQLModel, table=True):
    """Configuration for observation series."""

    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    climatic_indicator_id: Optional[int] = sqlmodel.Field(
        default=None, foreign_key="climaticindicator.id"
    )
    measurement_aggregation_type: static.MeasurementAggregationType
    station_managers: list[static.ObservationStationManager] = sqlmodel.Field(
        default=list,
        sa_column=sqlalchemy.Column(
            sqlmodel.ARRAY(sqlmodel.Enum(static.ObservationStationManager))
        ),
    )

    climatic_indicator: "ClimaticIndicator" = sqlmodel.Relationship(
        back_populates="observation_series_configurations"
    )

    forecast_coverage_configuration_links: list[
        "coverages.ForecastCoverageConfigurationObservationSeriesConfigurationLink"
    ] = sqlmodel.Relationship(back_populates="observation_series_configuration")
    historical_coverage_configuration_links: list[
        "coverages.HistoricalCoverageConfigurationObservationSeriesConfigurationLink"
    ] = sqlmodel.Relationship(back_populates="observation_series_configuration")

    @pydantic.computed_field
    @property
    def identifier(self) -> str:
        return "{climatic_indicator}-{station_managers}-{measurement_aggregation_type}".format(
            climatic_indicator=self.climatic_indicator.identifier,
            station_managers=":".join(
                manager.value for manager in self.station_managers
            ),
            measurement_aggregation_type=self.measurement_aggregation_type,
        )

    def get_observation_stations_vector_tile_layer_url(
        self, settings: "ArpavPpcvSettings"
    ) -> Optional[str]:
        return "/".join(
            (
                settings.vector_tile_server_base_url,
                self.climatic_indicator.identifier.replace("-", "_"),
                "{z}/{x}/{y}",
            )
        )


class ObservationSeriesConfigurationCreate(sqlmodel.SQLModel):
    climatic_indicator_id: int
    measurement_aggregation_type: static.MeasurementAggregationType
    station_managers: list[static.ObservationStationManager]


class ObservationSeriesConfigurationUpdate(sqlmodel.SQLModel):
    climatic_indicator_id: Optional[int] = None
    measurement_aggregation_type: Optional[static.MeasurementAggregationType] = None
    station_managers: Optional[list[static.ObservationStationManager]] = None


class ClimaticIndicatorObservationName(sqlmodel.SQLModel, table=True):
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            [
                "climatic_indicator_id",
            ],
            [
                "climaticindicator.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all names if the related climatic_indicator gets deleted
        ),
    )

    climatic_indicator_id: Optional[int] = sqlmodel.Field(
        default=None,
        primary_key=True,
    )
    station_manager: static.ObservationStationManager = sqlmodel.Field(
        default=None,
        primary_key=True,
    )
    indicator_observation_name: str

    climatic_indicator: "ClimaticIndicator" = sqlmodel.Relationship(
        back_populates="observation_names"
    )
