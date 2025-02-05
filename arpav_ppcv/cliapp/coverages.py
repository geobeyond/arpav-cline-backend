import sqlmodel
import typer
from operator import attrgetter
from rich import print
from rich.table import Table

from . import schemas
from .. import database

app = typer.Typer()


@app.command(name="list")
def list_overview_coverage_configurations(ctx: typer.Context) -> None:
    """List overview coverage configurations."""
    occ_table = Table(title="Overview coverage configurations")
    occ_table.add_column("identifier", justify="right")
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        all_overview_cov_confs = list(
            database.collect_all_forecast_overview_series_configurations(session)
        )
        all_overview_cov_confs.sort(key=attrgetter("identifier"))
        for overview_cov_conf in all_overview_cov_confs:
            item = schemas.OverviewCoverageConfigurationItem(
                identifier=overview_cov_conf.identifier,
            )
            occ_table.add_row(item.identifier)
    print(occ_table)
