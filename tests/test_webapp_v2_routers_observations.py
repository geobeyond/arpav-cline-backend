import httpx

from arpav_cline.schemas import observations


def test_station_list(
    test_client_v2_app: httpx.Client, sample_stations: list[observations.Station]
):
    list_response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for("list_stations"),
        headers={"accept": "application/json"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 20


def test_station_list_geojson(
    test_client_v2_app: httpx.Client, sample_stations: list[observations.Station]
):
    list_response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for("list_stations")
    )
    assert list_response.status_code == 200
    assert len(list_response.json()["features"]) == 20


def test_station_detail(
    test_client_v2_app: httpx.Client,
    sample_stations: list[observations.ObservationStation],
):
    target_station = sample_stations[0]
    detail_response = test_client_v2_app.get(
        test_client_v2_app.app.url_path_for(
            "get_station", station_code=target_station.code
        )
    )
    assert detail_response.status_code == 200
    payload = detail_response.json()
    assert payload["code"] == target_station.code


# def test_monthly_measurement_list(
#     test_client_v2_app: httpx.Client,
#     sample_monthly_measurements: list[observations.MonthlyMeasurement],
# ):
#     list_response = test_client_v2_app.get(
#         test_client_v2_app.app.url_path_for("list_monthly_measurements")
#     )
#     assert list_response.status_code == 200
#     assert len(list_response.json()["items"]) == 20
#
#
# def test_monthly_measurement_list_filter_by_station_code(
#     test_client_v2_app: httpx.Client,
#     sample_monthly_measurements: list[observations.MonthlyMeasurement],
# ):
#     target_station = sample_monthly_measurements[0].station
#     list_response = test_client_v2_app.get(
#         test_client_v2_app.app.url_path_for("list_monthly_measurements"),
#         params={"station_code": target_station.code},
#     )
#     assert list_response.status_code == 200
#     payload = list_response.json()
#     assert len(payload["items"]) > 0
#     for returned_item in payload["items"]:
#         assert returned_item["station_code"] == target_station.code
#
#
# def test_monthly_measurement_list_filter_by_variable_name(
#     test_client_v2_app: httpx.Client,
#     sample_monthly_measurements: list[observations.MonthlyMeasurement],
# ):
#     target_climatic_indicator = sample_monthly_measurements[0].climatic_indicator
#     list_response = test_client_v2_app.get(
#         test_client_v2_app.app.url_path_for("list_monthly_measurements"),
#         params={"climatic_indicator_identifier": target_climatic_indicator.identifier},
#     )
#     assert list_response.status_code == 200
#     payload = list_response.json()
#     assert len(payload["items"]) > 0
#     for returned_item in payload["items"]:
#         assert (
#             returned_item["climatic_identifier"] == target_climatic_indicator.identifier
#         )
#
#
# def test_monthly_measurement_detail(
#     test_client_v2_app: httpx.Client,
#     sample_monthly_measurements: list[observations.MonthlyMeasurement],
# ):
#     target_measurement = sample_monthly_measurements[0]
#     detail_response = test_client_v2_app.get(
#         test_client_v2_app.app.url_path_for(
#             "get_monthly_measurement", monthly_measurement_id=target_measurement.id
#         )
#     )
#     assert detail_response.status_code == 200
#     payload = detail_response.json()
#     assert payload["value"] == target_measurement.value
