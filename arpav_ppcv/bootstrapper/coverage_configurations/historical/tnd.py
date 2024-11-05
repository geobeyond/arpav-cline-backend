from ....schemas.base import (
    CoreConfParamName,
    ObservationAggregationType,
)
from ....schemas.coverages import (
    CoverageConfigurationCreate,
    ConfigurationParameterPossibleValueCreate,
)

_DISPLAY_NAME_ENGLISH = "Minimum temperature"
_DISPLAY_NAME_ITALIAN = "Temperatura minima"
_DESCRIPTION_ENGLISH = "Average of minimum temperatures"
_DESCRIPTION_ITALIAN = "Media delle temperature minime"
_ARCHIVE = "historical"
# _VARIABLE = "tnd"
_UNIT = "ºC"
_COLOR_SCALE_MIN = -5
_COLOR_SCALE_MAX = 20
_RELATED_OBSERVATION_VARIABLE_NAME = "TNd"
_DATA_PRECISION = 1


def generate_configurations(
    conf_param_values,
    variables,
    climatic_indicators: dict[str, int],
) -> list[CoverageConfigurationCreate]:
    return [
        CoverageConfigurationCreate(
            name="tnd_30yr",
            display_name_english=_DISPLAY_NAME_ENGLISH,
            display_name_italian=_DISPLAY_NAME_ITALIAN,
            description_english=_DESCRIPTION_ENGLISH,
            description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="{historical_year_period}_avg",
            wms_main_layer_name="{historical_year_period}_avg",
            thredds_url_pattern="cline_30yr/TNd_{climatological_standard_normal}.nc",
            unit_english=_UNIT,
            palette="default/seq-YlOrRd",
            color_scale_min=_COLOR_SCALE_MIN,
            color_scale_max=_COLOR_SCALE_MAX,
            data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["tasmin-absolute-thirty_year"],
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
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "autumn")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "january")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "february")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "march")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "april")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "may")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "june")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "july")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "august")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "september")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "october")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "november")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "december")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="tnd_annual_yearly",
            display_name_english=_DISPLAY_NAME_ENGLISH,
            display_name_italian=_DISPLAY_NAME_ITALIAN,
            description_english=_DESCRIPTION_ENGLISH,
            description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="TNd",
            wms_main_layer_name="TNd",
            thredds_url_pattern="cline_yr/TNd_{historical_year_period}_*.nc",
            unit_english=_UNIT,
            palette="default/seq-YlOrRd",
            color_scale_min=_COLOR_SCALE_MIN,
            color_scale_max=_COLOR_SCALE_MAX,
            data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["tasmin-absolute-annual"],
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
            observation_variable_id=(
                v.id
                if (v := variables.get(_RELATED_OBSERVATION_VARIABLE_NAME)) is not None
                else None
            ),
            observation_variable_aggregation_type=ObservationAggregationType.YEARLY,
        ),
        CoverageConfigurationCreate(
            name="tnd_annual_seasonal",
            display_name_english=_DISPLAY_NAME_ENGLISH,
            display_name_italian=_DISPLAY_NAME_ITALIAN,
            description_english=_DESCRIPTION_ENGLISH,
            description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="TNd",
            wms_main_layer_name="TNd",
            thredds_url_pattern="cline_yr/TNd_{historical_year_period}_*.nc",
            unit_english=_UNIT,
            palette="default/seq-YlOrRd",
            color_scale_min=_COLOR_SCALE_MIN,
            color_scale_max=_COLOR_SCALE_MAX,
            data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["tasmin-absolute-annual"],
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
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "winter")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "spring")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "summer")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "autumn")
                    ].id
                ),
            ],
            observation_variable_id=(
                v.id
                if (v := variables.get(_RELATED_OBSERVATION_VARIABLE_NAME)) is not None
                else None
            ),
            observation_variable_aggregation_type=ObservationAggregationType.SEASONAL,
        ),
        CoverageConfigurationCreate(
            name="tnd_annual_monthly",
            display_name_english=_DISPLAY_NAME_ENGLISH,
            display_name_italian=_DISPLAY_NAME_ITALIAN,
            description_english=_DESCRIPTION_ENGLISH,
            description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="TNd",
            wms_main_layer_name="TNd",
            thredds_url_pattern="cline_yr/TNd_{historical_year_period}_*.nc",
            unit_english=_UNIT,
            palette="default/seq-YlOrRd",
            color_scale_min=_COLOR_SCALE_MIN,
            color_scale_max=_COLOR_SCALE_MAX,
            data_precision=_DATA_PRECISION,
            climatic_indicator_id=climatic_indicators["tasmin-absolute-annual"],
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
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "february")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "march")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "april")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "may")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "june")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "july")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "august")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "september")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "october")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "november")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        (CoreConfParamName.HISTORICAL_YEAR_PERIOD.value, "december")
                    ].id
                ),
            ],
            observation_variable_id=(
                v.id
                if (v := variables.get(_RELATED_OBSERVATION_VARIABLE_NAME)) is not None
                else None
            ),
            observation_variable_aggregation_type=ObservationAggregationType.MONTHLY,
        ),
    ]
