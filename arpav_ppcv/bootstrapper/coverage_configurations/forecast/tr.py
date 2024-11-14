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
            name="tr_annual_absolute_model_ensemble",
            netcdf_main_dataset_name="tr",
            wms_main_layer_name="tr",
            thredds_url_pattern="ensymbc/clipped/ecatr_20_avg_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-absolute-annual"],
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
                        (CoreConfParamName.YEAR_PERIOD.value, "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tr_annual_absolute_model_ec_earth_cclm4_8_17",
            netcdf_main_dataset_name="tr",
            wms_main_layer_name="tr",
            thredds_url_pattern="EC-EARTH_CCLM4-8-17ymbc/clipped/ecatr_20_EC-EARTH_CCLM4-8-17_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-absolute-annual"],
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
                        (CoreConfParamName.YEAR_PERIOD.value, "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tr_annual_absolute_model_ec_earth_racmo22e",
            netcdf_main_dataset_name="tr",
            wms_main_layer_name="tr",
            thredds_url_pattern="EC-EARTH_RACMO22Eymbc/clipped/ecatr_20_EC-EARTH_RACMO22E_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-absolute-annual"],
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
                        (CoreConfParamName.YEAR_PERIOD.value, "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tr_annual_absolute_model_ec_earth_rca4",
            netcdf_main_dataset_name="tr",
            wms_main_layer_name="tr",
            thredds_url_pattern="EC-EARTH_RCA4ymbc/clipped/ecatr_20_EC-EARTH_RCA4_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-absolute-annual"],
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
                        (CoreConfParamName.YEAR_PERIOD.value, "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tr_annual_absolute_model_hadgem2_es_racmo22e",
            netcdf_main_dataset_name="tr",
            wms_main_layer_name="tr",
            thredds_url_pattern="HadGEM2-ES_RACMO22Eymbc/clipped/ecatr_20_HadGEM2-ES_RACMO22E_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-absolute-annual"],
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tr_annual_absolute_model_mpi_esm_lr_remo2009",
            netcdf_main_dataset_name="tr",
            wms_main_layer_name="tr",
            thredds_url_pattern="MPI-ESM-LR_REMO2009ymbc/clipped/ecatr_20_MPI-ESM-LR_REMO2009_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-absolute-annual"],
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tr_annual_absolute_model_ensemble_upper_uncertainty",
            netcdf_main_dataset_name="tr_stdup",
            wms_main_layer_name="tr_stdup",
            thredds_url_pattern="ensymbc/std/clipped/ecatr_20_stdup_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-absolute-annual"],
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
                        (CoreConfParamName.UNCERTAINTY_TYPE.value, "upper_bound")
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tr_annual_absolute_model_ensemble_lower_uncertainty",
            netcdf_main_dataset_name="tr_stddown",
            wms_main_layer_name="tr_stddown",
            thredds_url_pattern="ensymbc/std/clipped/ecatr_20_stddown_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-absolute-annual"],
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
                        (CoreConfParamName.UNCERTAINTY_TYPE.value, "lower_bound")
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tr_30yr_anomaly_annual_agree_model_ensemble",
            netcdf_main_dataset_name="tr",
            wms_main_layer_name="tr-uncertainty_group",
            wms_secondary_layer_name="tr",
            thredds_url_pattern="ensembletwbc/std/clipped/ecatran_20_avgagree_{time_window}_{scenario}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-anomaly-thirty_year"],
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tr_30yr_anomaly_annual_model_ec_earth_cclm4_8_17",
            netcdf_main_dataset_name="tr",
            wms_main_layer_name="tr",
            thredds_url_pattern="indici5rcm/clipped/ecatran_20_EC-EARTH_CCLM4-8-17_{scenario}_{time_window}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-anomaly-thirty_year"],
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tr_30yr_anomaly_annual_model_ec_earth_racmo22e",
            netcdf_main_dataset_name="tr",
            wms_main_layer_name="tr",
            thredds_url_pattern="indici5rcm/clipped/ecatran_20_EC-EARTH_RACMO22E_{scenario}_{time_window}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-anomaly-thirty_year"],
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tr_30yr_anomaly_annual_model_ec_earth_rca4",
            netcdf_main_dataset_name="tr",
            wms_main_layer_name="tr",
            thredds_url_pattern="indici5rcm/clipped/ecatran_20_EC-EARTH_RCA4_{scenario}_{time_window}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-anomaly-thirty_year"],
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tr_30yr_anomaly_annual_model_hadgem2_es_racmo22e",
            netcdf_main_dataset_name="tr",
            wms_main_layer_name="tr",
            thredds_url_pattern="indici5rcm/clipped/ecatran_20_HadGEM2-ES_RACMO22E_{scenario}_{time_window}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-anomaly-thirty_year"],
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tr_30yr_anomaly_annual_model_mpi_esm_lr_remo2009",
            netcdf_main_dataset_name="tr",
            wms_main_layer_name="tr",
            thredds_url_pattern="indici5rcm/clipped/ecatran_20_MPI-ESM-LR_REMO2009_{scenario}_{time_window}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tr-anomaly-thirty_year"],
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
    ]


def get_related_map() -> dict[str, list[str]]:
    return {
        "tr_annual_absolute_model_ensemble": [
            "tr_annual_absolute_model_ec_earth_cclm4_8_17",
            "tr_annual_absolute_model_ec_earth_racmo22e",
            "tr_annual_absolute_model_ec_earth_rca4",
            "tr_annual_absolute_model_hadgem2_es_racmo22e",
            "tr_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tr_annual_absolute_model_ec_earth_cclm4_8_17": [
            "tr_annual_absolute_model_ensemble",
            "tr_annual_absolute_model_ec_earth_racmo22e",
            "tr_annual_absolute_model_ec_earth_rca4",
            "tr_annual_absolute_model_hadgem2_es_racmo22e",
            "tr_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tr_annual_absolute_model_ec_earth_racmo22e": [
            "tr_annual_absolute_model_ensemble",
            "tr_annual_absolute_model_ec_earth_cclm4_8_17",
            "tr_annual_absolute_model_ec_earth_rca4",
            "tr_annual_absolute_model_hadgem2_es_racmo22e",
            "tr_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tr_annual_absolute_model_ec_earth_rca4": [
            "tr_annual_absolute_model_ensemble",
            "tr_annual_absolute_model_ec_earth_cclm4_8_17",
            "tr_annual_absolute_model_ec_earth_racmo22e",
            "tr_annual_absolute_model_hadgem2_es_racmo22e",
            "tr_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tr_annual_absolute_model_hadgem2_es_racmo22e": [
            "tr_annual_absolute_model_ensemble",
            "tr_annual_absolute_model_ec_earth_cclm4_8_17",
            "tr_annual_absolute_model_ec_earth_racmo22e",
            "tr_annual_absolute_model_ec_earth_rca4",
            "tr_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tr_annual_absolute_model_mpi_esm_lr_remo2009": [
            "tr_annual_absolute_model_ensemble",
            "tr_annual_absolute_model_ec_earth_cclm4_8_17",
            "tr_annual_absolute_model_ec_earth_racmo22e",
            "tr_annual_absolute_model_ec_earth_rca4",
            "tr_annual_absolute_model_hadgem2_es_racmo22e",
        ],
        "tr_30yr_anomaly_annual_agree_model_ensemble": [
            "tr_30yr_anomaly_annual_model_ec_earth_cclm4_8_17",
            "tr_30yr_anomaly_annual_model_ec_earth_racmo22e",
            "tr_30yr_anomaly_annual_model_ec_earth_rca4",
            "tr_30yr_anomaly_annual_model_hadgem2_es_racmo22e",
            "tr_30yr_anomaly_annual_model_mpi_esm_lr_remo2009",
        ],
        "tr_30yr_anomaly_annual_model_ec_earth_cclm4_8_17": [
            "tr_30yr_anomaly_annual_agree_model_ensemble",
            "tr_30yr_anomaly_annual_model_ec_earth_racmo22e",
            "tr_30yr_anomaly_annual_model_ec_earth_rca4",
            "tr_30yr_anomaly_annual_model_hadgem2_es_racmo22e",
            "tr_30yr_anomaly_annual_model_mpi_esm_lr_remo2009",
        ],
        "tr_30yr_anomaly_annual_model_ec_earth_racmo22e": [
            "tr_30yr_anomaly_annual_agree_model_ensemble",
            "tr_30yr_anomaly_annual_model_ec_earth_cclm4_8_17",
            "tr_30yr_anomaly_annual_model_ec_earth_rca4",
            "tr_30yr_anomaly_annual_model_hadgem2_es_racmo22e",
            "tr_30yr_anomaly_annual_model_mpi_esm_lr_remo2009",
        ],
        "tr_30yr_anomaly_annual_model_ec_earth_rca4": [
            "tr_30yr_anomaly_annual_agree_model_ensemble",
            "tr_30yr_anomaly_annual_model_ec_earth_cclm4_8_17",
            "tr_30yr_anomaly_annual_model_ec_earth_racmo22e",
            "tr_30yr_anomaly_annual_model_hadgem2_es_racmo22e",
            "tr_30yr_anomaly_annual_model_mpi_esm_lr_remo2009",
        ],
        "tr_30yr_anomaly_annual_model_hadgem2_es_racmo22e": [
            "tr_30yr_anomaly_annual_agree_model_ensemble",
            "tr_30yr_anomaly_annual_model_ec_earth_cclm4_8_17",
            "tr_30yr_anomaly_annual_model_ec_earth_racmo22e",
            "tr_30yr_anomaly_annual_model_ec_earth_rca4",
            "tr_30yr_anomaly_annual_model_mpi_esm_lr_remo2009",
        ],
        "tr_30yr_anomaly_annual_model_mpi_esm_lr_remo2009": [
            "tr_30yr_anomaly_annual_agree_model_ensemble",
            "tr_30yr_anomaly_annual_model_ec_earth_cclm4_8_17",
            "tr_30yr_anomaly_annual_model_ec_earth_racmo22e",
            "tr_30yr_anomaly_annual_model_ec_earth_rca4",
            "tr_30yr_anomaly_annual_model_hadgem2_es_racmo22e",
        ],
    }


def get_uncertainty_map() -> dict[str, tuple[str, str]]:
    return {
        "tr_annual_absolute_model_ensemble": (
            "tr_annual_absolute_model_ensemble_lower_uncertainty",
            "tr_annual_absolute_model_ensemble_upper_uncertainty",
        )
    }
