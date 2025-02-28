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
            name="snwdays",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Snow days (SNWDAYS)",
            display_name_italian="Giorni con neve nuova (SNWDAYS)",
            description_english=(
                "Number of days with average temperature less than 2°C and "
                "daily precipitation larger than 1 mm"
            ),
            description_italian=(
                "Numero di giorni con temperatura media minore di 2°C e "
                "precipitazione giornaliera maggiore di 1 mm"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-BuYl-inv",
            color_scale_min=0,
            color_scale_max=100,
            data_precision=0,
            sort_order=12,
            observation_names=[
                ClimaticIndicatorObservationNameCreate(
                    observation_station_manager=ObservationStationManager.ARPAFVG,
                    indicator_observation_name="SNWDAYS",
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
            name="snwdays",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Snow days (SNWDAYS)",
            display_name_italian="Giorni con neve nuova (SNWDAYS)",
            description_english=(
                "Number of days with average temperature less than 2°C and "
                "daily precipitation larger than 1 mm"
            ),
            description_italian=(
                "Numero di giorni con temperatura media minore di 2°C e "
                "precipitazione giornaliera maggiore di 1 mm"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="uncert-stippled/seq-YlOrBr-inv",
            color_scale_min=-50,
            color_scale_max=50,
            data_precision=0,
            sort_order=12,
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
