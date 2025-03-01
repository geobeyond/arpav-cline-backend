from ...schemas.static import (
    AggregationPeriod,
    MeasureType,
    ObservationStationManager,
)
from ...schemas.climaticindicators import (
    ClimaticIndicatorCreate,
    ClimaticIndicatorObservationNameCreate,
    ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator,
)


def generate_climatic_indicators(
    forecast_model_ids: dict[str, int],
) -> list[ClimaticIndicatorCreate]:
    return [
        ClimaticIndicatorCreate(
            name="fd",
            historical_coverages_internal_name="FD",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Frost days (FD)",
            display_name_italian="Giorni di gelo (FD)",
            description_english=(
                "Number of days with minimum temperature less than 0ºC"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima minore di 0°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-Blues-inv",
            color_scale_min=0,
            color_scale_max=160,
            data_precision=0,
            sort_order=5,
            observation_names=[
                ClimaticIndicatorObservationNameCreate(
                    observation_station_manager=ObservationStationManager.ARPAV,
                    indicator_observation_name="FD",
                ),
                ClimaticIndicatorObservationNameCreate(
                    observation_station_manager=ObservationStationManager.ARPAFVG,
                    indicator_observation_name="FD",
                ),
            ],
            forecast_models=[
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["model_ensemble"],
                    thredds_url_base_path="ensymbc/clipped",
                    thredds_url_uncertainties_base_path="ensymbc/std/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_cclm_4_8_17"],
                    thredds_url_base_path="EC-EARTH_CCLM4-8-17ymbc/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_racmo22e"],
                    thredds_url_base_path="EC-EARTH_RACMO22Eymbc/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_rca4"],
                    thredds_url_base_path="EC-EARTH_RCA4ymbc/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["hadgem2_racmo22e"],
                    thredds_url_base_path="HadGEM2-ES_RACMO22Eymbc/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["mpi_esm_lr_remo2009"],
                    thredds_url_base_path="MPI-ESM-LR_REMO2009ymbc/clipped",
                ),
            ],
        ),
        ClimaticIndicatorCreate(
            name="fd",
            historical_coverages_internal_name="FD",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Frost days (FD)",
            display_name_italian="Giorni di gelo (FD)",
            description_english=(
                "Number of days with minimum temperature less than 0ºC"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima minore di 0°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/div-RdBu",
            color_scale_min=-60,
            color_scale_max=60,
            data_precision=0,
            sort_order=5,
        ),
        ClimaticIndicatorCreate(
            name="fd",
            historical_coverages_internal_name="FD",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.TEN_YEAR,
            display_name_english="Frost days (FD)",
            display_name_italian="Giorni di gelo (FD)",
            description_english=(
                "Number of days with minimum temperature less than 0ºC"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima minore di 0°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-Blues-inv",
            color_scale_min=0,
            color_scale_max=160,
            data_precision=0,
            sort_order=5,
        ),
        ClimaticIndicatorCreate(
            name="fd",
            historical_coverages_internal_name="FD",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.TEN_YEAR,
            display_name_english="Frost days (FD)",
            display_name_italian="Giorni di gelo (FD)",
            description_english=(
                "Number of days with minimum temperature less than 0ºC"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima minore di 0°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/div-RdBu",
            color_scale_min=-60,
            color_scale_max=60,
            data_precision=0,
            sort_order=5,
        ),
        ClimaticIndicatorCreate(
            name="fd",
            historical_coverages_internal_name="FD",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Frost days (FD)",
            display_name_italian="Giorni di gelo (FD)",
            description_english=(
                "Number of days with minimum temperature less than 0ºC"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima minore di 0°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-Blues-inv",
            color_scale_min=0,
            color_scale_max=160,
            data_precision=0,
            sort_order=5,
        ),
        ClimaticIndicatorCreate(
            name="fd",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Frost days (FD)",
            display_name_italian="Giorni di gelo (FD)",
            description_english=(
                "Number of days with minimum temperature less than 0ºC"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima minore di 0°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="uncert-stippled/seq-YlOrRd-inv",
            color_scale_min=-85,
            color_scale_max=5,
            data_precision=0,
            sort_order=5,
            forecast_models=[
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["model_ensemble"],
                    thredds_url_base_path="ensembletwbc/std/clipped",
                    thredds_url_uncertainties_base_path="ensymbc/std/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_cclm_4_8_17"],
                    thredds_url_base_path="indici5rcm/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_racmo22e"],
                    thredds_url_base_path="indici5rcm/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_rca4"],
                    thredds_url_base_path="indici5rcm/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["hadgem2_racmo22e"],
                    thredds_url_base_path="indici5rcm/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["mpi_esm_lr_remo2009"],
                    thredds_url_base_path="indici5rcm/clipped",
                ),
            ],
        ),
    ]
