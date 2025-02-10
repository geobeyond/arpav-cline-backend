import random
import re

import httpx
import pytest_httpx
import pytest

from arpav_ppcv.schemas import (
    coverages,
    observations,
)
from arpav_ppcv import database

random.seed(0)


def test_coverage_configurations_list(
    test_client_v2_app: httpx.Client,
    sample_coverage_configurations: list[coverages.CoverageConfiguration],
):
    list_response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for("list_coverage_configurations"),
        headers={"accept": "application/json"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 10


def test_coverage_identifiers_list(
    test_client_v2_app: httpx.Client,
    sample_coverage_configurations: list[coverages.CoverageConfiguration],
):
    list_response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for("list_coverage_identifiers"),
        headers={"accept": "application/json"},
    )
    assert list_response.status_code == 200


@pytest.mark.parametrize(
    "possible_values, expected_identifiers",
    [
        pytest.param(
            {
                "aggregation_period": "annual",
                "climatological_variable": "tas",
                "climatological_model": "model_ensemble",
                "archive": "forecast",
                "measure": "absolute",
                "scenario": "rcp26",
                "year_period": "winter",
            },
            [
                "tas_seasonal_absolute_model_ensemble-annual-forecast-model_ensemble-tas-absolute-rcp26-winter",
                "tas_seasonal_absolute_model_ensemble_lower_uncertainty-annual-forecast-model_ensemble-tas-absolute-rcp26-lower_bound-winter",
                "tas_seasonal_absolute_model_ensemble_upper_uncertainty-annual-forecast-model_ensemble-tas-absolute-rcp26-upper_bound-winter",
            ],
        )
    ],
)
def test_coverage_identifiers_list_with_possible_values_filter(
    test_client_v2_app: httpx.Client,
    sample_real_coverage_configurations: list[coverages.CoverageConfiguration],
    possible_values: dict[str, str],
    expected_identifiers: list[str],
):
    list_response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for("list_coverage_identifiers"),
        params={"possible_value": [f"{k}:{v}" for k, v in possible_values.items()]},
        headers={"accept": "application/json"},
    )
    items = list_response.json()["items"]
    identifiers = [i["identifier"] for i in items]
    for expected_id in expected_identifiers:
        assert expected_id in identifiers
    for found_id in identifiers:
        assert found_id in expected_identifiers


def test_get_time_series(
    httpx_mock: pytest_httpx.HTTPXMock,
    test_client_v2_app: httpx.Client,
    arpav_db_session,
    sample_tas_csv_data: dict[str, str],
):
    db_cov_conf = coverages.CoverageConfiguration(
        name="fake_tas",
        netcdf_main_dataset_name="tas",
        thredds_url_pattern="fake",
        palette="fake",
    )
    arpav_db_session.add(db_cov_conf)
    arpav_db_session.commit()
    arpav_db_session.refresh(db_cov_conf)

    httpx_mock.add_response(
        url=re.compile(r".*ncss/grid.*"),
        method="get",
        text=sample_tas_csv_data["tas"],
    )
    identifiers = database.generate_coverage_identifiers(db_cov_conf)
    cov_id = random.choice(identifiers)
    series_response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for(
            "get_time_series", coverage_identifier=cov_id
        ),
        params={
            "coords": "POINT(11.5469 44.9524)",
            "include_observation_data": False,
            "coverage_data_smoothing": ["NO_SMOOTHING"],
        },
        headers={"accept": "application/json"},
    )
    print(series_response.content)
    assert series_response.status_code == 200


@pytest.mark.parametrize(
    [
        "include_coverage_data",
        "coverage_data_smoothing",
        "include_observation_data",
        "observation_data_smoothing",
        "include_coverage_uncertainty",
        "include_coverage_related_data",
        "expected_italian_parameter_values",
    ],
    [
        pytest.param(
            True,
            ["NO_SMOOTHING"],
            False,
            None,
            False,
            False,
            [
                {
                    ("series_name", "Temperatura media"),
                    ("processing_method", "nessuna elaborazione"),
                },
            ],
        ),
        pytest.param(
            True,
            ["NO_SMOOTHING", "MOVING_AVERAGE_11_YEARS"],
            False,
            None,
            False,
            False,
            [
                {
                    ("series_name", "Temperatura media"),
                    ("processing_method", "nessuna elaborazione"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("processing_method", "media mobile centrata a 11 anni"),
                },
            ],
        ),
        pytest.param(
            True,
            ["NO_SMOOTHING", "MOVING_AVERAGE_11_YEARS"],
            False,
            None,
            True,
            False,
            [
                {
                    ("series_name", "Temperatura media"),
                    ("processing_method", "nessuna elaborazione"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("processing_method", "media mobile centrata a 11 anni"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("processing_method", "nessuna elaborazione"),
                    ("uncertainty_type", "Limiti inferiori dell'incertezza"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("processing_method", "media mobile centrata a 11 anni"),
                    ("uncertainty_type", "Limiti inferiori dell'incertezza"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("processing_method", "nessuna elaborazione"),
                    ("uncertainty_type", "Limiti superiori dell'incertezza"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("processing_method", "media mobile centrata a 11 anni"),
                    ("uncertainty_type", "Limiti superiori dell'incertezza"),
                },
            ],
        ),
        pytest.param(
            True,
            ["NO_SMOOTHING", "MOVING_AVERAGE_11_YEARS"],
            False,
            None,
            False,
            True,
            [
                {
                    ("series_name", "Temperatura media"),
                    ("processing_method", "nessuna elaborazione"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("processing_method", "media mobile centrata a 11 anni"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("climatological_model", "EC-EARTH RCA4"),
                    ("processing_method", "nessuna elaborazione"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("climatological_model", "EC-EARTH RCA4"),
                    ("processing_method", "media mobile centrata a 11 anni"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("climatological_model", "HadGEM RACMO22E"),
                    ("processing_method", "nessuna elaborazione"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("climatological_model", "HadGEM RACMO22E"),
                    ("processing_method", "media mobile centrata a 11 anni"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("climatological_model", "Insieme di 5 modelli"),
                    ("processing_method", "nessuna elaborazione"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("climatological_model", "Insieme di 5 modelli"),
                    ("processing_method", "media mobile centrata a 11 anni"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("climatological_model", "EC-EARTH RACMO22E"),
                    ("processing_method", "nessuna elaborazione"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("climatological_model", "EC-EARTH RACMO22E"),
                    ("processing_method", "media mobile centrata a 11 anni"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("climatological_model", "MPI-ESM-LR-REMO2009"),
                    ("processing_method", "nessuna elaborazione"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("climatological_model", "MPI-ESM-LR-REMO2009"),
                    ("processing_method", "media mobile centrata a 11 anni"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("climatological_model", "EC-EARTH CCLM4-8-17"),
                    ("processing_method", "nessuna elaborazione"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("climatological_model", "EC-EARTH CCLM4-8-17"),
                    ("processing_method", "media mobile centrata a 11 anni"),
                },
            ],
        ),
        pytest.param(
            True,
            ["NO_SMOOTHING", "MOVING_AVERAGE_11_YEARS"],
            True,
            ["NO_SMOOTHING", "MOVING_AVERAGE_5_YEARS"],
            False,
            False,
            [
                {
                    ("series_name", "Temperatura media"),
                    ("processing_method", "nessuna elaborazione"),
                },
                {
                    ("series_name", "Temperatura media"),
                    ("processing_method", "media mobile centrata a 11 anni"),
                },
                {
                    (
                        "series_name",
                        "Temperatura media (dalla stazione di osservazione)",
                    ),
                    ("processing_method", "nessuna elaborazione"),
                },
                {
                    (
                        "series_name",
                        "Temperatura media (dalla stazione di osservazione)",
                    ),
                    ("processing_method", "media mobile centrata a 11 anni"),
                },
            ],
        ),
    ],
)
def test_real_get_time_series(
    httpx_mock: pytest_httpx.HTTPXMock,
    test_client_v2_app: httpx.Client,
    arpav_db_session,
    sample_real_coverage_configurations: list[coverages.CoverageConfiguration],
    sample_real_monthly_measurements: list[observations.MonthlyMeasurement],
    sample_tas_csv_data: dict[str, str],
    include_coverage_data: bool,
    coverage_data_smoothing: list[str],
    include_observation_data: bool,
    observation_data_smoothing: list[str],
    include_coverage_uncertainty: bool,
    include_coverage_related_data: bool,
    expected_italian_parameter_values: list[set[tuple[str, str]]],
):
    coverage_identifier = "tas_seasonal_absolute_model_ensemble-annual-forecast-model_ensemble-tas-absolute-rcp45-winter"
    tas_thredds_url_pattern = "tas_avg_"
    tas_stddown_thredds_url_pattern = "tas_stddown_.*"
    tas_stdup_thredds_url_pattern = "tas_stdup_.*"
    httpx_mock.add_response(
        url=re.compile(rf".*?ncss/grid.*?{tas_thredds_url_pattern}.*"),
        method="get",
        text=sample_tas_csv_data["tas"],
    )
    if include_coverage_uncertainty:
        httpx_mock.add_response(
            url=re.compile(rf".*?ncss/grid.*?{tas_stddown_thredds_url_pattern}"),
            method="get",
            text=sample_tas_csv_data["tas_stddown"],
        )
        httpx_mock.add_response(
            url=re.compile(rf".*?ncss/grid.*?{tas_stdup_thredds_url_pattern}"),
            method="get",
            text=sample_tas_csv_data["tas_stdup"],
        )
    if include_coverage_related_data:
        patterns = (
            "tas_EC-EARTH_CCLM4-8-17_",
            "tas_EC-EARTH_RACMO22E_",
            "tas_EC-EARTH_RCA4_",
            "tas_MPI-ESM-LR_REMO2009_",
            "tas_HadGEM2-ES_RACMO22E_",
        )
        for patt in patterns:
            httpx_mock.add_response(
                url=re.compile(rf".*?ncss/grid.*?{patt}.*"),
                method="get",
                text=sample_tas_csv_data["tas"],
            )
    request_params = {
        "coords": "POINT(11.5469 44.9524)",
        "include_coverage_data": include_coverage_data,
        "include_observation_data": include_observation_data,
        "include_coverage_uncertainty": include_coverage_uncertainty,
        "include_coverage_related_data": include_coverage_related_data,
    }
    if coverage_data_smoothing is not None:
        request_params["coverage_data_smoothing"] = coverage_data_smoothing
    if observation_data_smoothing is not None:
        request_params["observation_data_smoothing"] = observation_data_smoothing
    series_response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for(
            "get_time_series", coverage_identifier=coverage_identifier
        ),
        params=request_params,
        headers={"accept": "application/json"},
    )
    print(series_response.content)
    for found_series in series_response.json()["series"]:
        found_italian_values = {
            (k, v["it"])
            for k, v in found_series["translations"]["parameter_values"].items()
        }
        print(f"{found_italian_values=}")
        for expected in expected_italian_parameter_values:
            print(f"{expected=}")
            if expected <= found_italian_values:
                break
        else:
            assert False
