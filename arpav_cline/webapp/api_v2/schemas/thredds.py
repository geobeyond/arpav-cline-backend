import pydantic

from .base import WebResourceList


class ForecastModelScenario(pydantic.BaseModel):
    name: str
    code: str


class ThreddsDatasetConfiguration(pydantic.BaseModel):
    identifier: str
    dataset_id_pattern: str
    unit: str | None = None
    palette: str
    range: list[float]
    allowed_values: dict[str, list[str]] | None = None


class ThreddsDatasetConfigurationList(WebResourceList):
    items: list[ThreddsDatasetConfiguration]


class ThreddsDatasetConfigurationIdentifierList(WebResourceList):
    items: list[str]


class ForecastModelScenarioList(WebResourceList):
    items: list[ForecastModelScenario]
