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
    ] = None,
) -> None:
    observations_flows.refresh_stations(
        observation_series_configuration_identifier=series_configuration_identifier,
    )


@app.command()
def refresh_measurements(
    series_configuration_identifier: Annotated[
        str,
        typer.Option(
            help=(
                "The observation series configuration identifier to process. If "
                "not provided, all observation series configurations are "
                "processed."
            ),
        ),
    ] = None,
    station: Annotated[
        str,
        typer.Option(
            help=(
                "Code of the station to process. If not provided, all "
                "stations are processed."
            ),
        ),
    ] = None,
) -> None:
    observations_flows.refresh_measurements(
        station_code=station,
        observation_series_configuration_identifier=series_configuration_identifier,
    )
