import dataclasses
import datetime as dt
import enum
import fnmatch
import urllib.parse

import shapely


@dataclasses.dataclass
class _ForecastTemporalPeriodMetadata:
    name: str
    code: str


@dataclasses.dataclass
class _ForecastYearPeriodMetadata:
    name: str
    code: str


@dataclasses.dataclass
class _ForecastScenarioMetadata:
    name: str
    code: str


class ForecastTemporalPeriod(enum.Enum):
    TW1 = _ForecastTemporalPeriodMetadata(name="2021 - 2050", code="tw1")
    TW2 = _ForecastTemporalPeriodMetadata(name="2071 - 2100", code="tw2")


class ForecastYearPeriod(enum.Enum):
    WINTER = _ForecastYearPeriodMetadata(name="Winter", code="DJF")
    SPRING = _ForecastYearPeriodMetadata(name="Spring", code="MAM")
    SUMMER = _ForecastYearPeriodMetadata(name="Summer", code="JJA")
    AUTUMN = _ForecastYearPeriodMetadata(name="Autumn", code="SON")
    ANNUAL = _ForecastYearPeriodMetadata(name="Annual", code="*")


class ForecastScenario(enum.Enum):
    RCP26 = _ForecastScenarioMetadata(name="RCP26", code="rcp26")
    RCP45 = _ForecastScenarioMetadata(name="RCP45", code="rcp45")
    RCP85 = _ForecastScenarioMetadata(name="RCP85", code="rcp85")


class AveragingPeriod(enum.Enum):
    YEAR = "year"
    THIRTY_YEAR = "thirty-year"


@dataclasses.dataclass
class ThreddsDatasetDescriptionVariable:
    name: str
    description: str
    units: str


@dataclasses.dataclass
class ThreddsDatasetDescriptionTemporalBounds:
    start: dt.datetime
    end: dt.datetime


@dataclasses.dataclass
class ThreddsDatasetDescription:
    variables: list[ThreddsDatasetDescriptionVariable]
    spatial_bounds: shapely.Polygon
    temporal_bounds: ThreddsDatasetDescriptionTemporalBounds


@dataclasses.dataclass
class ThreddsClientService:
    name: str
    service_type: str
    base: str


@dataclasses.dataclass
class ThreddsClientPublicDataset:
    name: str
    id: str
    url_path: str


@dataclasses.dataclass
class ThreddsClientCatalogRef:
    title: str
    id: str
    name: str
    href: str


@dataclasses.dataclass
class ThreddsClientDataset:
    name: str
    properties: dict[str, str]
    metadata: dict[str, str]
    public_datasets: dict[str, ThreddsClientPublicDataset]
    catalog_refs: dict[str, ThreddsClientCatalogRef]


@dataclasses.dataclass
class ThreddsClientCatalog:
    url: urllib.parse.ParseResult
    services: dict[str, ThreddsClientService]
    dataset: ThreddsClientDataset

    def build_dataset_download_url(self, dataset_id: str) -> str:
        dataset = self.dataset.public_datasets[dataset_id]
        url_pattern = "{scheme}://{host}/{service_base}/{dataset_path}"
        return url_pattern.format(
            scheme=self.url.scheme,
            host=self.url.netloc,
            service_base=self.services["HTTPServer"].base.strip("/"),
            dataset_path=dataset.url_path.strip("/"),
        )

    def get_public_datasets(
        self, wildcard_pattern: str = "*"
    ) -> dict[str, ThreddsClientPublicDataset]:
        relevant_ids = fnmatch.filter(
            self.dataset.public_datasets.keys(), wildcard_pattern
        )
        return {id_: self.dataset.public_datasets[id_] for id_ in relevant_ids}
