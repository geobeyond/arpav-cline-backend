import typer
from typing import Annotated

from ..prefect.flows import observations as observations_flows

app = typer.Typer()


@app.command()
def refresh_stations(
    variable: Annotated[
        str,
        typer.Option(
            help=(
                "Name of the variable to process. If not provided, all "
                "variables are processed."
            )
        ),
    ] = None,
    refresh_monthly: Annotated[
        bool,
        typer.Option(
            help=(
                "Refresh stations that have monthly measurements for "
                "the input month."
            )
        ),
    ] = True,
    refresh_seasonal: Annotated[
        bool,
        typer.Option(
            help=(
                "Refresh stations that have seasonal measurements for "
                "the input season."
            )
        ),
    ] = True,
    refresh_yearly: Annotated[
        bool, typer.Option(help=("Refresh stations that have yearly measurements"))
    ] = True,
) -> None:
    observations_flows.refresh_stations(
        variable_name=variable,
        refresh_stations_with_monthly_data=refresh_monthly,
        refresh_stations_with_seasonal_data=refresh_seasonal,
        refresh_stations_with_yearly_data=refresh_yearly,
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
    observations_flows.refresh_yearly_measurements(
        station_code=station, variable_name=variable
    )
