from typing import (
    Annotated,
    ClassVar,
    Final,
    Optional,
)

import pydantic
import sqlmodel

from . import static

_name_description_text: Final[str] = (
    "Parameter name. Only alphanumeric characters and the underscore are allowed. "
    "Example: my_indicator"
)


class ClimaticIndicator(sqlmodel.SQLModel, table=True):
    identifier_pattern: ClassVar[str] = "{name}-{measure_type}-{aggregation_period}"

    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    name: str
    measure_type: static.MeasureType
    aggregation_period: static.AggregationPeriod
    display_name_english: str = sqlmodel.Field(default="")
    display_name_italian: str = sqlmodel.Field(default="")
    description_english: str = sqlmodel.Field(default="")
    description_italian: str = sqlmodel.Field(default="")
    unit_english: str = sqlmodel.Field(default="")
    unit_italian: str = sqlmodel.Field(default="")
    palette: str
    color_scale_min: float
    color_scale_max: float
    data_precision: int = sqlmodel.Field(default=0)
    sort_order: int = sqlmodel.Field(default=0)

    @pydantic.computed_field
    @property
    def identifier(self) -> str:
        return self.identifier_pattern.format(
            name=self.name,
            measure_type=self.measure_type.value.lower(),
            aggregation_period=self.aggregation_period.value.lower(),
        )


class ClimaticIndicatorCreate(sqlmodel.SQLModel):
    name: Annotated[
        str,
        pydantic.Field(pattern=static.NAME_PATTERN, description=_name_description_text),
    ]
    measure_type: static.MeasureType
    aggregation_period: static.AggregationPeriod
    display_name_english: str = sqlmodel.Field(default="")
    display_name_italian: str = sqlmodel.Field(default="")
    description_english: str = sqlmodel.Field(default="")
    description_italian: str = sqlmodel.Field(default="")
    unit_english: str = sqlmodel.Field(default="")
    unit_italian: str = sqlmodel.Field(default="")
    palette: str
    color_scale_min: float = 0.0
    color_scale_max: float = 0.0
    data_precision: int = sqlmodel.Field(default=0)
    sort_order: int = sqlmodel.Field(default=0)


class ClimaticIndicatorUpdate(sqlmodel.SQLModel):
    name: Annotated[
        Optional[str],
        pydantic.Field(pattern=static.NAME_PATTERN, description=_name_description_text),
    ] = None
    measure_type: Optional[static.MeasureType] = None
    aggregation_period: Optional[static.AggregationPeriod] = None
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None
    unit_english: Optional[str] = None
    unit_italian: Optional[str] = None
    palette: Optional[str] = None
    color_scale_min: Optional[float] = None
    color_scale_max: Optional[float] = None
    data_precision: Optional[int] = None
    sort_order: Optional[int] = None
