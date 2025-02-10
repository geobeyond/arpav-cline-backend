import pytest


@pytest.mark.parametrize(
    "code, lon, lat, altitude, name, type_",
    [
        pytest.param("fakecode1", "-10.44", "39.45", "5", "fakename1", "faketype1"),
        pytest.param("fakecode2", "-10.44", "39.45", None, None, None),
    ],
)
def test_create_station(cli_runner, cli_app, code, lon, lat, altitude, name, type_):
    execution_args = [
        "app",
        "create-station",
        code,
        lon,
        lat,
    ]
    if altitude is not None:
        execution_args.extend(["--altitude", altitude])
    if name is not None:
        execution_args.extend(["--name", name])
    if type_ is not None:
        execution_args.extend(["--type", type_])
    result = cli_runner.invoke(cli_app, execution_args)
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "name, description, unit",
    [
        pytest.param("fakevar1", "Some fake var 1", "ºC"),
        pytest.param("fakevar2", "Some fake var 2", None),
    ],
)
def test_create_variable(
    cli_runner,
    cli_app,
    name,
    description,
    unit,
):
    execution_args = [
        "app",
        "create-variable",
        name,
        description,
    ]
    if unit is not None:
        execution_args.extend(["--unit", unit])
    result = cli_runner.invoke(cli_app, execution_args)
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "date, value",
    [
        pytest.param("2020-01-01", "-34.23"),
    ],
)
def test_create_monthly_measurement(
    cli_runner, cli_app, sample_stations, sample_variables, date, value
):
    target_station = sample_stations[0]
    target_variable = sample_variables[0]
    execution_args = [
        "app",
        "create-monthly-measurement",
        target_station.code,
        target_variable.name,
        "2020-01-01",
        "23.33",
    ]
    result = cli_runner.invoke(cli_app, execution_args)
    assert result.exit_code == 0
