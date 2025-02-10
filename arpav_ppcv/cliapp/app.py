import datetime as dt
import uuid
from typing import (
    Annotated,
    Optional,
)

import geojson_pydantic
import pydantic_core
import sqlmodel
import typer
from rich import print

from .. import database
from ..schemas import (
    base,
    observations,
)
from . import schemas

app = typer.Typer()

_JSON_INDENTATION = 2


@app.command(name="list-stations")
def list_stations(ctx: typer.Context) -> None:
    """List stations."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        result = [
            schemas.StationRead(**s.model_dump())
            for s in database.collect_all_stations(session)
        ]
        print(pydantic_core.to_json(result, indent=_JSON_INDENTATION).decode("utf-8"))


@app.command(name="create-station", context_settings={"ignore_unknown_options": True})
def create_station(
    ctx: typer.Context,
    code: str,
    longitude: Annotated[float, typer.Argument(min=-180, max=180)],
    latitude: Annotated[float, typer.Argument(min=-90, max=90)],
    altitude: Annotated[float, typer.Option(min=-50, max=10_000)] = None,
    name: Annotated[str, typer.Option(help="Station name")] = "",
    type: Annotated[str, typer.Option(help="Station type")] = "",
) -> None:
    station_create = schemas.StationCreate(
        geom=geojson_pydantic.Point(type="Point", coordinates=(longitude, latitude)),
        code=code,
        altitude_m=altitude,
        name=name,
        type_=type.lower().replace(" ", "_"),
    )
    """Create a new station."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        db_station = database.create_station(session, station_create)
        print(
            schemas.StationRead(**db_station.model_dump()).model_dump_json(
                indent=_JSON_INDENTATION
            )
        )


@app.command(name="delete-station")
def delete_station(
    ctx: typer.Context,
    station_id: uuid.UUID,
) -> None:
    """Delete a station."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        database.delete_station(session, station_id)


@app.command(name="list-variables")
def list_variables(ctx: typer.Context) -> None:
    """List variables."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        result = [
            schemas.VariableRead(**v.model_dump())
            for v in database.collect_all_variables(session)
        ]
        print(pydantic_core.to_json(result, indent=_JSON_INDENTATION).decode("utf-8"))


@app.command(name="create-variable")
def create_variable(
    ctx: typer.Context,
    name: str,
    description: str,
    unit: Optional[str] = "",
) -> None:
    variable_create = schemas.VariableCreate(
        name=name, description=description, unit=unit
    )
    """Create a new variable."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        db_variable = database.create_variable(session, variable_create)
        print(
            schemas.VariableRead(**db_variable.model_dump()).model_dump_json(
                indent=_JSON_INDENTATION
            )
        )


@app.command(name="delete-variable")
def delete_variable(
    ctx: typer.Context,
    variable_id: uuid.UUID,
) -> None:
    """Delete a variable."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        database.delete_variable(session, variable_id)


@app.command(name="list-monthly-measurements")
def list_monthly_measurements(ctx: typer.Context) -> None:
    """List monthly measurements."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        result = [
            schemas.MonthlyMeasurementRead(**v.model_dump())
            for v in database.collect_all_monthly_measurements(session)
        ]
        print(pydantic_core.to_json(result, indent=_JSON_INDENTATION).decode("utf-8"))


@app.command(name="create-monthly-measurement")
def create_monthly_measurement(
    ctx: typer.Context,
    station_code: str,
    variable: str,
    date: dt.datetime,
    value: float,
) -> None:
    """Create a new monthly measurement."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        db_station = database.get_station_by_code(session, station_code)
        db_variable = database.get_variable_by_name(session, variable)
        if db_station is None:
            raise SystemExit("Invalid station code")
        elif db_variable is None:
            raise SystemExit("invalid variable")
        else:
            db_monthly_measurement = database.create_monthly_measurement(
                session,
                observations.MonthlyMeasurementCreate(
                    station_id=db_station.id,
                    variable_id=db_variable.id,
                    date=dt.date(date.year, date.month, 1),
                    value=value,
                ),
            )
        print(
            schemas.MonthlyMeasurementRead(
                **db_monthly_measurement.model_dump()
            ).model_dump_json(indent=_JSON_INDENTATION)
        )


@app.command(name="delete-monthly-measurement")
def delete_monthly_measurement(
    ctx: typer.Context,
    monthly_measurement_id: uuid.UUID,
) -> None:
    """Delete a monthly measurement."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        database.delete_monthly_measurement(session, monthly_measurement_id)


@app.command(name="list-seasonal-measurements")
def list_seasonal_measurements(
    ctx: typer.Context,
    station_code: Optional[str] = None,
    variable_name: Optional[str] = None,
) -> None:
    """List seasonal measurements."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        if station_code is not None:
            db_station = database.get_station_by_code(session, station_code)
            if db_station is not None:
                station_id_filter = db_station.id
            else:
                raise SystemExit("Invalid station code")
        else:
            station_id_filter = None
        if variable_name is not None:
            db_variable = database.get_variable_by_name(session, variable_name)
            if db_variable is not None:
                variable_id_filter = db_variable.id
            else:
                raise SystemExit("Invalid variable name")
        else:
            variable_id_filter = None
        result = [
            schemas.SeasonalMeasurementRead(**v.model_dump())
            for v in database.collect_all_seasonal_measurements(
                session,
                station_id_filter=station_id_filter,
                variable_id_filter=variable_id_filter,
            )
        ]
        print(pydantic_core.to_json(result, indent=_JSON_INDENTATION).decode("utf-8"))


@app.command(name="create-seasonal-measurement")
def create_seasonal_measurement(
    ctx: typer.Context,
    station_code: str,
    variable: str,
    year: int,
    season: base.Season,
    value: float,
) -> None:
    """Create a new seasonal measurement."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        db_station = database.get_station_by_code(session, station_code)
        db_variable = database.get_variable_by_name(session, variable)
        if db_station is None:
            raise SystemExit("Invalid station code")
        elif db_variable is None:
            raise SystemExit("invalid variable")
        else:
            db_measurement = database.create_seasonal_measurement(
                session,
                observations.SeasonalMeasurementCreate(
                    station_id=db_station.id,
                    variable_id=db_variable.id,
                    year=year,
                    season=season,
                    value=value,
                ),
            )
        print(
            schemas.SeasonalMeasurementRead(
                **db_measurement.model_dump()
            ).model_dump_json(indent=_JSON_INDENTATION)
        )


@app.command(name="delete-seasonal-measurement")
def delete_seasonal_measurement(
    ctx: typer.Context,
    measurement_id: uuid.UUID,
) -> None:
    """Delete a seasonal measurement."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        database.delete_seasonal_measurement(session, measurement_id)


@app.command(name="list-yearly-measurements")
def list_yearly_measurements(
    ctx: typer.Context,
    station_code: Optional[str] = None,
    variable_name: Optional[str] = None,
) -> None:
    """List yearly measurements."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        if station_code is not None:
            db_station = database.get_station_by_code(session, station_code)
            if db_station is not None:
                station_id_filter = db_station.id
            else:
                raise SystemExit("Invalid station code")
        else:
            station_id_filter = None
        if variable_name is not None:
            db_variable = database.get_variable_by_name(session, variable_name)
            if db_variable is not None:
                variable_id_filter = db_variable.id
            else:
                raise SystemExit("Invalid variable name")
        else:
            variable_id_filter = None
        result = [
            schemas.YearlyMeasurementRead(**v.model_dump())
            for v in database.collect_all_yearly_measurements(
                session,
                station_id_filter=station_id_filter,
                variable_id_filter=variable_id_filter,
            )
        ]
        print(pydantic_core.to_json(result, indent=_JSON_INDENTATION).decode("utf-8"))


@app.command(name="create-yearly-measurement")
def create_yearly_measurement(
    ctx: typer.Context,
    station_code: str,
    variable: str,
    value: float,
    year: int,
) -> None:
    """Create a new yearly measurement."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        db_station = database.get_station_by_code(session, station_code)
        db_variable = database.get_variable_by_name(session, variable)
        if db_station is None:
            raise SystemExit("Invalid station code")
        elif db_variable is None:
            raise SystemExit("invalid variable")
        else:
            db_measurement = database.create_yearly_measurement(
                session,
                observations.YearlyMeasurementCreate(
                    station_id=db_station.id,
                    variable_id=db_variable.id,
                    year=year,
                    value=value,
                ),
            )
        print(
            schemas.YearlyMeasurementRead(
                **db_measurement.model_dump()
            ).model_dump_json(indent=_JSON_INDENTATION)
        )


@app.command(name="delete-yearly-measurement")
def delete_yearly_measurement(
    ctx: typer.Context,
    measurement_id: uuid.UUID,
) -> None:
    """Delete a yearly measurement."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        database.delete_yearly_measurement(session, measurement_id)
