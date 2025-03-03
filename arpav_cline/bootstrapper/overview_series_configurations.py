from ..schemas.overviews import (
    ForecastOverviewSeriesConfigurationCreate,
    ObservationOverviewSeriesConfigurationCreate,
)
from ..schemas.static import ForecastScenario


def generate_observation_overview_series_configurations(
    climatic_indicator_ids: dict[str, int],
) -> list[ObservationOverviewSeriesConfigurationCreate]:
    return [
        ObservationOverviewSeriesConfigurationCreate(
            netcdf_main_dataset_name="TDd",
            thredds_url_pattern=("cline_yr/fldmean/TDd_A00_*.nc"),
            climatic_indicator_id=climatic_indicator_ids["tas-absolute-annual"],
        ),
    ]


def generate_forecast_overview_series_configurations(
    climatic_indicator_ids: dict[str, int],
) -> list[ForecastOverviewSeriesConfigurationCreate]:
    return [
        ForecastOverviewSeriesConfigurationCreate(
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "ensymbc/std/clipped/fldmean/"
                "{climatic_indicator}_avg_{scenario}_ts19762100_"
                "ls_VFVG_fldmean.nc"
            ),
            climatic_indicator_id=climatic_indicator_ids["tas-absolute-annual"],
            lower_uncertainty_thredds_url_pattern=(
                "ensymbc/std/clipped/fldmean/{climatic_indicator}_stddown_"
                "{scenario}_ts19762100_ls_VFVG_fldmean.nc"
            ),
            lower_uncertainty_netcdf_main_dataset_name="{climatic_indicator}_stddown",
            upper_uncertainty_thredds_url_pattern=(
                "ensymbc/std/clipped/fldmean/{climatic_indicator}_stdup_"
                "{scenario}_ts19762100_ls_VFVG_fldmean.nc"
            ),
            upper_uncertainty_netcdf_main_dataset_name="{climatic_indicator}_stdup",
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
        ),
    ]
