from arpav_cline import db
from arpav_cline.schemas import (
    climaticindicators,
    static,
)


def test_update_climatic_indicator_only_changes_specified_property(
    arpav_db_session,
    sample_real_forecast_models,
):
    """Test that when a simple property is updated, the related objects are not modified."""
    old_color_scale_min = 1.2
    new_color_scale_min = 30
    indicator_create = climaticindicators.ClimaticIndicatorCreate(
        name="fake_climatic_indicator_name",
        historical_coverages_internal_name="fake_historical_coverages_internal_name",
        measure_type=static.MeasureType.ABSOLUTE,
        aggregation_period=static.AggregationPeriod.ANNUAL,
        display_name_english="fake_indicator",
        display_name_italian="fake_indicator_italian",
        description_english="fake_description",
        description_italian="fake_description_italian",
        unit_english="fake_unit",
        unit_italian="fake_unit_italian",
        palette="fake_palette",
        color_scale_min=old_color_scale_min,
        color_scale_max=20.1,
        data_precision=2,
        sort_order=40,
        observation_names=[
            climaticindicators.ClimaticIndicatorObservationNameCreate(
                observation_station_manager=static.ObservationStationManager.ARPAV,
                indicator_observation_name="fake_indicator_observation_name",
            )
        ],
        forecast_models=[
            climaticindicators.ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
                forecast_model_id=fm.id,
                thredds_url_base_path=f"fake_thredds_url_base_path_{fm.name}",
                thredds_url_uncertainties_base_path=f"fake_thredds_url_uncertainties_base_path_{fm.name}",
            )
            for fm in sample_real_forecast_models
        ],
    )
    created_indicator = db.create_climatic_indicator(arpav_db_session, indicator_create)
    indicator_update = climaticindicators.ClimaticIndicatorUpdate(
        color_scale_min=new_color_scale_min,
    )
    result = db.update_climatic_indicator(
        arpav_db_session, created_indicator, indicator_update
    )
    assert result.name == indicator_create.name
    assert (
        result.historical_coverages_internal_name
        == indicator_create.historical_coverages_internal_name
    )
    assert result.measure_type == indicator_create.measure_type
    assert result.aggregation_period == indicator_create.aggregation_period
    assert result.display_name_english == indicator_create.display_name_english
    assert result.display_name_italian == indicator_create.display_name_italian
    assert result.description_english == indicator_create.description_english
    assert result.description_italian == indicator_create.description_italian
    assert result.unit_english == indicator_create.unit_english
    assert result.unit_italian == indicator_create.unit_italian
    assert result.palette == indicator_create.palette
    assert result.color_scale_min == new_color_scale_min
    assert result.color_scale_max == indicator_create.color_scale_max
    assert result.data_precision == indicator_create.data_precision
    assert result.sort_order == indicator_create.sort_order
    assert (
        result.observation_names[0].station_manager
        == indicator_create.observation_names[0].observation_station_manager
    )
    assert (
        result.observation_names[0].indicator_observation_name
        == indicator_create.observation_names[0].indicator_observation_name
    )
    for existing_fm in result.forecast_model_links:
        to_create_fm = [
            tc
            for tc in indicator_create.forecast_models
            if tc.forecast_model_id == existing_fm.forecast_model_id
        ][0]
        assert existing_fm.thredds_url_base_path == to_create_fm.thredds_url_base_path
        assert (
            existing_fm.thredds_url_uncertainties_base_path
            == to_create_fm.thredds_url_uncertainties_base_path
        )
