import httpx

from arpav_ppcv.schemas import coverages


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
