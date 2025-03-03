import sqlmodel
import typer
from operator import attrgetter
from rich import print

from . import schemas
from .. import database

stations_app = typer.Typer()
series_configurations_app = typer.Typer()


@stations_app.command(name="list")
def list_observation_stations(ctx: typer.Context) -> None:
    """List observation stations."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        all_stations = list(database.collect_all_observation_stations(session))
        all_stations.sort(key=attrgetter("code"))
        for db_station in all_stations:
            item = schemas.ObservationStationItem(**db_station.model_dump())
            print(f"{item.code} - {item.name}")


@stations_app.command(name="get")
def get_observation_station(ctx: typer.Context, code: str) -> None:
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        if (
            db_station := database.get_observation_station_by_code(session, code)
        ) is not None:
            item = schemas.ObservationStationDetail(**db_station.model_dump())
            print(item)


@series_configurations_app.command(name="list")
def list_observation_series_configurations(ctx: typer.Context) -> None:
    """List observation series configurations."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        all_series_configurations = list(
            database.collect_all_observation_series_configurations(session)
        )
        for db_series_configuration in all_series_configurations:
            item = schemas.ObservationSeriesConfigurationItem(
                **db_series_configuration.model_dump()
            )
            print(item.identifier)


@series_configurations_app.command(name="get")
def get_observation_series_configuration(ctx: typer.Context, identifier: str) -> None:
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        if (
            db_series_configuration := (
                database.get_observation_series_configuration_by_identifier(
                    session, identifier
                )
            )
        ) is not None:
            item = schemas.ObservationSeriesConfigurationDetail(
                **db_series_configuration.model_dump(exclude={"climatic_indicator_id"}),
                climatic_indicator=schemas.ClimaticIndicatorItem(
                    **db_series_configuration.climatic_indicator.model_dump()
                ),
            )
            print(item)
