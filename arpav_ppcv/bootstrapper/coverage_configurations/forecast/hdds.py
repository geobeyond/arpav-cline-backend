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
            name="hdds_annual_absolute_model_ensemble",
            netcdf_main_dataset_name="hdds",
            wms_main_layer_name="hdds",
            thredds_url_pattern="ensymbc/clipped_noppcne/hdds_20oc_avg_ts19762100_{scenario}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-absolute-annual"],
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
            name="hdds_annual_absolute_model_ec_earth_cclm4_8_17",
            netcdf_main_dataset_name="hdds",
            wms_main_layer_name="hdds",
            thredds_url_pattern="EC-EARTH_CCLM4-8-17ymbc/clipped_noppcne/hdds_20oc_EC-EARTH_CCLM4-8-17_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-absolute-annual"],
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
            name="hdds_annual_absolute_model_ec_earth_racmo22e",
            netcdf_main_dataset_name="hdds",
            wms_main_layer_name="hdds",
            thredds_url_pattern="EC-EARTH_RACMO22Eymbc/clipped_noppcne/hdds_20oc_EC-EARTH_RACMO22E_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-absolute-annual"],
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
            name="hdds_annual_absolute_model_ec_earth_rca4",
            netcdf_main_dataset_name="hdds",
            wms_main_layer_name="hdds",
            thredds_url_pattern="EC-EARTH_RCA4ymbc/clipped_noppcne/hdds_20oc_EC-EARTH_RCA4_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-absolute-annual"],
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
            name="hdds_annual_absolute_model_hadgem2_es_racmo22e",
            netcdf_main_dataset_name="hdds",
            wms_main_layer_name="hdds",
            thredds_url_pattern="HadGEM2-ES_RACMO22Eymbc/clipped_noppcne/hdds_20oc_HadGEM2-ES_RACMO22E_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-absolute-annual"],
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
                        (CoreConfParamName.YEAR_PERIOD.value, "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="hdds_annual_absolute_model_mpi_esm_lr_remo2009",
            netcdf_main_dataset_name="hdds",
            wms_main_layer_name="hdds",
            thredds_url_pattern="MPI-ESM-LR_REMO2009ymbc/clipped_noppcne/hdds_20oc_MPI-ESM-LR_REMO2009_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-absolute-annual"],
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
                        (CoreConfParamName.YEAR_PERIOD.value, "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="hdds_annual_absolute_model_ensemble_upper_uncertainty",
            netcdf_main_dataset_name="hdds_stdup",
            wms_main_layer_name="hdds_stdup",
            thredds_url_pattern="ensymbc/std/clipped/hdds_20oc_stdup_ts19762100_{scenario}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-absolute-annual"],
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
            name="hdds_annual_absolute_model_ensemble_lower_uncertainty",
            netcdf_main_dataset_name="hdds_stddown",
            wms_main_layer_name="hdds_stddown",
            thredds_url_pattern="ensymbc/std/clipped/hdds_20oc_stddown_ts19762100_{scenario}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-absolute-annual"],
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
            name="hdds_30yr_anomaly_annual_agree_model_ensemble",
            netcdf_main_dataset_name="hdds",
            wms_main_layer_name="hdds-uncertainty_group",
            wms_secondary_layer_name="hdds",
            thredds_url_pattern="ensembletwbc/std/clipped/hdds_an_20oc_avgagree_{time_window}_{scenario}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-anomaly-thirty_year"],
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
            name="hdds_30yr_anomaly_annual_model_ec_earth_cclm4_8_17",
            netcdf_main_dataset_name="hdds",
            wms_main_layer_name="hdds",
            thredds_url_pattern="indici5rcm/clipped_noppcne/hdds_an_20oc_EC-EARTH_CCLM4-8-17_{scenario}_{time_window}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-anomaly-thirty_year"],
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
            name="hdds_30yr_anomaly_annual_model_ec_earth_racmo22e",
            netcdf_main_dataset_name="hdds",
            wms_main_layer_name="hdds",
            thredds_url_pattern="indici5rcm/clipped_noppcne/hdds_an_20oc_EC-EARTH_RACMO22E_{scenario}_{time_window}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-anomaly-thirty_year"],
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
            name="hdds_30yr_anomaly_annual_model_ec_earth_rca4",
            netcdf_main_dataset_name="hdds",
            wms_main_layer_name="hdds",
            thredds_url_pattern="indici5rcm/clipped_noppcne/hdds_an_20oc_EC-EARTH_RCA4_{scenario}_{time_window}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-anomaly-thirty_year"],
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
            name="hdds_30yr_anomaly_annual_model_hadgem2_es_racmo22e",
            netcdf_main_dataset_name="hdds",
            wms_main_layer_name="hdds",
            thredds_url_pattern="indici5rcm/clipped_noppcne/hdds_an_20oc_HadGEM2-ES_RACMO22E_{scenario}_{time_window}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-anomaly-thirty_year"],
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
            name="hdds_30yr_anomaly_annual_model_mpi_esm_lr_remo2009",
            netcdf_main_dataset_name="hdds",
            wms_main_layer_name="hdds",
            thredds_url_pattern="indici5rcm/clipped_noppcne/hdds_an_20oc_MPI-ESM-LR_REMO2009_{scenario}_{time_window}_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["hdds-anomaly-thirty_year"],
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
        "hdds_annual_absolute_model_ensemble": [
            "hdds_annual_absolute_model_ec_earth_cclm4_8_17",
            "hdds_annual_absolute_model_ec_earth_racmo22e",
            "hdds_annual_absolute_model_ec_earth_rca4",
            "hdds_annual_absolute_model_hadgem2_es_racmo22e",
            "hdds_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "hdds_annual_absolute_model_ec_earth_cclm4_8_17": [
            "hdds_annual_absolute_model_ensemble",
            "hdds_annual_absolute_model_ec_earth_racmo22e",
            "hdds_annual_absolute_model_ec_earth_rca4",
            "hdds_annual_absolute_model_hadgem2_es_racmo22e",
            "hdds_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "hdds_annual_absolute_model_ec_earth_racmo22e": [
            "hdds_annual_absolute_model_ensemble",
            "hdds_annual_absolute_model_ec_earth_cclm4_8_17",
            "hdds_annual_absolute_model_ec_earth_rca4",
            "hdds_annual_absolute_model_hadgem2_es_racmo22e",
            "hdds_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "hdds_annual_absolute_model_ec_earth_rca4": [
            "hdds_annual_absolute_model_ensemble",
            "hdds_annual_absolute_model_ec_earth_cclm4_8_17",
            "hdds_annual_absolute_model_ec_earth_racmo22e",
            "hdds_annual_absolute_model_hadgem2_es_racmo22e",
            "hdds_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "hdds_annual_absolute_model_hadgem2_es_racmo22e": [
            "hdds_annual_absolute_model_ensemble",
            "hdds_annual_absolute_model_ec_earth_cclm4_8_17",
            "hdds_annual_absolute_model_ec_earth_racmo22e",
            "hdds_annual_absolute_model_ec_earth_rca4",
            "hdds_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "hdds_annual_absolute_model_mpi_esm_lr_remo2009": [
            "hdds_annual_absolute_model_ensemble",
            "hdds_annual_absolute_model_ec_earth_cclm4_8_17",
            "hdds_annual_absolute_model_ec_earth_racmo22e",
            "hdds_annual_absolute_model_ec_earth_rca4",
            "hdds_annual_absolute_model_hadgem2_es_racmo22e",
        ],
        "hdds_30yr_anomaly_annual_agree_model_ensemble": [
            "hdds_30yr_anomaly_annual_model_ec_earth_cclm4_8_17",
            "hdds_30yr_anomaly_annual_model_ec_earth_racmo22e",
            "hdds_30yr_anomaly_annual_model_ec_earth_rca4",
            "hdds_30yr_anomaly_annual_model_hadgem2_es_racmo22e",
            "hdds_30yr_anomaly_annual_model_mpi_esm_lr_remo2009",
        ],
        "hdds_30yr_anomaly_annual_model_ec_earth_cclm4_8_17": [
            "hdds_30yr_anomaly_annual_agree_model_ensemble",
            "hdds_30yr_anomaly_annual_model_ec_earth_racmo22e",
            "hdds_30yr_anomaly_annual_model_ec_earth_rca4",
            "hdds_30yr_anomaly_annual_model_hadgem2_es_racmo22e",
            "hdds_30yr_anomaly_annual_model_mpi_esm_lr_remo2009",
        ],
        "hdds_30yr_anomaly_annual_model_ec_earth_racmo22e": [
            "hdds_30yr_anomaly_annual_agree_model_ensemble",
            "hdds_30yr_anomaly_annual_model_ec_earth_cclm4_8_17",
            "hdds_30yr_anomaly_annual_model_ec_earth_rca4",
            "hdds_30yr_anomaly_annual_model_hadgem2_es_racmo22e",
            "hdds_30yr_anomaly_annual_model_mpi_esm_lr_remo2009",
        ],
        "hdds_30yr_anomaly_annual_model_ec_earth_rca4": [
            "hdds_30yr_anomaly_annual_agree_model_ensemble",
            "hdds_30yr_anomaly_annual_model_ec_earth_cclm4_8_17",
            "hdds_30yr_anomaly_annual_model_ec_earth_racmo22e",
            "hdds_30yr_anomaly_annual_model_hadgem2_es_racmo22e",
            "hdds_30yr_anomaly_annual_model_mpi_esm_lr_remo2009",
        ],
        "hdds_30yr_anomaly_annual_model_hadgem2_es_racmo22e": [
            "hdds_30yr_anomaly_annual_agree_model_ensemble",
            "hdds_30yr_anomaly_annual_model_ec_earth_cclm4_8_17",
            "hdds_30yr_anomaly_annual_model_ec_earth_racmo22e",
            "hdds_30yr_anomaly_annual_model_ec_earth_rca4",
            "hdds_30yr_anomaly_annual_model_mpi_esm_lr_remo2009",
        ],
        "hdds_30yr_anomaly_annual_model_mpi_esm_lr_remo2009": [
            "hdds_30yr_anomaly_annual_agree_model_ensemble",
            "hdds_30yr_anomaly_annual_model_ec_earth_cclm4_8_17",
            "hdds_30yr_anomaly_annual_model_ec_earth_racmo22e",
            "hdds_30yr_anomaly_annual_model_ec_earth_rca4",
            "hdds_30yr_anomaly_annual_model_hadgem2_es_racmo22e",
        ],
    }


def get_uncertainty_map() -> dict[str, tuple[str, str]]:
    return {
        "hdds_annual_absolute_model_ensemble": (
            "hdds_annual_absolute_model_ensemble_lower_uncertainty",
            "hdds_annual_absolute_model_ensemble_upper_uncertainty",
        ),
    }
