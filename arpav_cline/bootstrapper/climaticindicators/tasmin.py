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
            name="tasmin",
            historical_coverages_internal_name="TNd",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Minimum temperature (TASMIN)",
            display_name_italian="Temperatura minima (TASMIN)",
            description_english=("Daily minimum air temperature close to the ground"),
            description_italian=(
                "Temperatura minima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=-3,
            color_scale_max=32,
            data_precision=1,
            sort_order=1,
            observation_names=[
                ClimaticIndicatorObservationNameCreate(
                    observation_station_manager=ObservationStationManager.ARPAV,
                    indicator_observation_name="TNd",
                ),
                ClimaticIndicatorObservationNameCreate(
                    observation_station_manager=ObservationStationManager.ARPAFVG,
                    indicator_observation_name="TASMIN",
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
            name="tasmin",
            historical_coverages_internal_name="TNd",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Minimum temperature (TASMIN)",
            display_name_italian="Temperatura minima (TASMIN)",
            description_english=("Daily minimum air temperature close to the ground"),
            description_italian=(
                "Temperatura minima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/div-RdBu-inv",
            color_scale_min=-5,
            color_scale_max=5,
            data_precision=1,
            sort_order=1,
        ),
        ClimaticIndicatorCreate(
            name="tasmin",
            historical_coverages_internal_name="TNd",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.TEN_YEAR,
            display_name_english="Minimum temperature (TASMIN)",
            display_name_italian="Temperatura minima (TASMIN)",
            description_english=("Daily minimum air temperature close to the ground"),
            description_italian=(
                "Temperatura minima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=-10,
            color_scale_max=26,
            data_precision=1,
            sort_order=1,
        ),
        ClimaticIndicatorCreate(
            name="tasmin",
            historical_coverages_internal_name="TNd",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.TEN_YEAR,
            display_name_english="Minimum temperature (TASMIN)",
            display_name_italian="Temperatura minima (TASMIN)",
            description_english=("Daily minimum air temperature close to the ground"),
            description_italian=(
                "Temperatura minima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/div-RdBu-inv",
            color_scale_min=-5,
            color_scale_max=5,
            data_precision=1,
            sort_order=1,
        ),
        ClimaticIndicatorCreate(
            name="tasmin",
            historical_coverages_internal_name="TNd",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Minimum temperature (TASMIN)",
            display_name_italian="Temperatura minima (TASMIN)",
            description_english=("Daily minimum air temperature close to the ground"),
            description_italian=(
                "Temperatura minima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=-10,
            color_scale_max=26,
            data_precision=1,
            sort_order=1,
        ),
        ClimaticIndicatorCreate(
            name="tasmin",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Minimum temperature (TASMIN)",
            display_name_italian="Temperatura minima (TASMIN)",
            description_english=("Daily minimum air temperature close to the ground"),
            description_italian=(
                "Temperatura minima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="uncert-stippled/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=6,
            data_precision=1,
            sort_order=1,
            forecast_models=[
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["model_ensemble"],
                    thredds_url_base_path="ensembletwbc/std/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_cclm_4_8_17"],
                    thredds_url_base_path="taspr5rcm/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_racmo22e"],
                    thredds_url_base_path="taspr5rcm/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["ec_earth_rca4"],
                    thredds_url_base_path="taspr5rcm/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["hadgem2_racmo22e"],
                    thredds_url_base_path="taspr5rcm/clipped",
                ),
                ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                    forecast_model_id=forecast_model_ids["mpi_esm_lr_remo2009"],
                    thredds_url_base_path="taspr5rcm/clipped",
                ),
            ],
        ),
    ]
