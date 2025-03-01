from ...schemas.coverages import ForecastCoverageConfigurationCreate
from ...schemas.static import ForecastScenario

# below are configurations for:
# 1. pr anomaly 30 year (model ensemble)
# 2. pr anomaly 30 year (other forecast models - no agree)
# 3. pr anomaly annual (model ensemble) (4 seasons)
# 4. pr anomaly annual (other forecast models - no uncertainties) (4 seasons)
# 5. pr absolute annual (model ensemble) (4 seasons)
# 6. pr absolute annual (other forecast models - no uncertainties) (4 seasons)
# 7. pr absolute annual (model ensemble) (all year)
# 8. pr absolute annual (other forecast models - no uncertainties) (all year)


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
            climatic_indicator_id=climatic_indicator_ids["pr-anomaly-thirty_year"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/{climatic_indicator}_avgagree_percentage_"
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
            climatic_indicator_id=climatic_indicator_ids["pr-anomaly-thirty_year"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/{climatic_indicator}_{forecast_model}_"
                "{scenario}_seas_{time_window}_percentage_{year_period}_"
                "{spatial_region}.nc"
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
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["pr-anomaly-annual"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/{climatic_indicator}_anom_pp_ts_"
                "{scenario}_{year_period}_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvgtaa"],
            lower_uncertainty_thredds_url_pattern=(
                "{forecast_model_uncertainties_base_path}/{climatic_indicator}_anom_"
                "stddown_pp_ts_{scenario}_{year_period}_{spatial_region}.nc"
            ),
            lower_uncertainty_netcdf_main_dataset_name="{climatic_indicator}_stddown",
            upper_uncertainty_thredds_url_pattern=(
                "{forecast_model_uncertainties_base_path}/{climatic_indicator}_anom_"
                "stdup_pp_ts_{scenario}_{year_period}_{spatial_region}.nc"
            ),
            upper_uncertainty_netcdf_main_dataset_name="{climatic_indicator}_stdup",
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_period_group=year_period_groups["all_seasons"],
            forecast_model_group=forecast_model_groups["ensemble"],
        ),
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["pr-anomaly-annual"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/{climatic_indicator}_{forecast_model}_"
                "{scenario}_{year_period}_anomaly_pp_percentage_{spatial_region}.nc"
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
        ),
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["pr-absolute-annual"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/{climatic_indicator}_avg_{scenario}_"
                "{year_period}_ts19762100_ls_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvgtaa"],
            lower_uncertainty_thredds_url_pattern=(
                "{forecast_model_uncertainties_base_path}/{climatic_indicator}_"
                "stddown_{scenario}_{year_period}_ts19762100_ls_{spatial_region}.nc"
            ),
            lower_uncertainty_netcdf_main_dataset_name="{climatic_indicator}_stddown",
            upper_uncertainty_thredds_url_pattern=(
                "{forecast_model_uncertainties_base_path}/{climatic_indicator}_"
                "stdup_{scenario}_{year_period}_ts19762100_ls_{spatial_region}.nc"
            ),
            upper_uncertainty_netcdf_main_dataset_name="{climatic_indicator}_stdup",
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_period_group=year_period_groups["all_seasons"],
            forecast_model_group=forecast_model_groups["ensemble"],
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "tas-absolute-annual-arpa_v:arpa_fvg-seasonal"
                ],
            ],
        ),
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["pr-absolute-annual"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/{climatic_indicator}_{forecast_model}_"
                "{scenario}_{year_period}_ts_ls_{spatial_region}.nc"
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
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "tas-absolute-annual-arpa_v:arpa_fvg-seasonal"
                ],
            ],
        ),
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["pr-absolute-annual"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/{climatic_indicator}_avg_{scenario}_"
                "ts19762100_ls_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvgtaa"],
            lower_uncertainty_thredds_url_pattern=(
                "{forecast_model_uncertainties_base_path}/{climatic_indicator}_"
                "stddown_{scenario}_ts19762100_ls_{spatial_region}.nc"
            ),
            lower_uncertainty_netcdf_main_dataset_name="{climatic_indicator}_stddown",
            upper_uncertainty_thredds_url_pattern=(
                "{forecast_model_uncertainties_base_path}/{climatic_indicator}_"
                "stdup_{scenario}_ts19762100_ls_{spatial_region}.nc"
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
                    "tas-absolute-annual-arpa_v:arpa_fvg-yearly"
                ],
            ],
        ),
        ForecastCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["pr-absolute-annual"],
            netcdf_main_dataset_name="{climatic_indicator}",
            thredds_url_pattern=(
                "{forecast_model_base_path}/{climatic_indicator}_{forecast_model}_{scenario}_"
                "ts_ls_{spatial_region}.nc"
            ),
            wms_main_layer_name="{climatic_indicator}",
            spatial_region_id=spatial_region_ids["arpa_vfvgtaa"],
            scenarios=[
                ForecastScenario.RCP26,
                ForecastScenario.RCP45,
                ForecastScenario.RCP85,
            ],
            year_period_group=year_period_groups["only_year"],
            forecast_model_group=forecast_model_groups["five_models"],
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "tas-absolute-annual-arpa_v:arpa_fvg-yearly"
                ],
            ],
        ),
    ]
