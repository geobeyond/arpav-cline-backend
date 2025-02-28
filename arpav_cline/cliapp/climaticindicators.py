import sqlmodel
import typer
from operator import attrgetter
from rich import print

from . import schemas
from .. import database

app = typer.Typer()


@app.command(name="list")
def list_climatic_indicators(ctx: typer.Context) -> None:
    """List climatic indicators."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        all_indicators = list(database.collect_all_climatic_indicators(session))
        all_indicators.sort(key=attrgetter("sort_order"))
        for db_climatic_indicator in all_indicators:
            item = schemas.ClimaticIndicatorItem(**db_climatic_indicator.model_dump())
            print(item.identifier)


@app.command(name="get")
def get_climatic_indicator(ctx: typer.Context, identifier: str) -> None:
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        if (
            db_climatic_indicator := database.get_climatic_indicator_by_identifier(
                session, identifier
            )
        ) is not None:
            item = schemas.ClimaticIndicatorDetail(**db_climatic_indicator.model_dump())
            print(item)
