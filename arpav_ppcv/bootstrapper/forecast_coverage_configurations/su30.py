from ...schemas.coverages import ForecastCoverageConfigurationCreate
from ...schemas.static import ForecastScenario

# below are configurations for:
# 1. su30 anomaly 30 year (model ensemble) (all year)
# 2. su30 anomaly 30 year (other forecast models - no agree) (all year)
# 3. su30 absolute annual (model ensemble) (all year)
# 4. su30 absolute annual (other forecast models - no uncertainties) (all year)


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
            climatic_indicator_id=climatic_indicator_ids["su30-anomaly-thirty_year"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/ecasuan_30_avgagree_"
                "{time_window}_{scenario}_ls_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}-uncertainty_group",
            wms_secondary_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvg"],
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_period_group=year_period_groups["only_year"],
            forecast_model_group=forecast_model_groups["ensemble"],
            forecast_time_windows=[
                forecast_time_window_ids["tw1"],
                forecast_time_window_ids["tw2"],
            ],
        ),
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["su30-anomaly-thirty_year"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/ecasuan_30_"
                "{forecast_model}_{scenario}_{time_window}_ls_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvg"],
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_period_group=year_period_groups["only_year"],
            forecast_model_group=forecast_model_groups["five_models"],
            forecast_time_windows=[
                forecast_time_window_ids["tw1"],
                forecast_time_window_ids["tw2"],
            ],
        ),
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["su30-absolute-annual"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/ecasu_30_avg_{scenario}_"
                "ts19762100_ls_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvg"],
            lower_uncertainty_thredds_url_pattern=(
                "{forecast_model_uncertainties_base_path}/ecasu_"
                "30_stddown_{scenario}_ts19762100_ls_{spatial_region}.nc"
            ),
            lower_uncertainty_netcdf_main_dataset_name="{climatic_indicator}_stddown",
            upper_uncertainty_thredds_url_pattern=(
                "{forecast_model_uncertainties_base_path}/ecasu_"
                "30_stdup_{scenario}_ts19762100_ls_{spatial_region}.nc"
            ),
            upper_uncertainty_netcdf_main_dataset_name="{climatic_indicator}_stdup",
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_period_group=year_period_groups["only_year"],
            forecast_model_group=forecast_model_groups["ensemble"],
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "su30-absolute-annual-arpa_v:arpa_fvg-yearly"
                ],
            ],
        ),
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["su30-absolute-annual"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/ecasu_30_"
                "{forecast_model}_{scenario}_ts19762100_ls_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvg"],
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_period_group=year_period_groups["only_year"],
            forecast_model_group=forecast_model_groups["five_models"],
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "su30-absolute-annual-arpa_v:arpa_fvg-yearly"
                ],
            ],
        ),
    ]
