import sqlmodel
import typer
from operator import attrgetter
from rich import print
from rich.table import Table

from . import schemas
from .. import database

stations_app = typer.Typer()
series_configurations_app = typer.Typer()


@stations_app.command(name="list")
def list_observation_stations(ctx: typer.Context) -> None:
    """List observation stations."""
    stations_table = Table(title="Observation Stations")
    stations_table.add_column("managed_by", justify="right")
    stations_table.add_column("code", justify="right")
    stations_table.add_column("name", justify="left")
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        all_stations = list(database.collect_all_observation_stations(session))
        all_stations.sort(key=attrgetter("code"))
        for db_station in all_stations:
            item = schemas.ObservationStationItem(**db_station.model_dump())
            stations_table.add_row(item.managed_by, item.code, item.name)
    print(stations_table)


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
    confs_table = Table(title="Observation Series Configurations")
    confs_table.add_column("identifier", justify="left")
    confs_table.add_column("climatic_indicator", justify="left")
    confs_table.add_column("station_managers", justify="left")
    confs_table.add_column("measurement_aggregation_type", justify="left")
    confs_table.add_column("indicator_internal_name", justify="left")
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        all_series_configurations = list(
            database.collect_all_observation_series_configurations(session)
        )
        for db_series_configuration in all_series_configurations:
            item = schemas.ObservationSeriesConfigurationItem(
                **db_series_configuration.model_dump(
                    exclude={
                        "climatic_indicator",
                    }
                ),
                climatic_indicator=db_series_configuration.climatic_indicator.identifier,
            )
            confs_table.add_row(
                item.identifier,
                item.climatic_indicator,
                ", ".join(i for i in db_series_configuration.station_managers),
                item.measurement_aggregation_type,
                item.indicator_internal_name,
            )
    print(confs_table)


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
