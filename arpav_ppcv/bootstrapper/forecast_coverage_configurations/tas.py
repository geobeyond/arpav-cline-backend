from ...schemas.coverages import ForecastCoverageConfigurationCreate
from ...schemas.static import (
    ForecastScenario,
    ForecastYearPeriod,
)


def generate_forecast_coverage_configurations(
    climatic_indicator_ids: dict[str, int],
    spatial_region_ids: dict[str, int],
    forecast_model_ids: dict[str, int],
    forecast_time_window_ids: dict[str, int],
    observation_series_configuration_ids: dict[str, int],
) -> list[ForecastCoverageConfigurationCreate]:
    return [
        ForecastCoverageConfigurationCreate(
            netcdf_main_dataset_name="tas",
            thredds_url_pattern="{forecast_model_base_path}/{climatic_indicator}_avg_{scenario}_ts19762100_ls_{spatial_region}.nc",
            wms_main_layer_name="tas",
            climatic_indicator_id=climatic_indicator_ids["tas-absolute-annual"],
            spatial_region_id=spatial_region_ids["arpa-vfvg"],
            lower_uncertainty_thredds_url_pattern="{forecast_model_uncertainties_base_path}/{climatic_indicator}_stddown_{scenario}_ts19762100_ls_{spatial_region}.nc ",
            upper_uncertainty_thredds_url_pattern="{forecast_model_uncertainties_base_path}/{climatic_indicator}_stdup_{scenario}_ts19762100_ls_{spatial_region}.nc ",
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_periods=[
                ForecastYearPeriod.WINTER,
                ForecastYearPeriod.SPRING,
                ForecastYearPeriod.SUMMER,
                ForecastYearPeriod.AUTUMN,
            ],
            forecast_models=[
                forecast_model_ids["model_ensemble"],
                forecast_model_ids["ec_earth_cclm_4_8_17"],
                forecast_model_ids["ec_earth_racmo22e"],
                forecast_model_ids["ec_earth_rca4"],
                forecast_model_ids["hadgem2_racmo22e"],
                forecast_model_ids["mpi_esm_lr_remo2009"],
            ],
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "tas-absolute-annual_ARPAV_SEASONAL"
                ],
            ],
        ),
        ForecastCoverageConfigurationCreate(
            netcdf_main_dataset_name="tas",
            thredds_url_pattern="{forecast_model_base_path}/{climatic_indicator}_avg_{scenario}_ts19762100_ls_{spatial_region}.nc",
            wms_main_layer_name="tas",
            climatic_indicator_id=climatic_indicator_ids["tas-absolute-thirty_year"],
            spatial_region_id=spatial_region_ids["arpa-vfvg"],
            lower_uncertainty_thredds_url_pattern="{forecast_model_uncertainties_base_path}/{climatic_indicator}_stddown_{scenario}_ts19762100_ls_{spatial_region}.nc ",
            upper_uncertainty_thredds_url_pattern="{forecast_model_uncertainties_base_path}/{climatic_indicator}_stdup_{scenario}_ts19762100_ls_{spatial_region}.nc ",
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_periods=[
                ForecastYearPeriod.WINTER,
                ForecastYearPeriod.SPRING,
                ForecastYearPeriod.SUMMER,
                ForecastYearPeriod.AUTUMN,
            ],
            forecast_models=[
                forecast_model_ids["model_ensemble"],
                forecast_model_ids["ec_earth_cclm_4_8_17"],
                forecast_model_ids["ec_earth_racmo22e"],
                forecast_model_ids["ec_earth_rca4"],
                forecast_model_ids["hadgem2_racmo22e"],
                forecast_model_ids["mpi_esm_lr_remo2009"],
            ],
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "tas-absolute-annual_ARPAV_SEASONAL"
                ],
            ],
        ),
    ]
