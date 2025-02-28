import httpx

from arpav_cline.schemas.climaticindicators import ClimaticIndicator


def test_climatic_indicator_list(
    test_client_v2_app: httpx.Client,
    sample_real_climatic_indicators: list[ClimaticIndicator],
):
    list_response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for("list_climatic_indicators")
    )
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == min(
        20, len(sample_real_climatic_indicators)
    )


def test_climatic_indicator_detail(
    test_client_v2_app: httpx.Client,
    sample_real_climatic_indicators: list[ClimaticIndicator],
):
    target_indicator = sample_real_climatic_indicators[0]
    detail_response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for(
            "get_climatic_indicator",
            climatic_indicator_identifier=target_indicator.identifier,
        )
    )
    assert detail_response.status_code == 200
    payload = detail_response.json()
    assert payload["identifier"] == target_indicator.identifier
