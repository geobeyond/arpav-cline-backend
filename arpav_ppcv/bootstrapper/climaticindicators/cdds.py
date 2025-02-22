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
            name="cdds",
            historical_coverages_internal_name="CDD_jrc",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Cooling degree days (CDDs)",
            display_name_italian="Gradi giorno di raffrescamento (CDDs)",
            description_english=(
                "Sum of the average daily temperature minus 21°C if the "
                "average daily temperature is larger than 24°C"
            ),
            description_italian=(
                "Somma della temperatura media giornaliera meno 21°C se la "
                "temperatura media giornaliera è maggiore di 24°C"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/div-RdBu-inv",
            color_scale_min=-300,
            color_scale_max=300,
            data_precision=0,
            sort_order=8,
        ),
        ClimaticIndicatorCreate(
            name="cdds",
            historical_coverages_internal_name="CDD_jrc",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Cooling degree days (CDDs)",
            display_name_italian="Gradi giorno di raffrescamento (CDDs)",
            description_english=(
                "Sum of the average daily temperature minus 21°C if the "
                "average daily temperature is larger than 24°C"
            ),
            description_italian=(
                "Somma della temperatura media giornaliera meno 21°C se la "
                "temperatura media giornaliera è maggiore di 24°C"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=650,
            data_precision=0,
            sort_order=8,
            observation_names=[
                ClimaticIndicatorObservationNameCreate(
                    observation_station_manager=ObservationStationManager.ARPAV,
                    indicator_observation_name="CDD_jrc",
                )
            ],
            forecast_models=[
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["model_ensemble"],
                    thredds_url_base_path="ensymbc/clipped_noppcne",
                    thredds_url_uncertainties_base_path="ensymbc/std/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_cclm_4_8_17"],
                    thredds_url_base_path="EC-EARTH_CCLM4-8-17ymbc/clipped_noppcne",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_racmo22e"],
                    thredds_url_base_path="EC-EARTH_RACMO22Eymbc/clipped_noppcne",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_rca4"],
                    thredds_url_base_path="EC-EARTH_RCA4ymbc/clipped_noppcne",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["hadgem2_racmo22e"],
                    thredds_url_base_path="HadGEM2-ES_RACMO22Eymbc/clipped_noppcne",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["mpi_esm_lr_remo2009"],
                    thredds_url_base_path="MPI-ESM-LR_REMO2009ymbc/clipped_noppcne",
                ),
            ],
        ),
        ClimaticIndicatorCreate(
            name="cdds",
            historical_coverages_internal_name="CDD_jrc",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.TEN_YEAR,
            display_name_english="Cooling degree days (CDDs)",
            display_name_italian="Gradi giorno di raffrescamento (CDDs)",
            description_english=(
                "Sum of the average daily temperature minus 21°C if the "
                "average daily temperature is larger than 24°C"
            ),
            description_italian=(
                "Somma della temperatura media giornaliera meno 21°C se la "
                "temperatura media giornaliera è maggiore di 24°C"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/div-RdBu-inv",
            color_scale_min=-300,
            color_scale_max=300,
            data_precision=0,
            sort_order=8,
        ),
        ClimaticIndicatorCreate(
            name="cdds",
            historical_coverages_internal_name="CDD_jrc",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.TEN_YEAR,
            display_name_english="Cooling degree days (CDDs)",
            display_name_italian="Gradi giorno di raffrescamento (CDDs)",
            description_english=(
                "Sum of the average daily temperature minus 21°C if the "
                "average daily temperature is larger than 24°C"
            ),
            description_italian=(
                "Somma della temperatura media giornaliera meno 21°C se la "
                "temperatura media giornaliera è maggiore di 24°C"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=650,
            data_precision=0,
            sort_order=8,
        ),
        ClimaticIndicatorCreate(
            name="cdds",
            historical_coverages_internal_name="CDD_jrc",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Cooling degree days (CDDs)",
            display_name_italian="Gradi giorno di raffrescamento (CDDs)",
            description_english=(
                "Sum of the average daily temperature minus 21°C if the "
                "average daily temperature is larger than 24°C"
            ),
            description_italian=(
                "Somma della temperatura media giornaliera meno 21°C se la "
                "temperatura media giornaliera è maggiore di 24°C"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=650,
            data_precision=0,
            sort_order=8,
        ),
        ClimaticIndicatorCreate(
            name="cdds",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Cooling degree days (CDDs)",
            display_name_italian="Gradi giorno di raffrescamento (CDDs)",
            description_english=(
                "Sum of the average daily temperature minus 21°C if the "
                "average daily temperature is larger than 24°C"
            ),
            description_italian=(
                "Somma della temperatura media giornaliera meno 21°C se la "
                "temperatura media giornaliera è maggiore di 24°C"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="uncert-stippled/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=1000,
            data_precision=0,
            sort_order=8,
            forecast_models=[
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["model_ensemble"],
                    thredds_url_base_path="ensembletwbc/std/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_cclm_4_8_17"],
                    thredds_url_base_path="indici5rcm/clipped_noppcne",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_racmo22e"],
                    thredds_url_base_path="indici5rcm/clipped_noppcne",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_rca4"],
                    thredds_url_base_path="indici5rcm/clipped_noppcne",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["hadgem2_racmo22e"],
                    thredds_url_base_path="indici5rcm/clipped_noppcne",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["mpi_esm_lr_remo2009"],
                    thredds_url_base_path="indici5rcm/clipped_noppcne",
                ),
            ],
        ),
    ]
