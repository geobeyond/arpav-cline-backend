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
            name="tas_seasonal_anomaly_model_ensemble",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="ens5ym/clipped/tas_anom_pp_ts_{scenario}_{year_period}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-annual"],
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
                        (CoreConfParamName.YEAR_PERIOD.value, "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.YEAR_PERIOD.value, "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.YEAR_PERIOD.value, "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.YEAR_PERIOD.value, "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_seasonal_anomaly_model_ec_earth_cclm4_8_17",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="EC-EARTH_CCLM4-8-17ym/clipped/tas_EC-EARTH_CCLM4-8-17_{scenario}_{year_period}_anomaly_pp_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-annual"],
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
                        (CoreConfParamName.YEAR_PERIOD.value, "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.YEAR_PERIOD.value, "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.YEAR_PERIOD.value, "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.YEAR_PERIOD.value, "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_seasonal_anomaly_model_ec_earth_racmo22e",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="EC-EARTH_RACMO22Eym/clipped/tas_EC-EARTH_RACMO22E_{scenario}_{year_period}_anomaly_pp_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-annual"],
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
                        (CoreConfParamName.YEAR_PERIOD.value, "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_seasonal_anomaly_model_ec_earth_rca4",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="EC-EARTH_RCA4ym/clipped/tas_EC-EARTH_RCA4_{scenario}_{year_period}_anomaly_pp_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-annual"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_seasonal_anomaly_model_hadgem2_es_racmo22e",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="HadGEM2-ES_RACMO22Eym/clipped/tas_HadGEM2-ES_RACMO22E_{scenario}_{year_period}_anomaly_pp_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-annual"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_seasonal_anomaly_model_mpi_esm_lr_remo2009",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="MPI-ESM-LR_REMO2009ym/clipped/tas_MPI-ESM-LR_REMO2009_{scenario}_{year_period}_anomaly_pp_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-annual"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_seasonal_anomaly_model_ensemble_upper_uncertainty",
            netcdf_main_dataset_name="tas_stdup",
            wms_main_layer_name="tas_stdup",
            thredds_url_pattern="ens5ym/std/clipped/tas_anom_stdup_pp_ts_{scenario}_{year_period}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-annual"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_seasonal_anomaly_model_ensemble_lower_uncertainty",
            netcdf_main_dataset_name="tas_stddown",
            wms_main_layer_name="tas_stddown",
            thredds_url_pattern="ens5ym/std/clipped/tas_anom_stddown_pp_ts_{scenario}_{year_period}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-annual"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_seasonal_absolute_model_ensemble",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="ensymbc/clipped/tas_avg_{scenario}_{year_period}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_annual_absolute_model_ensemble",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="ensymbc/clipped/tas_avg_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_seasonal_absolute_model_ec_earth_cclm4_8_17",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="EC-EARTH_CCLM4-8-17ymbc/clipped/tas_EC-EARTH_CCLM4-8-17_{scenario}_{year_period}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_annual_absolute_model_ec_earth_cclm4_8_17",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="EC-EARTH_CCLM4-8-17ymbc/clipped/tas_EC-EARTH_CCLM4-8-17_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_seasonal_absolute_model_ec_earth_racmo22e",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="EC-EARTH_RACMO22Eymbc/clipped/tas_EC-EARTH_RACMO22E_{scenario}_{year_period}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_annual_absolute_model_ec_earth_racmo22e",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="EC-EARTH_RACMO22Eymbc/clipped/tas_EC-EARTH_RACMO22E_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_seasonal_absolute_model_ec_earth_rca4",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="EC-EARTH_RCA4ymbc/clipped/tas_EC-EARTH_RCA4_{scenario}_{year_period}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_annual_absolute_model_ec_earth_rca4",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="EC-EARTH_RCA4ymbc/clipped/tas_EC-EARTH_RCA4_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
                        ("year_period", "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_seasonal_absolute_model_hadgem2_es_racmo22e",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="HadGEM2-ES_RACMO22Eymbc/clipped/tas_HadGEM2-ES_RACMO22E_{scenario}_{year_period}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_annual_absolute_model_hadgem2_es_racmo22e",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="HadGEM2-ES_RACMO22Eymbc/clipped/tas_HadGEM2-ES_RACMO22E_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
            name="tas_seasonal_absolute_model_mpi_esm_lr_remo2009",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="MPI-ESM-LR_REMO2009ymbc/clipped/tas_MPI-ESM-LR_REMO2009_{scenario}_{year_period}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_annual_absolute_model_mpi_esm_lr_remo2009",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="MPI-ESM-LR_REMO2009ymbc/clipped/tas_MPI-ESM-LR_REMO2009_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
            name="tas_seasonal_absolute_model_ensemble_upper_uncertainty",
            netcdf_main_dataset_name="tas_stdup",
            wms_main_layer_name="tas_stdup",
            thredds_url_pattern="ensymbc/std/clipped/tas_stdup_{scenario}_{year_period}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_seasonal_absolute_model_ensemble_lower_uncertainty",
            netcdf_main_dataset_name="tas_stddown",
            wms_main_layer_name="tas_stddown",
            thredds_url_pattern="ensymbc/std/clipped/tas_stddown_{scenario}_{year_period}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_annual_absolute_model_ensemble_upper_uncertainty",
            netcdf_main_dataset_name="tas_stdup",
            wms_main_layer_name="tas_stdup",
            thredds_url_pattern="ensymbc/std/clipped/tas_stdup_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
            name="tas_annual_absolute_model_ensemble_lower_uncertainty",
            netcdf_main_dataset_name="tas_stddown",
            wms_main_layer_name="tas_stddown",
            thredds_url_pattern="ensymbc/std/clipped/tas_stddown_{scenario}_ts19762100_ls_VFVG.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
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
            name="tas_30yr_anomaly_seasonal_agree_model_ensemble",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas-uncertainty_group",
            wms_secondary_layer_name="tas",
            thredds_url_pattern="ensembletwbc/std/clipped/tas_avgagree_anom_{time_window}_{scenario}_{year_period}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-thirty_year"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="taspr5rcm/clipped/tas_EC-EARTH_CCLM4-8-17_{scenario}_seas_{time_window}{year_period}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-thirty_year"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_30yr_anomaly_seasonal_model_ec_earth_racmo22e",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="taspr5rcm/clipped/tas_EC-EARTH_RACMO22E_{scenario}_seas_{time_window}{year_period}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-thirty_year"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_30yr_anomaly_seasonal_model_ec_earth_rca4",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="taspr5rcm/clipped/tas_EC-EARTH_RCA4_{scenario}_seas_{time_window}{year_period}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-thirty_year"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="taspr5rcm/clipped/tas_HadGEM2-ES_RACMO22E_{scenario}_seas_{time_window}{year_period}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-thirty_year"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="taspr5rcm/clipped/tas_MPI-ESM-LR_REMO2009_{scenario}_seas_{time_window}{year_period}_VFVGTAA.nc",
            climatic_indicator_id=climatic_indicators["tas-anomaly-thirty_year"],
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
                        ("year_period", "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("year_period", "autumn")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_barometro_climatico",
            netcdf_main_dataset_name="tas",
            wms_main_layer_name="tas",
            thredds_url_pattern="ensymbc/std/clipped/fldmean/tas_avg_{scenario}_ts19762100_ls_VFVG_fldmean.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "barometro_climatico")
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
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_barometro_climatico_lower_uncertainty",
            netcdf_main_dataset_name="tas_stddown",
            wms_main_layer_name="tas_stddown",
            thredds_url_pattern="ensymbc/std/clipped/fldmean/tas_stddown_{scenario}_ts19762100_ls_VFVG_fldmean.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "barometro_climatico")
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
            ],
        ),
        CoverageConfigurationCreate(
            name="tas_barometro_climatico_upper_uncertainty",
            netcdf_main_dataset_name="tas_stdup",
            wms_main_layer_name="tas_stdup",
            thredds_url_pattern="ensymbc/std/clipped/fldmean/tas_stdup_{scenario}_ts19762100_ls_VFVG_fldmean.nc",
            climatic_indicator_id=climatic_indicators["tas-absolute-annual"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, "barometro_climatico")
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
            ],
        ),
    ]


def get_related_map() -> dict[str, list[str]]:
    return {
        "tas_seasonal_anomaly_model_ensemble": [
            "tas_seasonal_anomaly_model_ec_earth_cclm4_8_17",
            "tas_seasonal_anomaly_model_ec_earth_racmo22e",
            "tas_seasonal_anomaly_model_ec_earth_rca4",
            "tas_seasonal_anomaly_model_hadgem2_es_racmo22e",
            "tas_seasonal_anomaly_model_mpi_esm_lr_remo2009",
        ],
        "tas_seasonal_anomaly_model_ec_earth_cclm4_8_17": [
            "tas_seasonal_anomaly_model_ensemble",
            "tas_seasonal_anomaly_model_ec_earth_racmo22e",
            "tas_seasonal_anomaly_model_ec_earth_rca4",
            "tas_seasonal_anomaly_model_hadgem2_es_racmo22e",
            "tas_seasonal_anomaly_model_mpi_esm_lr_remo2009",
        ],
        "tas_seasonal_anomaly_model_ec_earth_racmo22e": [
            "tas_seasonal_anomaly_model_ensemble",
            "tas_seasonal_anomaly_model_ec_earth_cclm4_8_17",
            "tas_seasonal_anomaly_model_ec_earth_rca4",
            "tas_seasonal_anomaly_model_hadgem2_es_racmo22e",
            "tas_seasonal_anomaly_model_mpi_esm_lr_remo2009",
        ],
        "tas_seasonal_anomaly_model_ec_earth_rca4": [
            "tas_seasonal_anomaly_model_ensemble",
            "tas_seasonal_anomaly_model_ec_earth_cclm4_8_17",
            "tas_seasonal_anomaly_model_ec_earth_racmo22e",
            "tas_seasonal_anomaly_model_hadgem2_es_racmo22e",
            "tas_seasonal_anomaly_model_mpi_esm_lr_remo2009",
        ],
        "tas_seasonal_anomaly_model_hadgem2_es_racmo22e": [
            "tas_seasonal_anomaly_model_ensemble",
            "tas_seasonal_anomaly_model_ec_earth_cclm4_8_17",
            "tas_seasonal_anomaly_model_ec_earth_racmo22e",
            "tas_seasonal_anomaly_model_ec_earth_rca4",
            "tas_seasonal_anomaly_model_mpi_esm_lr_remo2009",
        ],
        "tas_seasonal_anomaly_model_mpi_esm_lr_remo2009": [
            "tas_seasonal_anomaly_model_ensemble",
            "tas_seasonal_anomaly_model_ec_earth_cclm4_8_17",
            "tas_seasonal_anomaly_model_ec_earth_racmo22e",
            "tas_seasonal_anomaly_model_ec_earth_rca4",
            "tas_seasonal_anomaly_model_hadgem2_es_racmo22e",
        ],
        "tas_seasonal_absolute_model_ensemble": [
            "tas_seasonal_absolute_model_ec_earth_cclm4_8_17",
            "tas_seasonal_absolute_model_ec_earth_racmo22e",
            "tas_seasonal_absolute_model_ec_earth_rca4",
            "tas_seasonal_absolute_model_hadgem2_es_racmo22e",
            "tas_seasonal_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tas_seasonal_absolute_model_ec_earth_cclm4_8_17": [
            "tas_seasonal_absolute_model_ensemble",
            "tas_seasonal_absolute_model_ec_earth_racmo22e",
            "tas_seasonal_absolute_model_ec_earth_rca4",
            "tas_seasonal_absolute_model_hadgem2_es_racmo22e",
            "tas_seasonal_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tas_seasonal_absolute_model_ec_earth_racmo22e": [
            "tas_seasonal_absolute_model_ensemble",
            "tas_seasonal_absolute_model_ec_earth_cclm4_8_17",
            "tas_seasonal_absolute_model_ec_earth_rca4",
            "tas_seasonal_absolute_model_hadgem2_es_racmo22e",
            "tas_seasonal_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tas_seasonal_absolute_model_ec_earth_rca4": [
            "tas_seasonal_absolute_model_ensemble",
            "tas_seasonal_absolute_model_ec_earth_cclm4_8_17",
            "tas_seasonal_absolute_model_ec_earth_racmo22e",
            "tas_seasonal_absolute_model_hadgem2_es_racmo22e",
            "tas_seasonal_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tas_seasonal_absolute_model_hadgem2_es_racmo22e": [
            "tas_seasonal_absolute_model_ensemble",
            "tas_seasonal_absolute_model_ec_earth_cclm4_8_17",
            "tas_seasonal_absolute_model_ec_earth_racmo22e",
            "tas_seasonal_absolute_model_ec_earth_rca4",
            "tas_seasonal_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tas_seasonal_absolute_model_mpi_esm_lr_remo2009": [
            "tas_seasonal_absolute_model_ensemble",
            "tas_seasonal_absolute_model_ec_earth_cclm4_8_17",
            "tas_seasonal_absolute_model_ec_earth_racmo22e",
            "tas_seasonal_absolute_model_ec_earth_rca4",
            "tas_seasonal_absolute_model_hadgem2_es_racmo22e",
        ],
        "tas_annual_absolute_model_ensemble": [
            "tas_annual_absolute_model_ec_earth_cclm4_8_17",
            "tas_annual_absolute_model_ec_earth_racmo22e",
            "tas_annual_absolute_model_ec_earth_rca4",
            "tas_annual_absolute_model_hadgem2_es_racmo22e",
            "tas_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tas_annual_absolute_model_ec_earth_cclm4_8_17": [
            "tas_annual_absolute_model_ensemble",
            "tas_annual_absolute_model_ec_earth_racmo22e",
            "tas_annual_absolute_model_ec_earth_rca4",
            "tas_annual_absolute_model_hadgem2_es_racmo22e",
            "tas_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tas_annual_absolute_model_ec_earth_racmo22e": [
            "tas_annual_absolute_model_ensemble",
            "tas_annual_absolute_model_ec_earth_cclm4_8_17",
            "tas_annual_absolute_model_ec_earth_rca4",
            "tas_annual_absolute_model_hadgem2_es_racmo22e",
            "tas_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tas_annual_absolute_model_ec_earth_rca4": [
            "tas_annual_absolute_model_ensemble",
            "tas_annual_absolute_model_ec_earth_cclm4_8_17",
            "tas_annual_absolute_model_ec_earth_racmo22e",
            "tas_annual_absolute_model_hadgem2_es_racmo22e",
            "tas_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tas_annual_absolute_model_hadgem2_es_racmo22e": [
            "tas_annual_absolute_model_ensemble",
            "tas_annual_absolute_model_ec_earth_cclm4_8_17",
            "tas_annual_absolute_model_ec_earth_racmo22e",
            "tas_annual_absolute_model_ec_earth_rca4",
            "tas_annual_absolute_model_mpi_esm_lr_remo2009",
        ],
        "tas_annual_absolute_model_mpi_esm_lr_remo2009": [
            "tas_annual_absolute_model_ensemble",
            "tas_annual_absolute_model_ec_earth_cclm4_8_17",
            "tas_annual_absolute_model_ec_earth_racmo22e",
            "tas_annual_absolute_model_ec_earth_rca4",
            "tas_annual_absolute_model_hadgem2_es_racmo22e",
        ],
        "tas_30yr_anomaly_seasonal_agree_model_ensemble": [
            "tas_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17",
            "tas_30yr_anomaly_seasonal_model_ec_earth_racmo22e",
            "tas_30yr_anomaly_seasonal_model_ec_earth_rca4",
            "tas_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e",
            "tas_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009",
        ],
        "tas_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17": [
            "tas_30yr_anomaly_seasonal_agree_model_ensemble",
            "tas_30yr_anomaly_seasonal_model_ec_earth_racmo22e",
            "tas_30yr_anomaly_seasonal_model_ec_earth_rca4",
            "tas_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e",
            "tas_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009",
        ],
        "tas_30yr_anomaly_seasonal_model_ec_earth_racmo22e": [
            "tas_30yr_anomaly_seasonal_agree_model_ensemble",
            "tas_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17",
            "tas_30yr_anomaly_seasonal_model_ec_earth_rca4",
            "tas_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e",
            "tas_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009",
        ],
        "tas_30yr_anomaly_seasonal_model_ec_earth_rca4": [
            "tas_30yr_anomaly_seasonal_agree_model_ensemble",
            "tas_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17",
            "tas_30yr_anomaly_seasonal_model_ec_earth_racmo22e",
            "tas_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e",
            "tas_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009",
        ],
        "tas_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e": [
            "tas_30yr_anomaly_seasonal_agree_model_ensemble",
            "tas_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17",
            "tas_30yr_anomaly_seasonal_model_ec_earth_racmo22e",
            "tas_30yr_anomaly_seasonal_model_ec_earth_rca4",
            "tas_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009",
        ],
        "tas_30yr_anomaly_seasonal_model_mpi_esm_lr_remo2009": [
            "tas_30yr_anomaly_seasonal_agree_model_ensemble",
            "tas_30yr_anomaly_seasonal_model_ec_earth_cclm4_8_17",
            "tas_30yr_anomaly_seasonal_model_ec_earth_racmo22e",
            "tas_30yr_anomaly_seasonal_model_ec_earth_rca4",
            "tas_30yr_anomaly_seasonal_model_hadgem2_es_racmo22e",
        ],
    }


def get_uncertainty_map() -> dict[str, tuple[str, str]]:
    return {
        "tas_seasonal_anomaly_model_ensemble": (
            "tas_seasonal_anomaly_model_ensemble_lower_uncertainty",
            "tas_seasonal_anomaly_model_ensemble_upper_uncertainty",
        ),
        "tas_seasonal_absolute_model_ensemble": (
            "tas_seasonal_absolute_model_ensemble_lower_uncertainty",
            "tas_seasonal_absolute_model_ensemble_upper_uncertainty",
        ),
        "tas_annual_absolute_model_ensemble": (
            "tas_annual_absolute_model_ensemble_lower_uncertainty",
            "tas_annual_absolute_model_ensemble_upper_uncertainty",
        ),
        "tas_barometro_climatico": (
            "tas_barometro_climatico_lower_uncertainty",
            "tas_barometro_climatico_upper_uncertainty",
        ),
    }
