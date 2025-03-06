import random
import typing

import httpx
import pytest
import sqlmodel

from arpav_cline import db

if typing.TYPE_CHECKING:
    from arpav_cline.schemas import coverages

random.seed(0)


def test_coverage_configurations_list(
    test_client_v2_app: httpx.Client,
    sample_real_forecast_coverage_configurations: list[
        "coverages.ForecastCoverageConfiguration"
    ],
):
    list_response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for("legacy_list_coverage_configurations"),
        headers={"accept": "application/json"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == min(
        20, len(sample_real_forecast_coverage_configurations)
    )


def test_coverage_identifiers_list(
    test_client_v2_app: httpx.Client,
    sample_real_forecast_coverage_configurations: list[
        "coverages.ForecastCoverageConfiguration"
    ],
):
    list_response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for("legacy_list_coverages"),
        headers={"accept": "application/json"},
    )
    assert list_response.status_code == 200


@pytest.mark.parametrize(
    "climatological_variable, expected_total, expected_total_filtered",
    [
        pytest.param(None, 2385, 1728),
        pytest.param("tas", 2385, 306),
        pytest.param("su30", 2385, 54),
    ],
)
def test_real_forecast_coverages_list_climatological_variable_filter(
    test_client_v2_app: httpx.Client,
    arpav_db_session: sqlmodel.Session,
    sample_real_forecast_coverage_configurations: list[
        "coverages.ForecastCoverageConfiguration"
    ],
    sample_real_historical_coverage_configurations: list[
        "coverages.HistoricalCoverageConfiguration"
    ],
    climatological_variable: typing.Optional[str],
    expected_total,
    expected_total_filtered,
):
    request_params = {"possible_value": ["archive:forecast"]}
    if climatological_variable is not None:
        request_params["possible_value"].append(
            f"climatological_variable:{climatological_variable}"
        )
    list_response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for("legacy_list_coverages"),
        params=request_params,
    )
    all_forecast_coverages = db.collect_all_forecast_coverages(arpav_db_session)
    all_historical_coverages = db.collect_all_historical_coverages(arpav_db_session)
    total_coverages = len(all_forecast_coverages) + len(all_historical_coverages)
    filtered_coverages = db.collect_all_forecast_coverages(
        arpav_db_session,
        climatological_variable_filter=(
            [climatological_variable] if climatological_variable is not None else None
        ),
    )
    print(f"{total_coverages=}")
    print(f"{len(filtered_coverages)=}")
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["total_records"] == expected_total
    assert (
        list_response.json()["meta"]["total_filtered_records"]
        == expected_total_filtered
    )
    assert list_response.json()["meta"]["returned_records"] == 20


def test_forecast_tas_absolute_annual_details(
    test_client_v2_app: httpx.Client,
    sample_real_forecast_coverage_configurations: list[
        "coverages.ForecastCoverageConfiguration"
    ],
):
    response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for(
            "legacy_get_coverage",
            coverage_identifier=(
                "forecast-tas-absolute-annual-arpa_vfvg-all_seasons-ensemble-"
                "model_ensemble-rcp26-winter"
            ),
        )
    )
    assert response.status_code == 200
    details = response.json()
    assert details["data_precision"] == 1
    assert details["forecast_model"] == "model_ensemble"
    assert details["identifier"] == (
        "forecast-tas-absolute-annual-arpa_vfvg-all_seasons-ensemble-"
        "model_ensemble-rcp26-winter"
    )
    assert details["legend"]["color_entries"][0]["color"] == "#ffffffcc"
    assert details["legend"]["color_entries"][0]["value"] == -6.0
    assert details["legend"]["color_entries"][1]["color"] == "#fffed976"
    assert details["legend"]["color_entries"][1]["value"] == 3.0
    assert details["observation_stations_vector_tile_layer_url"].endswith(
        "/vector-tiles/tas_absolute_annual/{z}/{x}/{y}"
    )
    assert details["related_coverage_configuration_url"].endswith(
        "/coverages/coverage-configurations/"
        "forecast-tas-absolute-annual-arpa_vfvg-all_seasons-ensemble"
    )
    assert details["scenario"] == "rcp26"
    assert details["time_window"] is None
    assert details["unit_italian"] == "ºC"
    assert details["url"].endswith(
        "/coverages/coverages/"
        "forecast-tas-absolute-annual-arpa_vfvg-all_seasons-ensemble-"
        "model_ensemble-rcp26-winter"
    )
    assert details["wms_base_url"].endswith(
        "/coverages/wms/forecast-tas-absolute-annual-arpa_vfvg-"
        "all_seasons-ensemble-model_ensemble-rcp26-winter"
    )
    assert details["wms_main_layer_name"] == "tas"
    assert details["wms_secondary_layer_name"] is None
    assert details["year_period"] == "winter"
