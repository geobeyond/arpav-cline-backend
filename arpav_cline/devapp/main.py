import os
import sys
from pathlib import Path
from typing import (
    Annotated,
    Optional,
)

import anyio
import sqlmodel
import typer
from rich import print

from ..thredds import crawler
from .. import (
    config,
    db,
)

app = typer.Typer(help="Development-oriented commands")


@app.command()
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
    coverage_configuration_identifier_filter: Annotated[
        str,
        typer.Option(
            help=(
                "Only process coverage configurations whose identifier contains "
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
        relevant_forecast_cov_confs = (
            db.collect_all_forecast_coverage_configurations_with_identifier_filter(
                session, identifier_filter=coverage_configuration_identifier_filter
            )
        )
        relevant_historical_cov_confs = (
            db.collect_all_historical_coverage_configurations_with_identifier_filter(
                session, identifier_filter=coverage_configuration_identifier_filter
            )
        )
        # TODO: Implement also overviews
        urls = []
        settings: config.ArpavPpcvSettings = ctx.obj["settings"]

        # temporarily override the THREDDS server base URL in order to allow
        # finding datasets that use fnmatch wildcards in their URL
        old_thredds_base_url = settings.thredds_server.base_url
        settings.thredds_server.base_url = base_thredds_url

        for forecast_cov_conf in relevant_forecast_cov_confs:
            forecast_covs = db.generate_forecast_coverages_from_configuration(
                forecast_cov_conf
            )
            for cov in forecast_covs:
                urls.append(cov.get_thredds_file_download_url(settings.thredds_server))
                lower_uncert_url = cov.get_lower_uncertainty_thredds_file_download_url(
                    settings.thredds_server
                )
                if lower_uncert_url is not None:
                    urls.append(lower_uncert_url)
                upper_uncert_url = cov.get_upper_uncertainty_thredds_file_download_url(
                    settings.thredds_server
                )
                if upper_uncert_url is not None:
                    urls.append(upper_uncert_url)
        for historical_cov_conf in relevant_historical_cov_confs:
            historical_covs = db.generate_historical_coverages_from_configuration(
                historical_cov_conf
            )
            for cov in historical_covs:
                urls.append(cov.get_thredds_file_download_url(settings.thredds_server))
        # restore THREDDS base url
        settings.thredds_server.base_url = old_thredds_base_url
    # remote_urls = [
    #     url.replace(settings.thredds_server.base_url, base_thredds_url)
    #     for url in urls
    # ]
    print(f"Trying to download {len(urls)} datasets...")
    # for url in urls:
    #     print(url)
    anyio.run(
        crawler.download_datasets,  # noqa
        urls,
        base_thredds_url,
        output_base_dir,
        force_download,
    )


@app.command()
def install_qgis_into_venv(
    context: typer.Context,
    pyqt5_dir: Path = os.getenv(
        "PYQT5_DIR_PATH", "/usr/lib/python3/dist-packages/PyQt5"
    ),
    sip_dir: Path = os.getenv("SIP_DIR_PATH", "/usr/lib/python3/dist-packages"),
    qgis_dir: Path = os.getenv(
        "QGIS_PYTHON_DIR_PATH", "/usr/lib/python3/dist-packages/qgis"
    ),
    processing_plugin_dir: Path = os.getenv(
        "QGIS_PROCESSING_PLUGIN_DIR_PATH", "/usr/share/qgis/python/plugins/processing"
    ),
):
    venv_dir = _get_virtualenv_site_packages_dir()
    print(f"venv_dir: {venv_dir}")
    print(f"pyqt5_dir: {pyqt5_dir}")
    print(f"sip_dir: {sip_dir}")
    print(f"qgis_dir: {qgis_dir}")
    print(f"processing_plugin_dir: {processing_plugin_dir}")
    suitable, relevant_paths = _check_suitable_system(
        pyqt5_dir, sip_dir, qgis_dir, processing_plugin_dir
    )
    if suitable:
        target_pyqt5_dir_path = venv_dir / "PyQt5"
        print(f"Symlinking {relevant_paths['pyqt5']} to {target_pyqt5_dir_path}...")
        try:
            target_pyqt5_dir_path.symlink_to(
                relevant_paths["pyqt5"], target_is_directory=True
            )
        except FileExistsError as err:
            print(err)

        for sip_file in relevant_paths["sip"]:
            target = venv_dir / sip_file.name
            print(f"Symlinking {sip_file} to {target}...")
            try:
                target.symlink_to(sip_file)
            except FileExistsError as err:
                print(err)
        target_qgis_dir_path = venv_dir / "qgis"
        print(f"Symlinking {relevant_paths['qgis']} to {target_qgis_dir_path}...")
        try:
            target_qgis_dir_path.symlink_to(
                relevant_paths["qgis"], target_is_directory=True
            )
        except FileExistsError as err:
            print(err)
        target_processing_plugin_dir_path = venv_dir / "processing"
        print(
            f"Symlinking {relevant_paths['processing_plugin']} to "
            f"{target_processing_plugin_dir_path}..."
        )
        try:
            target_processing_plugin_dir_path.symlink_to(
                relevant_paths["processing_plugin"], target_is_directory=True
            )
        except FileExistsError as err:
            print(err)
        final_message = "Done!"
    else:
        final_message = f"Could not find all relevant paths: {relevant_paths}"
    print(final_message)


def _check_suitable_system(
    pyqt5_dir: Path,
    sip_dir: Path,
    qgis_dir: Path,
    processing_plugin_dir: Path,
) -> tuple[bool, dict]:
    pyqt5_found = pyqt5_dir.is_dir()
    try:
        sip_files = _find_sip_files(sip_dir)
    except IndexError:
        sip_files = []
    sip_found = len(sip_files) > 0
    qgis_found = qgis_dir.is_dir()
    processing_plugin_found = processing_plugin_dir.is_dir()
    suitable = pyqt5_found and sip_found and qgis_found and processing_plugin_found
    return (
        suitable,
        {
            "pyqt5": pyqt5_dir,
            "sip": sip_files,
            "qgis": qgis_dir,
            "processing_plugin": processing_plugin_dir,
        },
    )


def _find_sip_files(sip_dir) -> list[Path]:
    sip_so_file = list(sip_dir.glob("sip.*.so"))[0]
    sipconfig_files = list(sip_dir.glob("sipconfig*.py"))
    return sipconfig_files + [sip_so_file]


def _get_virtualenv_site_packages_dir() -> Path:
    venv_lib_root = Path(sys.executable).parents[1] / "lib"
    for item in [i for i in venv_lib_root.iterdir() if i.is_dir()]:
        if item.name.startswith("python"):
            python_lib_path = item
            break
    else:
        raise RuntimeError("Could not find site_packages_dir")
    site_packages_dir = python_lib_path / "site-packages"
    if site_packages_dir.is_dir():
        result = site_packages_dir
    else:
        raise RuntimeError(f"{site_packages_dir} does not exist")
    return result
