from ...schemas.coverages import ForecastCoverageConfigurationCreate
from ...schemas.static import (
    ForecastScenario,
    ForecastYearPeriod,
)

# below are configurations for:
# 1. hdds anomaly 30 year (model ensemble) (all year)
# 2. hdds anomaly 30 year (other forecast models - no agree) (all year)
# 3. hdds absolute annual (model ensemble) (all year)
# 4. hdds absolute annual (other forecast models - no uncertainties) (all year)


def generate_forecast_coverage_configurations(
    climatic_indicator_ids: dict[str, int],
    spatial_region_ids: dict[str, int],
    forecast_model_ids: dict[str, int],
    forecast_time_window_ids: dict[str, int],
    observation_series_configuration_ids: dict[str, int],
) -> list[ForecastCoverageConfigurationCreate]:
    return [
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["hdds-anomaly-thirty_year"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/{climatic_indicator}_an_20oc_"
                "avgagree_{time_window}_{scenario}_ls_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}-uncertainty_group",
            wms_secondary_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvg"],
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_periods=[
                ForecastYearPeriod.ALL_YEAR,
            ],
            forecast_time_windows=[
                forecast_time_window_ids["tw1"],
                forecast_time_window_ids["tw2"],
            ],
            forecast_models=[
                forecast_model_ids["model_ensemble"],
            ],
        ),
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["hdds-anomaly-thirty_year"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/{climatic_indicator}_an_20oc_"
                "{forecast_model}_{scenario}_{time_window}_ls_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvg"],
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_periods=[
                ForecastYearPeriod.ALL_YEAR,
            ],
            forecast_time_windows=[
                forecast_time_window_ids["tw1"],
                forecast_time_window_ids["tw2"],
            ],
            forecast_models=[
                forecast_model_ids["ec_earth_cclm_4_8_17"],
                forecast_model_ids["ec_earth_racmo22e"],
                forecast_model_ids["ec_earth_rca4"],
                forecast_model_ids["hadgem2_racmo22e"],
                forecast_model_ids["mpi_esm_lr_remo2009"],
            ],
        ),
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["hdds-absolute-annual"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/{climatic_indicator}_20oc_avg_"
                "ts19762100_{scenario}_ls_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvg"],
            lower_uncertainty_thredds_url_pattern=(
                "{forecast_model_uncertainties_base_path}/{climatic_indicator}_"
                "20oc_stddown_ts19762100_{scenario}_ls_{spatial_region}.nc"
            ),
            upper_uncertainty_thredds_url_pattern=(
                "{forecast_model_uncertainties_base_path}/{climatic_indicator}_"
                "20oc_stdup_ts19762100_{scenario}_ls_{spatial_region}.nc"
            ),
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_periods=[
                ForecastYearPeriod.ALL_YEAR,
            ],
            forecast_models=[
                forecast_model_ids["model_ensemble"],
            ],
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "hdds-absolute-annual-arpa_v-yearly"
                ],
            ],
        ),
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["hdds-absolute-annual"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/{climatic_indicator}_20oc_"
                "{forecast_model}_{scenario}_ts19762100_ls_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvg"],
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_periods=[
                ForecastYearPeriod.ALL_YEAR,
            ],
            forecast_models=[
                forecast_model_ids["ec_earth_cclm_4_8_17"],
                forecast_model_ids["ec_earth_racmo22e"],
                forecast_model_ids["ec_earth_rca4"],
                forecast_model_ids["hadgem2_racmo22e"],
                forecast_model_ids["mpi_esm_lr_remo2009"],
            ],
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "hdds-absolute-annual-arpa_v-yearly"
                ],
            ],
        ),
    ]
