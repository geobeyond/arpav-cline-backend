import datetime as dt
import uuid
from typing import Optional

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
from .climaticindicators import app as climatic_indicators_app
from .observations import (
    series_configurations_app,
    stations_app,
)

app = typer.Typer()
app.add_typer(climatic_indicators_app, name="climatic-indicators")
app.add_typer(stations_app, name="observation-stations")
app.add_typer(series_configurations_app, name="observation-series-configurations")

_JSON_INDENTATION = 2


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
