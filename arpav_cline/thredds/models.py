import dataclasses
import datetime as dt
import fnmatch
import logging
import urllib.parse

import babel
import shapely

from ..config import (
    ThreddsServerSettings,
)
from ..schemas import static
from ..schemas.coverages import (
    ForecastCoverageInternal,
    HistoricalCoverageInternal,
)

logger = logging.getLogger(__name__)


# @dataclasses.dataclass
# class _ForecastTemporalPeriodMetadata:
#     name: str
#     code: str
#
#
# @dataclasses.dataclass
# class _ForecastYearPeriodMetadata:
#     name: str
#     code: str
#
#
# @dataclasses.dataclass
# class _ForecastScenarioMetadata:
#     name: str
#     code: str
#
#
# class ForecastTemporalPeriod(enum.Enum):
#     TW1 = _ForecastTemporalPeriodMetadata(name="2021 - 2050", code="tw1")
#     TW2 = _ForecastTemporalPeriodMetadata(name="2071 - 2100", code="tw2")
#
#
# class ForecastYearPeriod(enum.Enum):
#     WINTER = _ForecastYearPeriodMetadata(name="Winter", code="DJF")
#     SPRING = _ForecastYearPeriodMetadata(name="Spring", code="MAM")
#     SUMMER = _ForecastYearPeriodMetadata(name="Summer", code="JJA")
#     AUTUMN = _ForecastYearPeriodMetadata(name="Autumn", code="SON")
#     ANNUAL = _ForecastYearPeriodMetadata(name="Annual", code="*")
#
#
# class ForecastScenario(enum.Enum):
#     RCP26 = _ForecastScenarioMetadata(name="RCP26", code="rcp26")
#     RCP45 = _ForecastScenarioMetadata(name="RCP45", code="rcp45")
#     RCP85 = _ForecastScenarioMetadata(name="RCP85", code="rcp85")
#
#
# class AveragingPeriod(enum.Enum):
#     YEAR = "year"
#     THIRTY_YEAR = "thirty-year"


@dataclasses.dataclass
class ThreddsDatasetDescriptionVariable:
    name: str
    description: str
    units: str


@dataclasses.dataclass
class ThreddsDatasetDescriptionTemporalBounds:
    start: dt.datetime | None
    end: dt.datetime | None


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


@dataclasses.dataclass(frozen=True)
class StaticCoverage:
    """This class provides static access to its properties.

    It exists in order to allow THREDDS-related code paths to run without
    needing a DB connection.
    """

    aggregation_period: static.AggregationPeriod
    climatic_indicator_name: str
    color_scale_min: float
    color_scale_max: float
    coverage_configuration_identifier: str
    coverage_identifier: str
    lower_uncertainty_identifier: str | None
    lower_uncertainty_ncss_url: str | None
    lower_uncertainy_netcdf_variable_name: str | None
    measure_type: static.MeasureType
    netcdf_variable_name: str | None
    ncss_url: str | None
    palette: str
    upper_uncertainty_identifier: str | None
    upper_uncertainty_ncss_url: str | None
    upper_uncertainy_netcdf_variable_name: str | None
    wms_base_url: str
    year_period: static.ObservationYearPeriod
    forecast_model_name: str | None = None
    forecast_model_name_translations: dict[babel.Locale, str]
    related_thredds_datasets: list["StaticCoverage"] = dataclasses.field(
        default_factory=list
    )
    scenario: static.ForecastScenario | None = None

    @classmethod
    def from_coverage(
        cls,
        cov: ForecastCoverageInternal | HistoricalCoverageInternal,
        settings: ThreddsServerSettings,
        related_covs: list[ForecastCoverageInternal] | None = None,
    ) -> "StaticCoverage":
        if (ncss_url := cov.get_thredds_ncss_url(settings)) is None:
            logger.warning("Could not find coverage's NCSS URL")
        if (netcdf_variable_name := cov.get_netcdf_main_dataset_name()) is None:
            logger.warning("Could not find coverage's NetCDF variable name")
        if (
            lower_uncert_nc_var := cov.get_netcdf_lower_uncertainty_main_dataset_name()
        ) is None:
            logger.info(
                f"Coverage {cov.identifier!r} does not specify a lower "
                f"uncertainty dataset"
            )
        if (
            upper_uncert_nc_var := cov.get_netcdf_upper_uncertainty_main_dataset_name()
        ) is None:
            logger.info(
                f"Coverage {cov.identifier!r} does not specify an upper "
                f"uncertainty dataset"
            )

        lower_uncert_ncss_url = None
        if (
            lower_uncert := getattr(cov, "lower_uncertainty_identifier", None)
        ) is not None:
            lower_uncert_ncss_url = cov.get_lower_uncertainty_thredds_ncss_url(settings)
        upper_uncert_ncss_url = None
        if (
            upper_uncert := getattr(cov, "upper_uncertainty_identifier", None)
        ) is not None:
            upper_uncert_ncss_url = cov.get_upper_uncertainty_thredds_ncss_url(settings)

        return cls(
            aggregation_period=cov.configuration.climatic_indicator.aggregation_period,
            climatic_indicator_name=cov.configuration.climatic_indicator.name,
            color_scale_min=cov.configuration.climatic_indicator.color_scale_min,
            color_scale_max=cov.configuration.climatic_indicator.color_scale_max,
            coverage_configuration_identifier=cov.configuration.identifier,
            coverage_identifier=cov.identifier,
            lower_uncertainty_identifier=lower_uncert,
            lower_uncertainty_ncss_url=lower_uncert_ncss_url,
            lower_uncertainy_netcdf_variable_name=lower_uncert_nc_var,
            measure_type=cov.configuration.climatic_indicator.measure_type,
            netcdf_variable_name=netcdf_variable_name,
            ncss_url=ncss_url,
            palette=cov.configuration.climatic_indicator.palette,
            upper_uncertainty_identifier=upper_uncert,
            upper_uncertainty_ncss_url=upper_uncert_ncss_url,
            upper_uncertainy_netcdf_variable_name=upper_uncert_nc_var,
            wms_base_url=cov.get_wms_base_url(settings),
            year_period=static.ObservationYearPeriod(cov.year_period.name),
            forecast_model_name=cov.forecast_model.name,
            related_thredds_datasets=[
                StaticCoverage.from_coverage(other_cov, settings)
                for other_cov in (related_covs or [])
            ],
            scenario=cov.scenario,
        )
