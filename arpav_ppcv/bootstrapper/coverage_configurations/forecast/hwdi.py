from ....schemas.base import CoreConfParamName
from ....schemas.coverages import (
    CoverageConfigurationCreate,
    ConfigurationParameterPossibleValueCreate,
)


def generate_configurations(
    conf_param_values,
    climatic_indicators: dict[str, int],
) -> list[CoverageConfigurationCreate]:
    return [
        CoverageConfigurationCreate(
            name="hwdi_30yr_anomaly_seasonal_agree_model_ensemble",
            netcdf_main_dataset_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            wms_main_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period-uncertainty_group",
            wms_secondary_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            thredds_url_pattern="ensembletwbc/std/clipped/heat_waves_anom_avgagree_55_{time_window}_{scenario}_{year_period}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["hwdi-anomaly-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "forecast")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.CLIMATOLOGICAL_MODEL.value, "model_ensemble")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("time_window", "tw1")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("time_window", "tw2")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp26")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp45")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp85")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.YEAR_PERIOD.value, "summer")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="hwdi_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17",
            netcdf_main_dataset_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            wms_main_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            thredds_url_pattern="indici5rcm/clipped/heat_waves_anom_EC-EARTH_CCLM4-8-17_{scenario}_{year_period}_55_{time_window}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["hwdi-anomaly-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "forecast")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (
                            CoreConfParamName.CLIMATOLOGICAL_MODEL.value,
                            "ec_earth_cclm_4_8_17",
                        )
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("time_window", "tw1")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("time_window", "tw2")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp26")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp45")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp85")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.YEAR_PERIOD.value, "summer")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="hwdi_30yr_anomaly_seasonal_model_ec_earth_racmo22e",
            netcdf_main_dataset_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            wms_main_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            thredds_url_pattern="indici5rcm/clipped/heat_waves_anom_EC-EARTH_RACMO22E_{scenario}_{year_period}_55_{time_window}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["hwdi-anomaly-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "forecast")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (
                            CoreConfParamName.CLIMATOLOGICAL_MODEL.value,
                            "ec_earth_racmo22e",
                        )
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("time_window", "tw1")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("time_window", "tw2")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp26")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp45")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp85")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.YEAR_PERIOD.value, "summer")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="hwdi_30yr_anomaly_seasonal_model_ec_earth_rca4",
            netcdf_main_dataset_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            wms_main_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            thredds_url_pattern="indici5rcm/clipped/heat_waves_anom_EC-EARTH_RCA4_{scenario}_{year_period}_55_{time_window}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["hwdi-anomaly-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "forecast")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.CLIMATOLOGICAL_MODEL.value, "ec_earth_rca4")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("time_window", "tw1")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("time_window", "tw2")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp26")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp45")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp85")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.YEAR_PERIOD.value, "summer")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="hwdi_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e",
            netcdf_main_dataset_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            wms_main_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            thredds_url_pattern="indici5rcm/clipped/heat_waves_anom_HadGEM2-ES_RACMO22E_{scenario}_{year_period}_55_{time_window}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["hwdi-anomaly-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "forecast")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (
                            CoreConfParamName.CLIMATOLOGICAL_MODEL.value,
                            "hadgem2_racmo22e",
                        )
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("time_window", "tw1")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("time_window", "tw2")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp26")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp45")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp85")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.YEAR_PERIOD.value, "summer")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="hwdi_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009",
            netcdf_main_dataset_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            wms_main_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            thredds_url_pattern="indici5rcm/clipped/heat_waves_anom_MPI-ESM-LR_REMO2009_{scenario}_{year_period}_55_{time_window}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["hwdi-anomaly-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "forecast")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (
                            CoreConfParamName.CLIMATOLOGICAL_MODEL.value,
                            "mpi_esm_lr_remo2009",
                        )
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("time_window", "tw1")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("time_window", "tw2")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp26")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp45")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.SCENARIO.value, "rcp85")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
            ],
        ),
    ]


def get_related_map() -> dict[str, list[str]]:
    return {
        "hwdi_30yr_anomaly_seasonal_agree_model_ensemble": [
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_racmo22e",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_rca4",
            "hwdi_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e",
            "hwdi_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009",
        ],
        "hwdi_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17": [
            "hwdi_30yr_anomaly_seasonal_agree_model_ensemble",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_racmo22e",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_rca4",
            "hwdi_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e",
            "hwdi_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009",
        ],
        "hwdi_30yr_anomaly_seasonal_model_ec_earth_racmo22e": [
            "hwdi_30yr_anomaly_seasonal_agree_model_ensemble",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_rca4",
            "hwdi_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e",
            "hwdi_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009",
        ],
        "hwdi_30yr_anomaly_seasonal_model_ec_earth_rca4": [
            "hwdi_30yr_anomaly_seasonal_agree_model_ensemble",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_racmo22e",
            "hwdi_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e",
            "hwdi_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009",
        ],
        "hwdi_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e": [
            "hwdi_30yr_anomaly_seasonal_agree_model_ensemble",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_racmo22e",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_rca4",
            "hwdi_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009",
        ],
        "hwdi_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009": [
            "hwdi_30yr_anomaly_seasonal_agree_model_ensemble",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_racmo22e",
            "hwdi_30yr_anomaly_seasonal_model_ec_earth_rca4",
            "hwdi_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e",
        ],
    }


def get_uncertainty_map() -> dict[str, tuple[str, str]]:
    return {}
