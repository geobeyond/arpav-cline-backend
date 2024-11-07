from ....schemas.base import CoreConfParamName
from ....schemas.coverages import (
    CoverageConfigurationCreate,
    ConfigurationParameterPossibleValueCreate,
)

# _DISPLAY_NAME_ENGLISH = "Duration of heat waves"
# _DISPLAY_NAME_ITALIAN = "Durata delle ondate di calore"
# _DESCRIPTION_ENGLISH = (
#     "Sequences of 5 consecutive days in which the temperature is 5°C higher than the "
#     "reference average for that day of the year"
# )
# _DESCRIPTION_ITALIAN = (
#     "Sequenze di 5 giorni consecutivi in cui la temperatura è maggiore di 5°C rispetto "
#     "alla media di riferimento per quel giorno dell'anno"
# )
# _DATA_PRECISION = 0


def generate_configurations(
    conf_param_values,
    climatic_indicators: dict[str, int],
) -> list[CoverageConfigurationCreate]:
    return [
        CoverageConfigurationCreate(
            name="hwdi_30yr_anomaly_seasonal_agree_model_ensemble",
            # display_name_english=_DISPLAY_NAME_ENGLISH,
            # display_name_italian=_DISPLAY_NAME_ITALIAN,
            # description_english=_DESCRIPTION_ENGLISH,
            # description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            wms_main_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period-uncertainty_group",
            wms_secondary_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            thredds_url_pattern="ensembletwbc/std/clipped/heat_waves_anom_avgagree_55_{time_window}_{scenario}_{year_period}_VFVGTAA.nc",
            # unit_english="days",
            # unit_italian="gg",
            # palette="uncert-stippled/seq-YlOrRd",
            # color_scale_min=0,
            # color_scale_max=50,
            # data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["hwdi-anomaly-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "forecast")
                    ].id
                ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.CLIMATOLOGICAL_VARIABLE.value, "hwdi")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.AGGREGATION_PERIOD.value, "30yr")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.MEASURE.value, "anomaly")
                #     ].id
                # ),
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
            # display_name_english=_DISPLAY_NAME_ENGLISH,
            # display_name_italian=_DISPLAY_NAME_ITALIAN,
            # description_english=_DESCRIPTION_ENGLISH,
            # description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            wms_main_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            thredds_url_pattern="indici5rcm/clipped/heat_waves_anom_EC-EARTH_CCLM4-8-17_{scenario}_{year_period}_55_{time_window}_VFVGTAA.nc",
            # unit_english="days",
            # unit_italian="gg",
            # palette="default/seq-YlOrRd",
            # color_scale_min=0,
            # color_scale_max=50,
            # data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["hwdi-anomaly-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "forecast")
                    ].id
                ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.CLIMATOLOGICAL_VARIABLE.value, "hwdi")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.AGGREGATION_PERIOD.value, "30yr")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.MEASURE.value, "anomaly")
                #     ].id
                # ),
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
            # display_name_english=_DISPLAY_NAME_ENGLISH,
            # display_name_italian=_DISPLAY_NAME_ITALIAN,
            # description_english=_DESCRIPTION_ENGLISH,
            # description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            wms_main_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            thredds_url_pattern="indici5rcm/clipped/heat_waves_anom_EC-EARTH_RACMO22E_{scenario}_{year_period}_55_{time_window}_VFVGTAA.nc",
            # unit_english="days",
            # unit_italian="gg",
            # palette="default/seq-YlOrRd",
            # color_scale_min=0,
            # color_scale_max=50,
            # data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["hwdi-anomaly-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "forecast")
                    ].id
                ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.CLIMATOLOGICAL_VARIABLE.value, "hwdi")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.AGGREGATION_PERIOD.value, "30yr")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.MEASURE.value, "anomaly")
                #     ].id
                # ),
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
            # display_name_english=_DISPLAY_NAME_ENGLISH,
            # display_name_italian=_DISPLAY_NAME_ITALIAN,
            # description_english=_DESCRIPTION_ENGLISH,
            # description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            wms_main_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            thredds_url_pattern="indici5rcm/clipped/heat_waves_anom_EC-EARTH_RCA4_{scenario}_{year_period}_55_{time_window}_VFVGTAA.nc",
            # unit_english="days",
            # unit_italian="gg",
            # palette="default/seq-YlOrRd",
            # color_scale_min=0,
            # color_scale_max=50,
            # data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["hwdi-anomaly-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "forecast")
                    ].id
                ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.CLIMATOLOGICAL_VARIABLE.value, "hwdi")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.AGGREGATION_PERIOD.value, "30yr")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.MEASURE.value, "anomaly")
                #     ].id
                # ),
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
            # display_name_english=_DISPLAY_NAME_ENGLISH,
            # display_name_italian=_DISPLAY_NAME_ITALIAN,
            # description_english=_DESCRIPTION_ENGLISH,
            # description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            wms_main_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            thredds_url_pattern="indici5rcm/clipped/heat_waves_anom_HadGEM2-ES_RACMO22E_{scenario}_{year_period}_55_{time_window}_VFVGTAA.nc",
            # unit_english="days",
            # unit_italian="gg",
            # palette="default/seq-YlOrRd",
            # color_scale_min=0,
            # color_scale_max=50,
            # data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["hwdi-anomaly-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "forecast")
                    ].id
                ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.CLIMATOLOGICAL_VARIABLE.value, "hwdi")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.AGGREGATION_PERIOD.value, "30yr")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.MEASURE.value, "anomaly")
                #     ].id
                # ),
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
            # display_name_english=_DISPLAY_NAME_ENGLISH,
            # display_name_italian=_DISPLAY_NAME_ITALIAN,
            # description_english=_DESCRIPTION_ENGLISH,
            # description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            wms_main_layer_name="heat_wave_duration_index_wrt_mean_of_reference_period",
            thredds_url_pattern="indici5rcm/clipped/heat_waves_anom_MPI-ESM-LR_REMO2009_{scenario}_{year_period}_55_{time_window}_VFVGTAA.nc",
            # unit_english="days",
            # unit_italian="gg",
            # palette="default/seq-YlOrRd",
            # color_scale_min=0,
            # color_scale_max=50,
            # data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["hwdi-anomaly-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "forecast")
                    ].id
                ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.CLIMATOLOGICAL_VARIABLE.value, "hwdi")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.AGGREGATION_PERIOD.value, "30yr")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.MEASURE.value, "anomaly")
                #     ].id
                # ),
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
