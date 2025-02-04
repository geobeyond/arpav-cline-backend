from ..schemas.coverages import OverviewCoverageConfigurationCreate
from ..schemas.static import (
    DataCategory,
    ForecastScenario,
)


def generate_overview_coverage_configurations(
    climatic_indicator_ids: dict[str, int],
    spatial_region_ids: dict[str, int],
) -> list[OverviewCoverageConfigurationCreate]:
    return [
        OverviewCoverageConfigurationCreate(
            netcdf_main_dataset_name="TDd",
            thredds_url_pattern=("cline_yr/fldmean/TDd_A00_*.nc"),
            climatic_indicator_id=climatic_indicator_ids["tas-absolute-annual"],
            spatial_region_id=spatial_region_ids["arpa_vfvg"],
            data_category=DataCategory.HISTORICAL,
        ),
        OverviewCoverageConfigurationCreate(
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "ensymbc/std/clipped/fldmean/"
                "{climatic_indicator}_avg_{scenario}_ts19762100_"
                "ls_{spatial_region}_fldmean.nc"
            ),
            climatic_indicator_id=climatic_indicator_ids["tas-absolute-annual"],
            spatial_region_id=spatial_region_ids["arpa_vfvg"],
            data_category=DataCategory.FORECAST,
            lower_uncertainty_thredds_url_pattern=(
                "ensymbc/std/clipped/fldmean/{climatic_indicator}_stddown_"
                "{scenario}_ts19762100_ls_{spatial_region}_fldmean.nc"
            ),
            lower_uncertainty_netcdf_main_dataset_name="{climatic_indicator}_stddown",
            upper_uncertainty_thredds_url_pattern=(
                "ensymbc/std/clipped/fldmean/{climatic_indicator}_stdup_"
                "{scenario}_ts19762100_ls_{spatial_region}_fldmean.nc"
            ),
            upper_uncertainty_netcdf_main_dataset_name="{climatic_indicator}_stdup",
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
        ),
    ]
