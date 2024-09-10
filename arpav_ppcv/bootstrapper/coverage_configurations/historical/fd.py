from ....schemas.base import ObservationAggregationType
from ....schemas.coverages import (
    CoverageConfigurationCreate,
    ConfigurationParameterPossibleValueCreate,
)

_DISPLAY_NAME_ENGLISH = "Frosty days"
_DISPLAY_NAME_ITALIAN = "Giorni di gelo"
_DESCRIPTION_ENGLISH = "Number of days with minimum temperature below 0°C"
_DESCRIPTION_ITALIAN = "Numero di giorni con temperatura minima minore di 0°C"
_HISTORICAL_COLLECTION = "historical"
_OBSERVATION_VARIABLE = "fd"
_UNIT = "gg"
_COLOR_SCALE_MIN = 0
_COLOR_SCALE_MAX = 260
_RELATED_OBSERVATION_VARIABLE_NAME = "FD"


def generate_configurations(
    conf_param_values, variables
) -> list[CoverageConfigurationCreate]:
    cov_confs = [
        CoverageConfigurationCreate(
            name="fd_30yr_yearly",
            display_name_english=_DISPLAY_NAME_ENGLISH,
            display_name_italian=_DISPLAY_NAME_ITALIAN,
            description_english=_DESCRIPTION_ENGLISH,
            description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="{observation_year_period}_avg",
            wms_main_layer_name="{observation_year_period}_avg",
            thredds_url_pattern="cline_30yr/FD_1991-2020.nc",
            unit=_UNIT,
            palette="default/seq-YlOrRd",
            color_scale_min=_COLOR_SCALE_MIN,
            color_scale_max=_COLOR_SCALE_MAX,
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("collection", _HISTORICAL_COLLECTION)
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("observation_variable", _OBSERVATION_VARIABLE)
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("aggregation_period", "30yr")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("measure", "absolute")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("observation_year_period", "A00")
                    ].id
                ),
            ],
        ),
        CoverageConfigurationCreate(
            name="fd_annual_yearly",
            display_name_english=_DISPLAY_NAME_ENGLISH,
            display_name_italian=_DISPLAY_NAME_ITALIAN,
            description_english=_DESCRIPTION_ENGLISH,
            description_italian=_DESCRIPTION_ITALIAN,
            netcdf_main_dataset_name="FD",
            wms_main_layer_name="FD",
            thredds_url_pattern="cline_yr/FD_{observation_year_period}_1992-2023_py85.nc",
            unit=_UNIT,
            palette="default/seq-YlOrRd",
            color_scale_min=_COLOR_SCALE_MIN,
            color_scale_max=_COLOR_SCALE_MAX,
            possible_values=[
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("collection", _HISTORICAL_COLLECTION)
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("observation_variable", _OBSERVATION_VARIABLE)
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("aggregation_period", "annual")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("measure", "absolute")
                    ].id
                ),
                ConfigurationParameterPossibleValueCreate(
                    configuration_parameter_value_id=conf_param_values[
                        ("observation_year_period", "A00")
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
    for season_name, season_id, duration in (
        ("winter", "S01", "1992-2024"),
        ("spring", "S02", "1992-2024"),
        ("autumn", "S04", "1992-2023"),
    ):
        cov_confs.extend(
            [
                CoverageConfigurationCreate(
                    name=f"fd_30yr_{season_name}",
                    display_name_english=_DISPLAY_NAME_ENGLISH,
                    display_name_italian=_DISPLAY_NAME_ITALIAN,
                    description_english=_DESCRIPTION_ENGLISH,
                    description_italian=_DESCRIPTION_ITALIAN,
                    netcdf_main_dataset_name="{observation_year_period}_avg",
                    wms_main_layer_name="{observation_year_period}_avg",
                    thredds_url_pattern="cline_30yr/FD_1991-2020.nc",
                    unit=_UNIT,
                    palette="default/seq-YlOrRd",
                    color_scale_min=_COLOR_SCALE_MIN,
                    color_scale_max=_COLOR_SCALE_MAX,
                    possible_values=[
                        ConfigurationParameterPossibleValueCreate(
                            configuration_parameter_value_id=conf_param_values[
                                ("collection", _HISTORICAL_COLLECTION)
                            ].id
                        ),
                        ConfigurationParameterPossibleValueCreate(
                            configuration_parameter_value_id=conf_param_values[
                                ("observation_variable", _OBSERVATION_VARIABLE)
                            ].id
                        ),
                        ConfigurationParameterPossibleValueCreate(
                            configuration_parameter_value_id=conf_param_values[
                                ("aggregation_period", "30yr")
                            ].id
                        ),
                        ConfigurationParameterPossibleValueCreate(
                            configuration_parameter_value_id=conf_param_values[
                                ("measure", "absolute")
                            ].id
                        ),
                        ConfigurationParameterPossibleValueCreate(
                            configuration_parameter_value_id=conf_param_values[
                                ("observation_year_period", season_id)
                            ].id
                        ),
                    ],
                ),
            ]
        )
    for month_name, month_id, duration in (
        ("january", "M01", "1992-2024"),
        ("february", "M02", "1992-2024"),
        ("march", "M03", "1992-2024"),
        ("april", "M04", "1992-2024"),
        ("october", "M10", "1992-2023"),
        ("november", "M11", "1992-2023"),
        ("december", "M12", "1992-2023"),
    ):
        cov_confs.extend(
            [
                CoverageConfigurationCreate(
                    name=f"fd_30yr_{month_name}",
                    display_name_english=_DISPLAY_NAME_ENGLISH,
                    display_name_italian=_DISPLAY_NAME_ITALIAN,
                    description_english=_DESCRIPTION_ENGLISH,
                    description_italian=_DESCRIPTION_ITALIAN,
                    netcdf_main_dataset_name="{observation_year_period}_avg",
                    wms_main_layer_name="{observation_year_period}_avg",
                    thredds_url_pattern="cline_30yr/FD_1991-2020.nc",
                    unit=_UNIT,
                    palette="default/seq-YlOrRd",
                    color_scale_min=_COLOR_SCALE_MIN,
                    color_scale_max=_COLOR_SCALE_MAX,
                    possible_values=[
                        ConfigurationParameterPossibleValueCreate(
                            configuration_parameter_value_id=conf_param_values[
                                ("collection", _HISTORICAL_COLLECTION)
                            ].id
                        ),
                        ConfigurationParameterPossibleValueCreate(
                            configuration_parameter_value_id=conf_param_values[
                                ("observation_variable", _OBSERVATION_VARIABLE)
                            ].id
                        ),
                        ConfigurationParameterPossibleValueCreate(
                            configuration_parameter_value_id=conf_param_values[
                                ("aggregation_period", "30yr")
                            ].id
                        ),
                        ConfigurationParameterPossibleValueCreate(
                            configuration_parameter_value_id=conf_param_values[
                                ("measure", "absolute")
                            ].id
                        ),
                        ConfigurationParameterPossibleValueCreate(
                            configuration_parameter_value_id=conf_param_values[
                                ("observation_year_period", month_id)
                            ].id
                        ),
                    ],
                ),
            ]
        )
    return cov_confs
