from ...schemas.coverages import ForecastCoverageConfigurationCreate
from ...schemas.static import ForecastScenario

# below are configurations for:
# 1. r95ptot anomaly 30 year (model ensemble) (all seasons)
# 2. r95ptot anomaly 30 year (other forecast models - no agree) (all seasons)


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
            climatic_indicator_id=climatic_indicator_ids["r95ptot-anomaly-thirty_year"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/pr_change_cumulative_check_avgagree_"
                "{time_window}_{scenario}_{year_period}_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}-uncertainty_group",
            wms_secondary_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvgtaa"],
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_period_group=year_period_groups["all_seasons"],
            forecast_model_group=forecast_model_groups["ensemble"],
            time_windows=[
                forecast_time_window_ids["tw1"],
                forecast_time_window_ids["tw2"],
            ],
        ),
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["r95ptot-anomaly-thirty_year"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/pr_change_cumulative_{forecast_model}_"
                "{year_period}_{scenario}_{time_window}_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvgtaa"],
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_period_group=year_period_groups["all_seasons"],
            forecast_model_group=forecast_model_groups["five_models"],
            time_windows=[
                forecast_time_window_ids["tw1"],
                forecast_time_window_ids["tw2"],
            ],
        ),
    ]
