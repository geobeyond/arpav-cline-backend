from ....schemas.base import (
    CoreConfParamName,
    ObservationAggregationType,
)
from ....schemas.coverages import (
    CoverageConfigurationCreate,
    ConfigurationParameterPossibleValueCreate,
)

_DISPLAY_NAME_ENGLISH = "Tropical nights"
_DISPLAY_NAME_ITALIAN = "Notti tropicali"
_DESCRIPTION_ENGLISH = "Number of days with minimum temperature higher than 20°C"
_DESCRIPTION_ITALIAN = "Numero di giorni con temperatura minima maggiore di 20°C"
_ARCHIVE = "historical"
_VARIABLE = "tr"
_UNIT = "gg"
_COLOR_SCALE_MIN = 0
_COLOR_SCALE_MAX = 50
_RELATED_OBSERVATION_VARIABLE_NAME = "TR"
_DATA_PRECISION = 0


def generate_configurations(
    conf_param_values,
    variables,
    climatic_indicators: dict[str, int],
) -> list[CoverageConfigurationCreate]:
    return [
        CoverageConfigurationCreate(
            name="tr_30yr",
            display_name_english=_DISPLAY_NAME_ENGLISH,
            display_name_italian=_DISPLAY_NAME_ITALIAN,
            description_english=_DESCRIPTION_ENGLISH,
            description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="{historical_year_period}_avg",
            wms_main_layer_name="{historical_year_period}_avg",
            thredds_url_pattern="cline_30yr/TR_{climatological_standard_normal}.nc",
            unit_english=_UNIT,
            palette="default/seq-YlOrRd",
            color_scale_min=_COLOR_SCALE_MIN,
            color_scale_max=_COLOR_SCALE_MAX,
            data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["tr-absolute-thirty_year"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, _ARCHIVE)
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_VARIABLE.value, _VARIABLE)
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.AGGREGATION_PERIOD.value, "30yr")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("climatological_standard_normal", "1991_2020")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.MEASURE.value, "absolute")
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
            name="tr_annual_yearly",
            display_name_english=_DISPLAY_NAME_ENGLISH,
            display_name_italian=_DISPLAY_NAME_ITALIAN,
            description_english=_DESCRIPTION_ENGLISH,
            description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="TR",
            wms_main_layer_name="TR",
            thredds_url_pattern="cline_yr/TR_{historical_year_period}_*.nc",
            unit_english=_UNIT,
            palette="default/seq-YlOrRd",
            color_scale_min=_COLOR_SCALE_MIN,
            color_scale_max=_COLOR_SCALE_MAX,
            data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["tr-absolute-annual"],
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.ARCHIVE.value, _ARCHIVE)
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_VARIABLE.value, _VARIABLE)
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.AGGREGATION_PERIOD.value, "annual")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.MEASURE.value, "absolute")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "all_year")
                    ].id
                ),
            ],
            observation_variable_id=(
                v.id
                if (v := variables.get(_RELATED_OBSERVATION_VARIABLE_NAME)) is not None
                else None
            ),
            observation_variable_aggregation_type=ObservationAggregationType.YEARLY,
        ),
    ]
