import logging
import uuid

import pydantic
from fastapi import Request

from ....schemas import (
    observations,
    static,
)
from ....schemas.base import Season
from .base import WebResourceList

logger = logging.getLogger(__name__)


class VariableReadEmbeddedInStationRead(pydantic.BaseModel):
    id: uuid.UUID
    name: str
    display_name_english: str
    display_name_italian: str


class StationReadListItem(observations.StationBase):
    url: pydantic.AnyHttpUrl
    monthly_variables: list[VariableReadEmbeddedInStationRead]
    seasonal_variables: list[VariableReadEmbeddedInStationRead]
    yearly_variables: list[VariableReadEmbeddedInStationRead]

    @classmethod
    def from_db_instance(
        cls,
        instance: observations.Station,
        request: Request,
    ) -> "StationReadListItem":
        url = request.url_for("get_station", **{"station_id": instance.id})
        return cls(
            **instance.model_dump(),
            monthly_variables=[
                VariableReadEmbeddedInStationRead(
                    **v.model_dump(
                        exclude={"display_name_english", "display_name_italian"}
                    ),
                    display_name_english=v.display_name_english or v.name,
                    display_name_italian=v.display_name_italian or v.name,
                )
                for v in instance.monthly_variables
            ],
            seasonal_variables=[
                VariableReadEmbeddedInStationRead(
                    **v.model_dump(
                        exclude={"display_name_english", "display_name_italian"}
                    ),
                    display_name_english=v.display_name_english or v.name,
                    display_name_italian=v.display_name_italian or v.name,
                )
                for v in instance.seasonal_variables
            ],
            yearly_variables=[
                VariableReadEmbeddedInStationRead(
                    **v.model_dump(
                        exclude={"display_name_english", "display_name_italian"}
                    ),
                    display_name_english=v.display_name_english or v.name,
                    display_name_italian=v.display_name_italian or v.name,
                )
                for v in instance.yearly_variables
            ],
            url=str(url),
        )


class ObservationStationReadListItem(pydantic.BaseModel):
    url: pydantic.AnyHttpUrl
    identifier: str
    name: str
    owner: static.ObservationStationOwner

    @classmethod
    def from_db_instance(
        cls, instance: observations.ObservationStation, request: Request
    ) -> "ObservationStationReadListItem":
        return cls(
            **instance.model_dump(),
            url=request.url_for("get_station", **{"station_id": instance.id}),
        )


class MonthlyMeasurementReadListItem(observations.MonthlyMeasurementBase):
    url: pydantic.AnyHttpUrl
    climatic_indicator_identifier: str
    station_code: str

    @classmethod
    def from_db_instance(
        cls,
        instance: observations.MonthlyMeasurement,
        request: Request,
    ) -> "MonthlyMeasurementReadListItem":
        return cls(
            **instance.model_dump(),
            climatic_indicator_identifier=instance.climatic_indicator.identifier,
            station_code=instance.station.code,
            url=str(
                request.url_for(
                    "get_monthly_measurement", monthly_measurement_id=instance.id
                )
            ),
        )


class SeasonalMeasurementReadListItem(pydantic.BaseModel):
    url: pydantic.AnyHttpUrl
    climatic_indicator_identifier: str
    station_code: str
    year: int
    season: Season
    value: float

    @classmethod
    def from_db_instance(
        cls,
        instance: observations.SeasonalMeasurement,
        request: Request,
    ) -> "SeasonalMeasurementReadListItem":
        return cls(
            **instance.model_dump(),
            climatic_indicator_identifier=instance.climatic_indicator.identifier,
            station_code=instance.station.code,
            url=str(
                request.url_for(
                    "get_seasonal_measurement", seasonal_measurement_id=instance.id
                )
            ),
        )


class YearlyMeasurementReadListItem(pydantic.BaseModel):
    url: pydantic.AnyHttpUrl
    climatic_indicator_identifier: str
    station_code: str
    year: int
    value: float

    @classmethod
    def from_db_instance(
        cls,
        instance: observations.YearlyMeasurement,
        request: Request,
    ) -> "YearlyMeasurementReadListItem":
        return cls(
            **instance.model_dump(),
            climatic_indicator_identifier=instance.climatic_indicator.identifier,
            station_code=instance.station.code,
            url=str(
                request.url_for(
                    "get_yearly_measurement", yearly_measurement_id=instance.id
                )
            ),
        )


# class StationList(WebResourceList):
#     items: list[StationReadListItem]
#     list_item_type = StationReadListItem
#     path_operation_name = "list_stations"


class ObservationStationList(WebResourceList):
    items: list[ObservationStationReadListItem]
    list_item_type = ObservationStationReadListItem
    path_operation_name = "list_stations"


class MonthlyMeasurementList(WebResourceList):
    items: list[MonthlyMeasurementReadListItem]
    list_item_type = MonthlyMeasurementReadListItem
    path_operation_name = "list_monthly_measurements"


class SeasonalMeasurementList(WebResourceList):
    items: list[SeasonalMeasurementReadListItem]
    list_item_type = SeasonalMeasurementReadListItem
    path_operation_name = "list_seasonal_measurements"


class YearlyMeasurementList(WebResourceList):
    items: list[YearlyMeasurementReadListItem]
    list_item_type = YearlyMeasurementReadListItem
    path_operation_name = "list_yearly_measurements"
