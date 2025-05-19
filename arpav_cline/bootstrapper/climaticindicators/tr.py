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
            name="tr",
            historical_coverages_internal_name="TR",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Tropical nights (TR)",
            display_name_italian="Notti tropicali (TR)",
            description_english=(
                "Number of nights with minimum temperature larger than 20°C"
            ),
            description_italian=(
                "Numero di notti con temperatura minima maggiore di 20°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=65,
            data_precision=1,
            sort_order=3,
            observation_names=[
                ClimaticIndicatorObservationNameCreate(
                    observation_station_manager=ObservationStationManager.ARPAV,
                    indicator_observation_name="TR",
                ),
                ClimaticIndicatorObservationNameCreate(
                    observation_station_manager=ObservationStationManager.ARPAFVG,
                    indicator_observation_name="TR",
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
            name="tr",
            historical_coverages_internal_name="TR",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Tropical nights (TR)",
            display_name_italian="Notti tropicali (TR)",
            description_english=(
                "Number of nights with minimum temperature larger than 20°C"
            ),
            description_italian=(
                "Numero di notti con temperatura minima maggiore di 20°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/div-RdBu-inv",
            color_scale_min=-40,
            color_scale_max=40,
            data_precision=1,
            sort_order=3,
        ),
        ClimaticIndicatorCreate(
            name="tr",
            historical_coverages_internal_name="TR",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.TEN_YEAR,
            display_name_english="Tropical nights (TR)",
            display_name_italian="Notti tropicali (TR)",
            description_english=(
                "Number of nights with minimum temperature larger than 20°C"
            ),
            description_italian=(
                "Numero di notti con temperatura minima maggiore di 20°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=65,
            data_precision=1,
            sort_order=3,
        ),
        ClimaticIndicatorCreate(
            name="tr",
            historical_coverages_internal_name="TR",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.TEN_YEAR,
            display_name_english="Tropical nights (TR)",
            display_name_italian="Notti tropicali (TR)",
            description_english=(
                "Number of nights with minimum temperature larger than 20°C"
            ),
            description_italian=(
                "Numero di notti con temperatura minima maggiore di 20°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/div-RdBu-inv",
            color_scale_min=-50,
            color_scale_max=50,
            data_precision=1,
            sort_order=3,
        ),
        ClimaticIndicatorCreate(
            name="tr",
            historical_coverages_internal_name="TR",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Tropical nights (TR)",
            display_name_italian="Notti tropicali (TR)",
            description_english=(
                "Number of nights with minimum temperature larger than 20°C"
            ),
            description_italian=(
                "Numero di notti con temperatura minima maggiore di 20°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=65,
            data_precision=1,
            sort_order=3,
        ),
        ClimaticIndicatorCreate(
            name="tr",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Tropical nights (TR)",
            display_name_italian="Notti tropicali (TR)",
            description_english=(
                "Number of days with minimum temperature larger than 20°C"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima maggiore di 20°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="uncert-stippled/seq-YlOrRd",
            color_scale_min=-5,
            color_scale_max=75,
            data_precision=1,
            sort_order=3,
            forecast_models=[
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["model_ensemble"],
                    thredds_url_base_path="ensembletwbc/std/clipped",
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
