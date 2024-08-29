"""Command-line interface for the project."""

import logging
import logging.config
import os
import sys
from typing import Annotated, Optional
from pathlib import Path

import alembic.command
import alembic.config
import anyio
import sqlmodel
import typer
import yaml
from babel.messages.catalog import Catalog
from babel.messages.pofile import (
    read_po,
    write_po,
)
from babel.messages.mofile import write_mo
from babel.messages.extract import extract_from_dir
from rich import print
from rich.padding import Padding
from rich.panel import Panel

from . import (
    config,
    database,
)
from .cliapp.app import app as cli_app
from .bootstrapper.cliapp import app as bootstrapper_app
from .observations_harvester.cliapp import app as observations_harvester_app
from .prefect.cliapp import app as prefect_app
from .thredds import crawler

app = typer.Typer()
db_app = typer.Typer()
dev_app = typer.Typer()
translations_app = typer.Typer()
app.add_typer(cli_app, name="app")
app.add_typer(db_app, name="db")
app.add_typer(dev_app, name="dev")
app.add_typer(observations_harvester_app, name="observations-harvester")
app.add_typer(bootstrapper_app, name="bootstrap")
app.add_typer(translations_app, name="translations")
app.add_typer(prefect_app, name="prefect")


@app.callback()
def base_callback(ctx: typer.Context) -> None:
    ctx_obj = ctx.ensure_object(dict)
    settings = config.get_settings()
    engine = database.get_engine(settings)
    alembic_config = alembic.config.Config()
    alembic_config.set_main_option("script_location", "arpav_ppcv:migrations")
    ctx_obj.update(
        {
            "settings": settings,
            "engine": engine,
            "alembic_config": alembic_config,
        }
    )
    if (
        config_file_path := settings.log_config_file
    ) is not None and config_file_path.exists():
        logging.config.dictConfig(yaml.safe_load(config_file_path.read_text()))


@db_app.callback()
def db_app_callback() -> None:
    """Manage ARPAV-PPCV database."""


@db_app.command(name="generate-migration")
def generate_migration(ctx: typer.Context, migration_message: str):
    """Generate migration files with any new database schema changes.

    Remember to inspect the autogenerated migration files in order to determine
    whether they correctly capture the changes in the code.
    """
    alembic.command.revision(
        ctx.obj["alembic_config"],
        message=migration_message,
        autogenerate=True,
    )


@db_app.command(name="upgrade")
def upgrade_db(ctx: typer.Context, revision_identifier: Optional[str] = None) -> None:
    """Apply any pending migration files."""
    print("Upgrading database...")
    revision_arg = "head" if revision_identifier is None else revision_identifier
    alembic.command.upgrade(ctx.obj["alembic_config"], revision_arg)
    print("Done!")


@app.command()
def run_server(ctx: typer.Context):
    """Run the uvicorn server.

    Example (dev) invocation:

    ```
    bash -c 'set -o allexport; source sample_env.env; set +o allexport; poetry run arpav-ppcv.run-server'
    ```
    """
    # NOTE: we explicitly do not use uvicorn's programmatic running abilities here
    # because they do not work correctly when called outside an
    # `if __name__ == __main__` guard and when using its debug features.
    # For more detail check:
    #
    # https://github.com/encode/uvicorn/issues/1045
    #
    # This solution works well both in development (where we want to use reload)
    # and in production, as using os.execvp is actually similar to just running
    # the standard `uvicorn` cli command (which is what uvicorn docs recommend).
    settings: config.ArpavPpcvSettings = ctx.obj["settings"]
    uvicorn_args = [
        "uvicorn",
        "arpav_ppcv.webapp.app:create_app",
        f"--port={settings.bind_port}",
        f"--host={settings.bind_host}",
        "--factory",
        "--access-log",
    ]
    if settings.debug:
        uvicorn_args.extend(
            [
                "--reload",
                f"--reload-dir={str(Path(__file__).parent)}",
                "--log-level=debug",
            ]
        )
    else:
        uvicorn_args.extend(["--log-level=info"])
    if (log_config_file := settings.log_config_file) is not None:
        uvicorn_args.append(f"--log-config={str(log_config_file)}")
    if settings.public_url.startswith("https://"):
        uvicorn_args.extend(
            [
                "--forwarded-allow-ips=*",
                "--proxy-headers",
            ]
        )

    serving_str = (
        f"[dim]Serving at:[/dim] [link]http://{settings.bind_host}:{settings.bind_port}[/link]\n\n"
        f"[dim]Public URL:[/dim] [link]{settings.public_url}[/link]\n\n"
        f"[dim]API docs:[/dim] [link]{settings.public_url}{settings.v2_api_mount_prefix}/docs[/link]"
    )
    panel = Panel(
        (
            f"{serving_str}\n\n"
            f"[dim]Running in [b]{'development' if settings.debug else 'production'} mode[/b]"
        ),
        title="ARPAV-PPCV",
        expand=False,
        padding=(1, 2),
        style="green",
    )
    print(Padding(panel, 1))
    sys.stdout.flush()
    sys.stderr.flush()
    os.execvp("uvicorn", uvicorn_args)


@dev_app.command()
def import_thredds_datasets(
    ctx: typer.Context,
    base_thredds_url: Annotated[
        str,
        typer.Argument(
            help=(
                "Base URL of the THREDDS server. Example: "
                "https://thredds.arpa.veneto.it/thredds"
            )
        ),
    ],
    output_base_dir: Annotated[
        Path,
        typer.Argument(
            help=(
                "Base path for downloaded NetCDF files. Example: "
                "/home/appuser/data/datasets"
            )
        ),
    ],
    name_filter: Annotated[
        str,
        typer.Option(
            help=(
                "Only process coverage configurations whose name contains "
                "this substring"
            )
        ),
    ] = None,
    force_download: Annotated[
        Optional[bool],
        typer.Option(
            help=(
                "Whether to re-download a dataset even if it is already "
                "present locally."
            )
        ),
    ] = False,
):
    """Import NetCDF datasets from a THREDDS server."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        relevant_cov_confs = database.collect_all_coverage_configurations(
            session, name_filter=name_filter
        )
        urls = []
        for cov_conf in relevant_cov_confs:
            cov_conf_urls = crawler.get_coverage_configuration_urls(
                base_thredds_url, cov_conf
            )
            urls.extend(cov_conf_urls)

    print(f"Trying to download {len(urls)} datasets...")
    anyio.run(
        crawler.download_datasets,  # noqa
        urls,
        base_thredds_url,
        output_base_dir,
        force_download,
    )


@translations_app.callback()
def translations_app_callback():
    """Manage PRTR translations."""


@translations_app.command(name="extract")
def extract_translations(
    output_path: Path = Path(__file__).parents[1] / "messages.pot",
):
    """Scan the PRTR source code and extract translatable strings into a pot file."""
    method_map = [
        ("**.py", "python"),
        ("**.html", "jinja2"),
    ]
    source_path = Path(__file__).parent
    print(f"Scanning source code from {source_path} for translatable strings...")
    messages = extract_from_dir(dirname=source_path, method_map=method_map)
    template_catalog = Catalog(project="arpav-ppcv")
    for message in messages:
        template_catalog.add(
            id=message[2],
            locations=[message[:2]],
            auto_comments=message[3],
            context=message[4],
        )
    print(f"Writing template catalog at {output_path}...")
    with output_path.open("wb") as fh:
        write_po(fh, catalog=template_catalog)
    print("Done!")


@translations_app.command(name="init")
def init_translations(
    template_catalog_path: Path = (Path(__file__).parents[1] / "messages.pot"),
    translations_dir: Path = (Path(__file__).parent / "translations"),
):
    """Initialize a translation catalog."""
    for locale in (config.LOCALE_IT, config.LOCALE_EN):
        catalog_path = translations_dir / locale.language / "LC_MESSAGES/messages.po"
        if not catalog_path.exists():
            if template_catalog_path.is_file():
                catalog_dir = catalog_path.parent
                catalog_dir.mkdir(parents=True, exist_ok=True)
                with (
                    template_catalog_path.open("r") as template_fh,
                    catalog_path.open("wb") as catalog_fh,
                ):
                    template_catalog = read_po(template_fh)
                    catalog = Catalog(locale=locale)
                    catalog.update(
                        template=template_catalog, update_header_comment=True
                    )
                    print(f"Initializing message catalog at {str(catalog_path)!s}...")
                    write_po(catalog_fh, catalog)
            else:
                print(f"{template_catalog_path} not found, aborting...")
                raise typer.Abort() from None
        else:
            print(f"Catalog {catalog_path} already exists, aborting...")
            raise typer.Abort() from None
    print("Done!")


@translations_app.command(name="update")
def update_translations(
    template_catalog_path: Path = (Path(__file__).parents[1] / "messages.pot"),
    translations_dir: Path = (Path(__file__).parent / "translations"),
):
    """Update existing translation catalogues."""
    if template_catalog_path.is_file():
        with template_catalog_path.open("r") as fh:
            template_catalog = read_po(fh)
            for locale_dir in (p for p in translations_dir.iterdir() if p.is_dir()):
                print(f"Updating translations for locale {locale_dir.name}...")
                po_path = locale_dir / "LC_MESSAGES/messages.po"
                with po_path.open("r") as po_fh:
                    catalog = read_po(po_fh)
                    catalog.update(template_catalog)
                print(f"Writing template catalog at {str(po_path.resolve())!r}...")
                with po_path.open("wb") as po_fh:
                    write_po(po_fh, catalog)
    else:
        print(f"{template_catalog_path} not found")
        raise typer.Abort() from None
    print("Done!")


@translations_app.command(name="compile")
def compile_translations(
    translations_dir: Path = (Path(__file__).parent / "translations"),
):
    """Compile translations from their .po file into the usable .mo file."""
    for locale_dir in (p for p in translations_dir.iterdir() if p.is_dir()):
        po_path = locale_dir / "LC_MESSAGES/messages.po"
        mo_path = locale_dir / "LC_MESSAGES/messages.mo"
        print(f"Compiling messages for locale {locale_dir.name}...")
        with po_path.open("r") as po_fh, mo_path.open("wb") as mo_fh:
            catalog = read_po(po_fh)
            write_mo(mo_fh, catalog)
        print(f"Wrote file {mo_path}...")
    print("Done!")
