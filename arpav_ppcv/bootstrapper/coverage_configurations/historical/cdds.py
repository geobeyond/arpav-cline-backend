from ....schemas.base import CoreConfParamName
from ....schemas.coverages import (
    CoverageConfigurationCreate,
    ConfigurationParameterPossibleValueCreate,
)

_DISPLAY_NAME_ENGLISH = "Cooling degree days"
_DISPLAY_NAME_ITALIAN = "Gradi giorno di raffrescamento"
_DESCRIPTION_ENGLISH = (
    "Sum of the average daily temperature minus 21°C if the average "
    "daily temperature is greater than 24°C."
)
_DESCRIPTION_ITALIAN = (
    "Somma della temperatura media giornaliera meno 21°C se la "
    "temperatura media giornaliera è maggiore di 24°C."
)
_ARCHIVE = "historical"
# _VARIABLE = "cdds"
_UNIT = "ºC"
_COLOR_SCALE_MIN = 0
_COLOR_SCALE_MAX = 320
_DATA_PRECISION = 0


def generate_configurations(
    conf_param_values,
    variables,
    climatic_indicators: dict[str, int],
) -> list[CoverageConfigurationCreate]:
    cov_confs = [
        CoverageConfigurationCreate(
            name="cdds_30yr",
            display_name_english=_DISPLAY_NAME_ENGLISH,
            display_name_italian=_DISPLAY_NAME_ITALIAN,
            description_english=_DESCRIPTION_ENGLISH,
            description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="{historical_year_period}_avg",
            wms_main_layer_name="{historical_year_period}_avg",
            thredds_url_pattern="cline_30yr/CDD_jrc_{climatological_standard_normal}.nc",
            unit_english=_UNIT,
            palette="default/seq-YlOrRd",
            color_scale_min=_COLOR_SCALE_MIN,
            color_scale_max=_COLOR_SCALE_MAX,
            data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["cdds-absolute-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, _ARCHIVE)
                    ].id
                ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.HISTORICAL_VARIABLE.value, _VARIABLE)
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.AGGREGATION_PERIOD.value, "30yr")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.MEASURE.value, "absolute")
                #     ].id
                # ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("climatological_standard_normal", "1991_2020")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "all_year")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="cdds_annual_yearly",
            display_name_english=_DISPLAY_NAME_ENGLISH,
            display_name_italian=_DISPLAY_NAME_ITALIAN,
            description_english=_DESCRIPTION_ENGLISH,
            description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="CDD_jrc",
            wms_main_layer_name="CDD_jrc",
            thredds_url_pattern="cline_yr/CDD_jrc_{historical_year_period}_*.nc",
            unit_english=_UNIT,
            palette="default/seq-YlOrRd",
            color_scale_min=_COLOR_SCALE_MIN,
            color_scale_max=_COLOR_SCALE_MAX,
            data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["cdds-absolute-annual"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, _ARCHIVE)
                    ].id
                ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.HISTORICAL_VARIABLE.value, _VARIABLE)
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.AGGREGATION_PERIOD.value, "annual")
                #     ].id
                # ),
                # ConfigurationParameterPossibleValueCreate(
                #     configuration_parameter_value_id=conf_param_values[
                #         (CoreConfParamName.MEASURE.value, "absolute")
                #     ].id
                # ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "all_year")
                    ].id
                ),
            ],
        ),
    ]
    return cov_confs
