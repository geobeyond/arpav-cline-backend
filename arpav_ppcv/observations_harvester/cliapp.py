import typer
from typing import Annotated

from ..prefect.flows import observations as observations_flows

app = typer.Typer()


@app.command()
def refresh_stations(
    series_configuration_identifier: Annotated[
        str,
        typer.Option(
            help=(
                "The observation series configuration identifier to process. If "
                "not provided, all observation series configurations are "
                "processed."
            ),
        ),
    ],
) -> None:
    observations_flows.refresh_stations(
        observation_series_configuration_identifier=series_configuration_identifier,
    )


@app.command()
def refresh_monthly_measurements(
    station: Annotated[
        str,
        typer.Option(
            help=(
                "Code of the station to process. If not provided, all "
                "stations are processed."
            ),
        ),
    ] = None,
    variable: Annotated[
        str,
        typer.Option(
            help=(
                "Name of the variable to process. If not provided, all "
                "variables are processed."
            )
        ),
    ] = None,
) -> None:
    observations_flows.refresh_monthly_measurements(
        station_code=station, variable_name=variable
    )


@app.command()
def refresh_seasonal_measurements(
    station: Annotated[
        str,
        typer.Option(
            help=(
                "Code of the station to process. If not provided, all "
                "stations are processed."
            ),
        ),
    ],
    variable: Annotated[
        str,
        typer.Option(
            help=(
                "Name of the variable to process. If not provided, all "
                "variables are processed."
            )
        ),
    ] = None,
) -> None:
    observations_flows.refresh_seasonal_measurements(
        station_code=station,
        variable_name=variable,
    )


@app.command()
def refresh_yearly_measurements(
    station: Annotated[
        str,
        typer.Option(
            help=(
                "Code of the station to process. If not provided, all "
                "stations are processed."
            ),
        ),
    ] = None,
    climatic_indicator: Annotated[
        str,
        typer.Option(
            help=(
                "Identifier of the climatic indicator to process. If not provided, all "
                "climatic indicators are processed."
            )
        ),
    ] = None,
) -> None:
    observations_flows.refresh_yearly_measurements(
        station_code=station, climatic_indicator_identifier=climatic_indicator
    )
