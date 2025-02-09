import json
from pathlib import Path
from typing import Annotated, Optional

import geojson_pydantic
import sqlmodel
import typer
from rich import print
from sqlalchemy.exc import IntegrityError

import arpav_ppcv.db.legacy
from .. import database
from .. import db
from ..prefect.flows import observations as observations_flows
from ..schemas import (
    municipalities,
)

from ..schemas.coverages import (
    ConfigurationParameterPossibleValueUpdate,
    CoverageConfigurationUpdate,
)

from .overview_series_configurations import (
    generate_observation_overview_series_configurations,
    generate_forecast_overview_series_configurations,
)
from .forecast_coverage_configurations import (
    cdd as cdd_forecast_coverage_configurations,
    cdds as cdds_forecast_coverage_configurations,
    fd as fd_forecast_coverage_configurations,
    hdds as hdds_forecast_coverage_configurations,
    hwdi as hwdi_forecast_coverage_configurations,
    pr as pr_forecast_coverage_configurations,
    r95ptot as r95ptot_forecast_coverage_configurations,
    snwdays as snwdays_forecast_coverage_configurations,
    su30 as su30_forecast_coverage_configurations,
    tas as tas_forecast_coverage_configurations,
    tasmax as tasmax_forecast_coverage_configurations,
    tasmin as tasmin_forecast_coverage_configurations,
    tr as tr_forecast_coverage_configurations,
)
from .historical_coverage_configurations import (
    cdds as cdds_historical_coverage_configurations,
    fd as fd_historical_coverage_configurations,
    hdds as hdds_historical_coverage_configurations,
    pr as pr_historical_coverage_configurations,
    su30 as su30_historical_coverage_configurations,
    tas as tas_historical_coverage_configurations,
    tasmax as tasmax_historical_coverage_configurations,
    tasmin as tasmin_historical_coverage_configurations,
    tr as tr_historical_coverage_configurations,
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
from .climaticindicators import (
    cdd as cdd_climatic_indicators,
    cdds as cdds_climatic_indicators,
    fd as fd_climatic_indicators,
    hdds as hdds_climatic_indicators,
    hwdi as hwdi_climatic_indicators,
    pr as pr_climatic_indicators,
    r95ptot as r95ptot_climatic_indicators,
    snwdays as snwdays_climatic_indicators,
    su30 as su30_climatic_indicators,
    tas as tas_climatic_indicators,
    tasmax as tasmax_climatic_indicators,
    tasmin as tasmin_climatic_indicators,
    tr as tr_climatic_indicators,
)
from .forecastmodels import generate_forecast_models
from .forecasttimewindows import generate_forecast_time_windows
from .observation_series_configurations import (
    generate_observation_series_configurations,
)
from .spatialregions import generate_spatial_regions

from .configurationparameters import generate_configuration_parameters

app = typer.Typer()


@app.command("municipalities")
def bootstrap_municipalities(
    ctx: typer.Context,
    municipalities_dataset: Annotated[
        Path,
        typer.Argument(
            help=(
                "Path to the municipalities geoJSON dataset. Example: "
                "/home/appuser/app/data/municipalities-istat-2021.geojson"
            )
        ),
    ],
    force: bool = False,
) -> None:
    """Bootstrap Italian municipalities"""
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


@app.command("climatic-indicators")
def bootstrap_climatic_indicators(
    ctx: typer.Context, name_filter: Optional[str] = None
):
    """Create initial climatic indicators."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        all_forecast_models = database.collect_all_forecast_models(session)
        forecast_model_ids = {fm.name: fm.id for fm in all_forecast_models}
        to_create = cdd_climatic_indicators.generate_climatic_indicators(
            forecast_model_ids
        )
        to_create.extend(
            cdds_climatic_indicators.generate_climatic_indicators(forecast_model_ids)
        )
        to_create.extend(
            fd_climatic_indicators.generate_climatic_indicators(forecast_model_ids)
        )
        to_create.extend(
            hdds_climatic_indicators.generate_climatic_indicators(forecast_model_ids)
        )
        to_create.extend(
            hwdi_climatic_indicators.generate_climatic_indicators(forecast_model_ids)
        )
        to_create.extend(
            pr_climatic_indicators.generate_climatic_indicators(forecast_model_ids)
        )
        to_create.extend(
            r95ptot_climatic_indicators.generate_climatic_indicators(forecast_model_ids)
        )
        to_create.extend(
            snwdays_climatic_indicators.generate_climatic_indicators(forecast_model_ids)
        )
        to_create.extend(
            su30_climatic_indicators.generate_climatic_indicators(forecast_model_ids)
        )
        to_create.extend(
            tas_climatic_indicators.generate_climatic_indicators(forecast_model_ids)
        )
        to_create.extend(
            tasmax_climatic_indicators.generate_climatic_indicators(forecast_model_ids)
        )
        to_create.extend(
            tasmin_climatic_indicators.generate_climatic_indicators(forecast_model_ids)
        )
        to_create.extend(
            tr_climatic_indicators.generate_climatic_indicators(forecast_model_ids)
        )
        for climatic_indicator_create in to_create:
            if name_filter is None or name_filter in climatic_indicator_create.name:
                try:
                    db_climatic_indicator = database.create_climatic_indicator(
                        session, climatic_indicator_create
                    )
                    print(
                        f"Created climatic indicator {db_climatic_indicator.identifier!r}"
                    )
                except IntegrityError as err:
                    print(
                        f"Could not create climatic indicator ("
                        f"{climatic_indicator_create.name!r}, "
                        f"{climatic_indicator_create.measure_type!r}, "
                        f"{climatic_indicator_create.aggregation_period!r}"
                        f"): {err}"
                    )
                    session.rollback()


@app.command("observation-series-configurations")
def bootstrap_observation_series_configurations(ctx: typer.Context):
    """Create initial observation series configurations."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        all_climatic_indicators = database.collect_all_climatic_indicators(session)
        to_generate = generate_observation_series_configurations(
            {ind.identifier: ind for ind in all_climatic_indicators}
        )
        for obs_series_create in to_generate:
            try:
                db_series_conf = database.create_observation_series_configuration(
                    session, obs_series_create
                )
                print(
                    f"Created observation series "
                    f"configuration {db_series_conf.identifier!r}"
                )
            except IntegrityError as err:
                print(f"Could not create observation series {to_generate!r}: {err}")
                session.rollback()


@app.command("coverage-configuration-parameters")
def bootstrap_coverage_configuration_parameters(
    ctx: typer.Context,
):
    """Create initial coverage configuration parameters."""
    params = generate_configuration_parameters()
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        for param_create in params:
            try:
                db_param = arpav_ppcv.db.legacy.create_configuration_parameter(
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
        all_conf_param_values = (
            arpav_ppcv.db.legacy.collect_all_configuration_parameter_values(session)
        )
        conf_param_values = {
            (pv.configuration_parameter.name, pv.name): pv
            for pv in all_conf_param_values
        }
        all_climatic_indicators = database.collect_all_climatic_indicators(session)
        clim_indicator_ids = {i.identifier: i.id for i in all_climatic_indicators}
    coverage_configurations = []
    coverage_configurations.extend(
        cdd_forecast.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        cdds_forecast.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        fd_forecast.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        hdds_forecast.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        hwdi_forecast.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        pr_forecast.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        r95ptot_forecast.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        snwdays_forecast.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        su30_forecast.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        tas_forecast.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        tasmax_forecast.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        tasmin_forecast.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        tr_forecast.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        cdds_historical.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        fd_historical.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        hdds_historical.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        prcptot_historical.generate_configurations(
            conf_param_values, clim_indicator_ids
        )
    )
    coverage_configurations.extend(
        su30_historical.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        tdd_historical.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        tnd_historical.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        tr_historical.generate_configurations(conf_param_values, clim_indicator_ids)
    )
    coverage_configurations.extend(
        txd_historical.generate_configurations(conf_param_values, clim_indicator_ids)
    )

    for cov_conf_create in coverage_configurations:
        try:
            db_cov_conf = arpav_ppcv.db.legacy.create_coverage_configuration(
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
        cc.name: cc
        for cc in arpav_ppcv.db.legacy.collect_all_coverage_configurations(session)
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
        arpav_ppcv.db.legacy.update_coverage_configuration(
            session,
            main_cov_conf,
            cov_update,
        )


@app.command("overview-series-configurations")
def bootstrap_overview_series_configurations(ctx: typer.Context):
    """Create initial overview series configurations."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        all_climatic_indicators = database.collect_all_climatic_indicators(session)
        clim_ind_ids = {ind.identifier: ind.id for ind in all_climatic_indicators}

        overview_obs_series_confs_to_create = (
            generate_observation_overview_series_configurations(
                climatic_indicator_ids=clim_ind_ids,
            )
        )
        for overview_obs in overview_obs_series_confs_to_create:
            try:
                db_overview_obs = db.create_observation_overview_series_configuration(
                    session, overview_obs
                )
                print(
                    f"Created observation overview series "
                    f"configuration {db_overview_obs.identifier!r}"
                )
            except IntegrityError as err:
                print(
                    f"Could not create observation overview series configuration "
                    f"{overview_obs!r}: {err}"
                )
                session.rollback()
        overview_forecast_series_confs_to_create = (
            generate_forecast_overview_series_configurations(
                climatic_indicator_ids=clim_ind_ids
            )
        )
        for overview_forecast in overview_forecast_series_confs_to_create:
            try:
                db_overview_forecast = db.create_forecast_overview_series_configuration(
                    session, overview_forecast
                )
                print(
                    f"Created forecast overview series "
                    f"configuration {db_overview_forecast.identifier!r}"
                )
            except IntegrityError as err:
                print(
                    f"Could not create forecast overview series configuration "
                    f"{overview_forecast!r}: {err}"
                )
                session.rollback()


@app.command("forecast-coverage-configurations")
def bootstrap_forecast_coverage_configurations(ctx: typer.Context):
    """Create initial forecast coverage configurations."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        all_climatic_indicators = database.collect_all_climatic_indicators(session)
        all_spatial_regions = database.collect_all_spatial_regions(session)
        all_forecast_models = database.collect_all_forecast_models(session)
        all_forecast_time_windows = database.collect_all_forecast_time_windows(session)
        all_observation_series_configurations = (
            database.collect_all_observation_series_configurations(session)
        )
        clim_ind_ids = {ind.identifier: ind.id for ind in all_climatic_indicators}
        region_ids = {sr.name: sr.id for sr in all_spatial_regions}
        forecast_model_ids = {fm.name: fm.id for fm in all_forecast_models}
        time_window_ids = {tw.name: tw.id for tw in all_forecast_time_windows}
        observation_series_configuration_ids = {
            osc.identifier: osc.id for osc in all_observation_series_configurations
        }

        to_create = cdd_forecast_coverage_configurations.generate_forecast_coverage_configurations(
            climatic_indicator_ids=clim_ind_ids,
            spatial_region_ids=region_ids,
            forecast_model_ids=forecast_model_ids,
            forecast_time_window_ids=time_window_ids,
            observation_series_configuration_ids=observation_series_configuration_ids,
        )
        to_create.extend(
            cdds_forecast_coverage_configurations.generate_forecast_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
                forecast_model_ids=forecast_model_ids,
                forecast_time_window_ids=time_window_ids,
                observation_series_configuration_ids=observation_series_configuration_ids,
            )
        )
        to_create.extend(
            fd_forecast_coverage_configurations.generate_forecast_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
                forecast_model_ids=forecast_model_ids,
                forecast_time_window_ids=time_window_ids,
                observation_series_configuration_ids=observation_series_configuration_ids,
            )
        )
        to_create.extend(
            hdds_forecast_coverage_configurations.generate_forecast_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
                forecast_model_ids=forecast_model_ids,
                forecast_time_window_ids=time_window_ids,
                observation_series_configuration_ids=observation_series_configuration_ids,
            )
        )
        to_create.extend(
            hwdi_forecast_coverage_configurations.generate_forecast_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
                forecast_model_ids=forecast_model_ids,
                forecast_time_window_ids=time_window_ids,
                observation_series_configuration_ids=observation_series_configuration_ids,
            )
        )
        to_create.extend(
            pr_forecast_coverage_configurations.generate_forecast_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
                forecast_model_ids=forecast_model_ids,
                forecast_time_window_ids=time_window_ids,
                observation_series_configuration_ids=observation_series_configuration_ids,
            )
        )
        to_create.extend(
            r95ptot_forecast_coverage_configurations.generate_forecast_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
                forecast_model_ids=forecast_model_ids,
                forecast_time_window_ids=time_window_ids,
                observation_series_configuration_ids=observation_series_configuration_ids,
            )
        )
        to_create.extend(
            snwdays_forecast_coverage_configurations.generate_forecast_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
                forecast_model_ids=forecast_model_ids,
                forecast_time_window_ids=time_window_ids,
                observation_series_configuration_ids=observation_series_configuration_ids,
            )
        )
        to_create.extend(
            su30_forecast_coverage_configurations.generate_forecast_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
                forecast_model_ids=forecast_model_ids,
                forecast_time_window_ids=time_window_ids,
                observation_series_configuration_ids=observation_series_configuration_ids,
            )
        )
        to_create.extend(
            tas_forecast_coverage_configurations.generate_forecast_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
                forecast_model_ids=forecast_model_ids,
                forecast_time_window_ids=time_window_ids,
                observation_series_configuration_ids=observation_series_configuration_ids,
            )
        )
        to_create.extend(
            tasmax_forecast_coverage_configurations.generate_forecast_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
                forecast_model_ids=forecast_model_ids,
                forecast_time_window_ids=time_window_ids,
                observation_series_configuration_ids=observation_series_configuration_ids,
            )
        )
        to_create.extend(
            tasmin_forecast_coverage_configurations.generate_forecast_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
                forecast_model_ids=forecast_model_ids,
                forecast_time_window_ids=time_window_ids,
                observation_series_configuration_ids=observation_series_configuration_ids,
            )
        )
        to_create.extend(
            tr_forecast_coverage_configurations.generate_forecast_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
                forecast_model_ids=forecast_model_ids,
                forecast_time_window_ids=time_window_ids,
                observation_series_configuration_ids=observation_series_configuration_ids,
            )
        )
        for forecast_coverage_configuration_create in to_create:
            try:
                db_forecast_cov_conf = database.create_forecast_coverage_configuration(
                    session, forecast_coverage_configuration_create
                )
                print(
                    f"Created forecast coverage "
                    f"configuration {db_forecast_cov_conf.identifier!r}"
                )
            except IntegrityError as err:
                print(
                    f"Could not create forecast coverage configuration "
                    f"{forecast_coverage_configuration_create!r}: {err}"
                )
                session.rollback()


@app.command("historical-coverage-configurations")
def bootstrap_historical_coverage_configurations(ctx: typer.Context):
    """Create initial historical coverage configurations."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        all_climatic_indicators = database.collect_all_climatic_indicators(session)
        all_spatial_regions = database.collect_all_spatial_regions(session)
        clim_ind_ids = {ind.identifier: ind.id for ind in all_climatic_indicators}
        region_ids = {sr.name: sr.id for sr in all_spatial_regions}

        to_create = cdds_historical_coverage_configurations.generate_historical_coverage_configurations(
            climatic_indicator_ids=clim_ind_ids,
            spatial_region_ids=region_ids,
        )
        to_create.extend(
            fd_historical_coverage_configurations.generate_historical_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
            )
        )
        to_create.extend(
            hdds_historical_coverage_configurations.generate_historical_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
            )
        )
        to_create.extend(
            pr_historical_coverage_configurations.generate_historical_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
            )
        )
        to_create.extend(
            su30_historical_coverage_configurations.generate_historical_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
            )
        )
        to_create.extend(
            tas_historical_coverage_configurations.generate_historical_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
            )
        )
        to_create.extend(
            tasmax_historical_coverage_configurations.generate_historical_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
            )
        )
        to_create.extend(
            tasmin_historical_coverage_configurations.generate_historical_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
            )
        )
        to_create.extend(
            tr_historical_coverage_configurations.generate_historical_coverage_configurations(
                climatic_indicator_ids=clim_ind_ids,
                spatial_region_ids=region_ids,
            )
        )
        for historical_coverage_configuration_create in to_create:
            try:
                db_historical_cov_conf = db.create_historical_coverage_configuration(
                    session, historical_coverage_configuration_create
                )
                print(
                    f"Created historical coverage "
                    f"configuration {db_historical_cov_conf.identifier!r}"
                )
            except IntegrityError as err:
                print(
                    f"Could not create historical coverage configuration "
                    f"{historical_coverage_configuration_create!r}: {err}"
                )
                session.rollback()


@app.command("spatial-regions")
def bootstrap_spatial_regions(
    ctx: typer.Context,
    region_bounds_base_directory: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            help=(
                "Path to the directory that holds geoJSON files with the "
                "spatial boundaries of spatial regions. Example: "
                "/home/appuser/app/data/spatial-regions"
            ),
        ),
    ],
):
    """Create initial spatial regions."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        existing = database.collect_all_spatial_regions(session)
        for spatial_region_create in generate_spatial_regions(
            region_bounds_base_directory
        ):
            if spatial_region_create.name not in (sr.name for sr in existing):
                try:
                    db_spatial_region = database.create_spatial_region(
                        session, spatial_region_create
                    )
                    print(f"Created spatial region {db_spatial_region.name!r}")
                except IntegrityError as err:
                    print(
                        f"Could not create spatial region {spatial_region_create.name!r}: {err}"
                    )
                    session.rollback()
            else:
                print(
                    f"Spatial region {spatial_region_create.name!r} already "
                    f"exists - skipping",
                )


@app.command("forecast-models")
def bootstrap_forecast_models(ctx: typer.Context):
    """Create initial forecast models."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        existing = database.collect_all_forecast_models(session)
        for forecast_model_create in generate_forecast_models():
            if forecast_model_create.name not in (db_fm.name for db_fm in existing):
                try:
                    db_forecast_model = database.create_forecast_model(
                        session, forecast_model_create
                    )
                    print(f"Created forecast model {db_forecast_model.name!r}")
                except IntegrityError as err:
                    print(
                        f"Could not create forecast model {forecast_model_create!r}: {err}"
                    )
                    session.rollback()
            else:
                print(
                    f"Forecast model {forecast_model_create.name!r} already "
                    f"exists - skipping",
                )


@app.command("forecast-time-windows")
def bootstrap_forecast_time_windows(ctx: typer.Context):
    """Create initial forecast time windows."""
    with sqlmodel.Session(ctx.obj["engine"]) as session:
        existing = database.collect_all_forecast_time_windows(session)
        for forecast_time_window_create in generate_forecast_time_windows():
            if forecast_time_window_create.name not in (tw.name for tw in existing):
                try:
                    db_forecast_time_window = database.create_forecast_time_window(
                        session, forecast_time_window_create
                    )
                    print(
                        f"Created forecast time window {db_forecast_time_window.name!r}"
                    )
                except IntegrityError as err:
                    print(
                        f"Could not create forecast time "
                        f"window {forecast_time_window_create!r}: {err}"
                    )
                    session.rollback()
            else:
                print(
                    f"Forecast time window {forecast_time_window_create.name!r} already exists"
                )


@app.command("all")
def perform_full_bootstrap(
    ctx: typer.Context,
    region_bounds_base_directory: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            help=(
                "Path to the directory that holds geoJSON files with the "
                "spatial boundaries of spatial regions. Example: "
                "/home/appuser/app/data/spatial-regions"
            ),
        ),
    ],
    municipalities_dataset: Annotated[
        Path,
        typer.Argument(
            help=(
                "Path to the municipalities geoJSON dataset. Example: "
                "/home/appuser/app/data/municipalities-istat-2021.geojson"
            )
        ),
    ],
):
    """Create all initial entities.

    This command will populate the system database with all bootstrappable
    entities.
    """
    ctx.invoke(
        bootstrap_spatial_regions,
        ctx=ctx,
        region_bounds_base_directory=region_bounds_base_directory,
    )
    ctx.invoke(
        bootstrap_municipalities,
        ctx=ctx,
        municipalities_dataset=municipalities_dataset,
        force=True,
    )
    ctx.invoke(bootstrap_forecast_models, ctx=ctx)
    ctx.invoke(bootstrap_forecast_time_windows, ctx=ctx)
    ctx.invoke(bootstrap_climatic_indicators, ctx=ctx)
    ctx.invoke(bootstrap_observation_series_configurations, ctx=ctx)
    ctx.invoke(bootstrap_forecast_coverage_configurations, ctx=ctx)
    ctx.invoke(bootstrap_historical_coverage_configurations, ctx=ctx)
    ctx.invoke(bootstrap_overview_series_configurations, ctx=ctx)
    print("All done!")
