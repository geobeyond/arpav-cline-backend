import random
import typing

import httpx

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
