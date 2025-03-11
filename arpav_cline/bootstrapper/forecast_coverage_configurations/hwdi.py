from ...schemas.coverages import ForecastCoverageConfigurationCreate
from ...schemas.static import ForecastScenario

# below are configurations for:
# 1. hwdi anomaly 30 year (model ensemble) (all seasons)
# 2. hwdi anomaly 30 year (other forecast models - no agree) (all seasons)


def generate_forecast_coverage_configurations(
    climatic_indicator_ids: dict[str, int],
    spatial_region_ids: dict[str, int],
    forecast_time_window_ids: dict[str, int],
    year_period_groups: dict[str, int],
    forecast_model_groups: dict[str, int],
    observation_series_configuration_ids: dict[str, int],
) -> list[ForecastCoverageConfigurationCreate]:
    return [
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["hwdi-anomaly-thirty_year"],
            include_in_advanced_section_combinations=True,
            netcdf_main_dataset_name=(
                "heat_wave_duration_index_wrt_mean_of_reference_period"
            ),
            thredds_url_pattern=(
                "{forecast_model_base_path}/heat_waves_anom_avgagree_55_"
                "{time_window}_{scenario}_{year_period}_{spatial_region}.nc"
            ),
            wms_main_layer_name=(
                "heat_wave_duration_index_wrt_mean_of_reference_period-"
                "uncertainty_group"
            ),
            wms_secondary_layer_name=(
                "heat_wave_duration_index_wrt_mean_of_reference_period"
            ),
            spatial_region_id=spatial_region_ids["arpa_vfvgtaa"],
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_period_group=year_period_groups["only_summer"],
            forecast_model_group=forecast_model_groups["ensemble"],
            time_windows=[
                forecast_time_window_ids["tw1"],
                forecast_time_window_ids["tw2"],
            ],
        ),
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["hwdi-anomaly-thirty_year"],
            include_in_advanced_section_combinations=True,
            netcdf_main_dataset_name=(
                "heat_wave_duration_index_wrt_mean_of_reference_period"
            ),
            thredds_url_pattern=(
                "{forecast_model_base_path}/heat_waves_anom_{forecast_model}_"
                "{scenario}_{year_period}_55_{time_window}_{spatial_region}.nc"
            ),
            wms_main_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            spatial_region_id=spatial_region_ids["arpa_vfvgtaa"],
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_period_group=year_period_groups["only_summer"],
            forecast_model_group=forecast_model_groups["five_models"],
            time_windows=[
                forecast_time_window_ids["tw1"],
                forecast_time_window_ids["tw2"],
            ],
        ),
    ]
