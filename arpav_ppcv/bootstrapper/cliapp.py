import json
from pathlib import Path
from typing import Annotated

import geojson_pydantic
import sqlmodel
import typer
from rich import print
from sqlalchemy.exc import IntegrityError

from .. import database
from ..prefect.flows import observations as observations_flows
from ..schemas import (
    municipalities,
)

from ..schemas.coverages import (
    ConfigurationParameterPossibleValueUpdate,
    CoverageConfigurationUpdate,
)

from .coverage_configurations.forecast import (
    cdd as cdd_forecast,
    cdds as cdds_forecast,
    fd as fd_forecast,
    hdds as hdds_forecast,
    hwdi as hwdi_forecast,
    pr as pr_forecast,
    r95ptot as r95ptot_forecast,
    snwdays as snwdays_forecast,
    su30 as su30_forecast,
    tas as tas_forecast,
    tasmax as tasmax_forecast,
    tasmin as tasmin_forecast,
    tr as tr_forecast,
)
from .coverage_configurations.historical import (
    cdds as cdds_historical,
    fd as fd_historical,
    hdds as hdds_historical,
    prcptot as prcptot_historical,
    su30 as su30_historical,
    tdd as tdd_historical,
    tnd as tnd_historical,
    tr as tr_historical,
    txd as txd_historical,
)
from .variables import generate_variable_configurations
from .configurationparameters import generate_configuration_parameters

app = typer.Typer()


@app.command("municipalities")
def bootstrap_municipalities(
    ctx: typer.Context, municipalities_dataset: Path, force: bool = False
) -> None:
    """Bootstrap Italian municipalities"""
    # data_directory = Path(__file__).parents[2] / "data"
    # municipalities_dataset = data_directory / "limits_IT_municipalities.geojson"
    to_create = []

    should_bootstrap = False
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        _, num_existing_municipalities = database.list_municipalities(
            session, include_total=True
        )
        if num_existing_municipalities == 0:
            should_bootstrap = True
        else:
            if force:
                should_bootstrap = True
            else:
                print(
                    "Municipalities have already been bootstrapped. Supply the "
                    "`--force` option to discard existing records and re-boostrap "
                    "them again"
                )
        if should_bootstrap:
            has_centroid_info = False
            with municipalities_dataset.open() as fh:
                municipalities_geojson = json.load(fh)
                for idx, feature in enumerate(municipalities_geojson["features"]):
                    print(
                        f"parsing feature ({idx + 1}/{len(municipalities_geojson['features'])})..."
                    )
                    props = feature["properties"]
                    if idx == 0:
                        has_centroid_info = props.get("xcoord") is not None
                    mun_create = municipalities.MunicipalityCreate(
                        geom=geojson_pydantic.MultiPolygon(
                            type="MultiPolygon",
                            coordinates=feature["geometry"]["coordinates"],
                        ),
                        name=props["name"],
                        province_name=props["province_name"],
                        region_name=props["region_name"],
                        centroid_epsg_4326_lon=props.get("xcoord"),
                        centroid_epsg_4326_lat=props.get("ycoord"),
                    )
                    to_create.append(mun_create)
            if len(to_create) > 0:
                if num_existing_municipalities > 0:
                    print("About to delete pre-existing municipalities...")
                    database.delete_all_municipalities(session)
                print(f"About to save {len(to_create)} municipalities...")
                database.create_many_municipalities(session, to_create)
                if has_centroid_info:
                    print("About to (re)create municipality centroids DB view...")
                    ctx.invoke(bootstrap_municipality_centroids, ctx)
            else:
                print("There are no municipalities to create, skipping...")
    print("Done!")


@app.command("municipality-centroids")
def bootstrap_municipality_centroids(
    ctx: typer.Context,
):
    """Refresh the municipality centroids' DB view."""
    view_name = "public.municipality_centroids"
    index_name = "idx_municipality_centroids"
    drop_view_statement = sqlmodel.text(f"DROP MATERIALIZED VIEW IF EXISTS {view_name}")
    create_view_statement = sqlmodel.text(
        f"CREATE MATERIALIZED VIEW {view_name} "
        f"AS SELECT "
        f"id, "
        f"ST_Point(centroid_epsg_4326_lon, centroid_epsg_4326_lat, 4326) AS geom, "
        f"name, "
        f"province_name, "
        f"region_name "
        f"FROM municipality "
        f"WITH DATA"
    )
    create_index_statement = sqlmodel.text(
        f"CREATE INDEX {index_name} ON {view_name} USING gist (geom)"
    )
    drop_index_statement = sqlmodel.text(f"DROP INDEX IF EXISTS {index_name}")
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        session.execute(drop_view_statement)
        session.execute(drop_index_statement)
        session.execute(create_view_statement)
        session.execute(create_index_statement)
        session.commit()
    print("Done!")


@app.command("station-variables")
def bootstrap_station_variables(
    variable: Annotated[
        str,
        typer.Option(
            help=(
                "Name of the variable to process. If not provided, all "
                "variables are processed."
            )
        ),
    ] = None,
):
    """Refresh views with stations that have values for each variable."""
    observations_flows.refresh_station_variables(variable_name=variable)
    print("Done!")


@app.command("observation-variables")
def bootstrap_observation_variables(
    ctx: typer.Context,
):
    """Create initial observation variables."""
    variables = generate_variable_configurations()
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        for var_create in variables:
            try:
                db_variable = database.create_variable(session, var_create)
                print(f"Created observation variable {db_variable.name!r}")
            except IntegrityError as err:
                print(
                    f"Could not create observation "
                    f"variable {var_create.name!r}: {err}"
                )
                session.rollback()
    print("Done!")


@app.command("coverage-configuration-parameters")
def bootstrap_coverage_configuration_parameters(
    ctx: typer.Context,
):
    """Create initial coverage configuration parameters."""
    params = generate_configuration_parameters()
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        for param_create in params:
            try:
                db_param = database.create_configuration_parameter(
                    session, param_create
                )
                print(f"Created configuration parameter {db_param.name!r}")
            except IntegrityError as err:
                print(
                    f"Could not create configuration parameter "
                    f"{param_create.name!r}: {err}"
                )
                session.rollback()
    print("Done!")


@app.command("coverage-configurations")
def bootstrap_coverage_configurations(
    ctx: typer.Context,
):
    """Create initial coverage configurations."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        all_vars = database.collect_all_variables(session)
        all_conf_param_values = database.collect_all_configuration_parameter_values(
            session
        )
        variables = {v.name: v for v in all_vars}
        conf_param_values = {
            (pv.configuration_parameter.name, pv.name): pv
            for pv in all_conf_param_values
        }
    coverage_configurations = []
    coverage_configurations.extend(
        cdd_forecast.generate_configurations(conf_param_values)
    )
    coverage_configurations.extend(
        cdds_forecast.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        fd_forecast.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        hdds_forecast.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        hwdi_forecast.generate_configurations(conf_param_values)
    )
    coverage_configurations.extend(
        pr_forecast.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        r95ptot_forecast.generate_configurations(conf_param_values)
    )
    coverage_configurations.extend(
        snwdays_forecast.generate_configurations(conf_param_values)
    )
    coverage_configurations.extend(
        su30_forecast.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        tas_forecast.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        tasmax_forecast.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        tasmin_forecast.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        tr_forecast.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        cdds_historical.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        fd_historical.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        hdds_historical.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        prcptot_historical.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        su30_historical.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        tdd_historical.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        tnd_historical.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        tr_historical.generate_configurations(conf_param_values, variables)
    )
    coverage_configurations.extend(
        txd_historical.generate_configurations(conf_param_values, variables)
    )

    for cov_conf_create in coverage_configurations:
        try:
            db_cov_conf = database.create_coverage_configuration(
                session, cov_conf_create
            )
            print(f"Created coverage configuration {db_cov_conf.name!r}")
        except IntegrityError as err:
            print(
                f"Could not create coverage configuration "
                f"{cov_conf_create.name!r}: {err}"
            )
            session.rollback()

    print("Creating related coverage relationships...")
    all_cov_confs = {
        cc.name: cc for cc in database.collect_all_coverage_configurations(session)
    }

    to_update = {}
    for name, related_names in {
        **cdd_forecast.get_related_map(),
        **cdds_forecast.get_related_map(),
        **fd_forecast.get_related_map(),
        **hdds_forecast.get_related_map(),
        **hwdi_forecast.get_related_map(),
        **pr_forecast.get_related_map(),
        **r95ptot_forecast.get_related_map(),
        **snwdays_forecast.get_related_map(),
        **su30_forecast.get_related_map(),
        **tas_forecast.get_related_map(),
        **tasmax_forecast.get_related_map(),
        **tasmin_forecast.get_related_map(),
        **tr_forecast.get_related_map(),
    }.items():
        to_update[name] = {
            "related": related_names,
        }

    for name, uncertainties in {
        **cdd_forecast.get_uncertainty_map(),
        **cdds_forecast.get_uncertainty_map(),
        **fd_forecast.get_uncertainty_map(),
        **hdds_forecast.get_uncertainty_map(),
        **hwdi_forecast.get_uncertainty_map(),
        **pr_forecast.get_uncertainty_map(),
        **r95ptot_forecast.get_uncertainty_map(),
        **snwdays_forecast.get_uncertainty_map(),
        **su30_forecast.get_uncertainty_map(),
        **tas_forecast.get_uncertainty_map(),
        **tasmax_forecast.get_uncertainty_map(),
        **tasmin_forecast.get_uncertainty_map(),
        **tr_forecast.get_uncertainty_map(),
    }.items():
        info = to_update.setdefault(name, {})
        info["uncertainties"] = uncertainties

    for name, info in to_update.items():
        main_cov_conf = all_cov_confs[name]
        secondaries = info.get("related")
        uncertainties = info.get("uncertainties")
        update_kwargs = {}
        if secondaries is not None:
            secondary_cov_confs = [
                cc for name, cc in all_cov_confs.items() if name in secondaries
            ]
            update_kwargs["secondary_coverage_configurations_ids"] = [
                cc.id for cc in secondary_cov_confs
            ]
        else:
            update_kwargs["secondary_coverage_configurations_ids"] = []
        if uncertainties is not None:
            lower_uncert_id = [
                cc.id for name, cc in all_cov_confs.items() if name == uncertainties[0]
            ][0]
            upper_uncert_id = [
                cc.id for name, cc in all_cov_confs.items() if name == uncertainties[1]
            ][0]
            update_kwargs.update(
                uncertainty_lower_bounds_coverage_configuration_id=lower_uncert_id,
                uncertainty_upper_bounds_coverage_configuration_id=upper_uncert_id,
            )
        cov_update = CoverageConfigurationUpdate(
            **main_cov_conf.model_dump(
                exclude={
                    "uncertainty_lower_bounds_coverage_configuration_id",
                    "uncertainty_upper_bounds_coverage_configuration_id",
                    "secondary_coverage_configurations_ids",
                    "possible_values",
                }
            ),
            **update_kwargs,
            possible_values=[
                ConfigurationParameterPossibleValueUpdate(
                    configuration_parameter_value_id=pv.configuration_parameter_value_id
                )
                for pv in main_cov_conf.possible_values
            ],
        )
        database.update_coverage_configuration(
            session,
            main_cov_conf,
            cov_update,
        )
