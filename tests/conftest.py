import csv
import datetime as dt
import io
import random
from pathlib import Path

import geojson_pydantic
import pandas as pd
import pytest
import shapely.io
import shapely.geometry
import sqlmodel
import typer
from fastapi import Depends
from fastapi.testclient import TestClient
from geoalchemy2.shape import from_shape
from typer.testing import CliRunner

from arpav_cline import (
    config,
    db,
    main,
)
from arpav_cline.bootstrapper.yearperiods import (
    generate_forecast_year_period_groups,
    generate_historical_year_period_groups,
)
from arpav_cline.schemas import (
    base,
    climaticindicators,
    dataseries,
    coverages,
    observations,
    static,
)
from arpav_cline.webapp import dependencies
from arpav_cline.webapp.app import create_app_from_settings
from arpav_cline.webapp.api_v2.app import create_app as create_v2_app
from arpav_cline.bootstrapper.forecastmodels import (
    generate_forecast_models,
    generate_forecast_model_groups,
)
from arpav_cline.bootstrapper.forecasttimewindows import generate_forecast_time_windows
from arpav_cline.bootstrapper.spatialregions import generate_spatial_regions
from arpav_cline.bootstrapper.climaticindicators.cdd import (
    generate_climatic_indicators as generate_cdd_climatic_indicators,
)
from arpav_cline.bootstrapper.climaticindicators.cdds import (
    generate_climatic_indicators as generate_cdds_climatic_indicators,
)
from arpav_cline.bootstrapper.climaticindicators.fd import (
    generate_climatic_indicators as generate_fd_climatic_indicators,
)
from arpav_cline.bootstrapper.climaticindicators.hdds import (
    generate_climatic_indicators as generate_hdds_climatic_indicators,
)
from arpav_cline.bootstrapper.climaticindicators.hwdi import (
    generate_climatic_indicators as generate_hwdi_climatic_indicators,
)
from arpav_cline.bootstrapper.climaticindicators.pr import (
    generate_climatic_indicators as generate_pr_climatic_indicators,
)
from arpav_cline.bootstrapper.climaticindicators.r95ptot import (
    generate_climatic_indicators as generate_r95ptot_climatic_indicators,
)
from arpav_cline.bootstrapper.climaticindicators.snwdays import (
    generate_climatic_indicators as generate_snwdays_climatic_indicators,
)
from arpav_cline.bootstrapper.climaticindicators.su30 import (
    generate_climatic_indicators as generate_su30_climatic_indicators,
)
from arpav_cline.bootstrapper.climaticindicators.tas import (
    generate_climatic_indicators as generate_tas_climatic_indicators,
)
from arpav_cline.bootstrapper.climaticindicators.tasmax import (
    generate_climatic_indicators as generate_tasmax_climatic_indicators,
)
from arpav_cline.bootstrapper.climaticindicators.tasmin import (
    generate_climatic_indicators as generate_tasmin_climatic_indicators,
)
from arpav_cline.bootstrapper.climaticindicators.tr import (
    generate_climatic_indicators as generate_tr_climatic_indicators,
)

from arpav_cline.bootstrapper.forecast_coverage_configurations.cdd import (
    generate_forecast_coverage_configurations as generate_cdd_forecast_coverage_configurations,
)
from arpav_cline.bootstrapper.forecast_coverage_configurations.cdds import (
    generate_forecast_coverage_configurations as generate_cdds_forecast_coverage_configurations,
)
from arpav_cline.bootstrapper.forecast_coverage_configurations.fd import (
    generate_forecast_coverage_configurations as generate_fd_forecast_coverage_configurations,
)
from arpav_cline.bootstrapper.forecast_coverage_configurations.hdds import (
    generate_forecast_coverage_configurations as generate_hdds_forecast_coverage_configurations,
)
from arpav_cline.bootstrapper.forecast_coverage_configurations.hwdi import (
    generate_forecast_coverage_configurations as generate_hwdi_forecast_coverage_configurations,
)
from arpav_cline.bootstrapper.forecast_coverage_configurations.pr import (
    generate_forecast_coverage_configurations as generate_pr_forecast_coverage_configurations,
)
from arpav_cline.bootstrapper.forecast_coverage_configurations.r95ptot import (
    generate_forecast_coverage_configurations as generate_r95ptot_forecast_coverage_configurations,
)
from arpav_cline.bootstrapper.forecast_coverage_configurations.snwdays import (
    generate_forecast_coverage_configurations as generate_snwdays_forecast_coverage_configurations,
)
from arpav_cline.bootstrapper.forecast_coverage_configurations.su30 import (
    generate_forecast_coverage_configurations as generate_su30_forecast_coverage_configurations,
)
from arpav_cline.bootstrapper.forecast_coverage_configurations.tas import (
    generate_forecast_coverage_configurations as generate_tas_forecast_coverage_configurations,
)
from arpav_cline.bootstrapper.forecast_coverage_configurations.tasmax import (
    generate_forecast_coverage_configurations as generate_tasmax_forecast_coverage_configurations,
)
from arpav_cline.bootstrapper.forecast_coverage_configurations.tasmin import (
    generate_forecast_coverage_configurations as generate_tasmin_forecast_coverage_configurations,
)
from arpav_cline.bootstrapper.forecast_coverage_configurations.tr import (
    generate_forecast_coverage_configurations as generate_tr_forecast_coverage_configurations,
)

from arpav_cline.bootstrapper.historical_coverage_configurations.cdds import (
    generate_historical_coverage_configurations as generate_cdds_historical_coverage_configurations,
)
from arpav_cline.bootstrapper.historical_coverage_configurations.fd import (
    generate_historical_coverage_configurations as generate_fd_historical_coverage_configurations,
)
from arpav_cline.bootstrapper.historical_coverage_configurations.hdds import (
    generate_historical_coverage_configurations as generate_hdds_historical_coverage_configurations,
)
from arpav_cline.bootstrapper.historical_coverage_configurations.pr import (
    generate_historical_coverage_configurations as generate_pr_historical_coverage_configurations,
)
from arpav_cline.bootstrapper.historical_coverage_configurations.su30 import (
    generate_historical_coverage_configurations as generate_su30_historical_coverage_configurations,
)
from arpav_cline.bootstrapper.historical_coverage_configurations.tas import (
    generate_historical_coverage_configurations as generate_tas_historical_coverage_configurations,
)
from arpav_cline.bootstrapper.historical_coverage_configurations.tasmax import (
    generate_historical_coverage_configurations as generate_tasmax_historical_coverage_configurations,
)
from arpav_cline.bootstrapper.historical_coverage_configurations.tasmin import (
    generate_historical_coverage_configurations as generate_tasmin_historical_coverage_configurations,
)
from arpav_cline.bootstrapper.historical_coverage_configurations.tr import (
    generate_historical_coverage_configurations as generate_tr_historical_coverage_configurations,
)
from arpav_cline.bootstrapper.overview_series_configurations import (
    generate_forecast_overview_series_configurations,
    generate_observation_overview_series_configurations,
)
from arpav_cline.bootstrapper.observation_series_configurations import (
    generate_observation_series_configurations,
)


@pytest.fixture
def settings() -> config.ArpavPpcvSettings:
    settings = _override_get_settings()
    yield settings


@pytest.fixture
def app(settings):
    yield create_app_from_settings(settings)


@pytest.fixture
def v2_app(settings):
    app = create_v2_app(settings)
    app.dependency_overrides[dependencies.get_db_session] = _override_get_db_session
    app.dependency_overrides[dependencies.get_db_engine] = _override_get_db_engine
    app.dependency_overrides[dependencies.get_settings] = _override_get_settings
    yield app


@pytest.fixture()
def arpav_db(settings):
    """Provides a clean DB."""
    engine = next(_override_get_db_engine(settings))
    sqlmodel.SQLModel.metadata.create_all(engine)
    yield
    sqlmodel.SQLModel.metadata.drop_all(engine)
    # tables_to_truncate = list(sqlmodel.SQLModel.metadata.tables.keys())
    # tables_fragment = ', '.join(f'"{t}"' for t in tables_to_truncate)
    # with engine.connect() as connection:
    #     connection.execute(text(f"TRUNCATE {tables_fragment}"))


@pytest.fixture()
def arpav_db_session(arpav_db, settings):
    engine = next(_override_get_db_engine(settings))
    with sqlmodel.Session(autocommit=False, autoflush=False, bind=engine) as session:
        yield session


@pytest.fixture()
def test_client(app) -> TestClient:
    yield TestClient(app)


@pytest.fixture()
def test_client_v2_app(v2_app) -> TestClient:
    """This fixture exists in order to ensure app overrides work.

    See https://github.com/tiangolo/fastapi/issues/3651#issuecomment-892138488
    """
    yield TestClient(v2_app)


@pytest.fixture()
def cli_runner():
    runner = CliRunner(mix_stderr=False)
    yield runner


@pytest.fixture()
def cli_app(settings, arpav_db):
    # replaces the default callback with another one, with different settings
    @main.app.callback()
    def _override_main_app_callback(ctx: typer.Context):
        cli_config = ctx.obj or {}
        cli_config["settings"] = settings
        engine = next(_override_get_db_engine(settings))
        # engine = database.get_engine(settings, use_test_db=True)
        cli_config["engine"] = engine
        ctx.obj = cli_config

    yield main.app


@pytest.fixture()
def sample_real_station(arpav_db_session) -> observations.ObservationStation:
    db_station = observations.ObservationStation(
        code="arpa_v-104",
        altitude_m=67,
        name="Villafranca di Verona",
        active_since=dt.date(1990, 11, 20),
        active_until=None,
        geom=from_shape(
            shapely.io.from_geojson(
                geojson_pydantic.Point(
                    type="Point", coordinates=(10.83262812, 45.3724202)
                ).model_dump_json()
            )
        ),
        managed_by=static.ObservationStationManager.ARPAV,
    )
    arpav_db_session.add(db_station)
    arpav_db_session.commit()
    arpav_db_session.refresh(db_station)
    return db_station


@pytest.fixture()
def sample_stations(arpav_db_session) -> list[observations.ObservationStation]:
    db_stations = []
    for i in range(50):
        manager = random.choice(list(static.ObservationStationManager))
        db_stations.append(
            observations.ObservationStation(
                code=f"{manager.value}-{i}",
                geom=from_shape(
                    shapely.io.from_geojson(
                        geojson_pydantic.Point(
                            type="Point", coordinates=(i, 2 * i)
                        ).model_dump_json()
                    )
                ),
                altitude_m=2,
                name=f"teststation{i}name",
                managed_by=manager,
            )
        )
    for db_station in db_stations:
        arpav_db_session.add(db_station)
    arpav_db_session.commit()
    for db_station in db_stations:
        arpav_db_session.refresh(db_station)
    return db_stations


@pytest.fixture()
def sample_real_spatial_regions(
    arpav_db_session,
) -> list[base.SpatialRegion]:
    created = []
    geoms_base_path = Path(__file__).parents[1] / "data/spatial-regions"
    for spatial_region_to_create in generate_spatial_regions(geoms_base_path):
        created.append(
            db.create_spatial_region(arpav_db_session, spatial_region_to_create)
        )
    return created


@pytest.fixture()
def sample_real_forecast_models(
    arpav_db_session,
) -> list[coverages.ForecastModel]:
    created = []
    for forecast_model_to_create in generate_forecast_models():
        created.append(
            db.create_forecast_model(arpav_db_session, forecast_model_to_create)
        )
    return created


@pytest.fixture()
def sample_real_historical_year_period_groups(
    arpav_db_session,
) -> list[coverages.HistoricalYearPeriodGroup]:
    created = []
    for year_group_create in generate_historical_year_period_groups():
        created.append(
            db.create_historical_year_period_group(arpav_db_session, year_group_create)
        )
    return created


@pytest.fixture()
def sample_real_forecast_year_period_groups(
    arpav_db_session,
) -> list[coverages.ForecastYearPeriodGroup]:
    created = []
    for year_group_create in generate_forecast_year_period_groups():
        created.append(
            db.create_forecast_year_period_group(arpav_db_session, year_group_create)
        )
    return created


@pytest.fixture()
def sample_real_forecast_model_groups(
    arpav_db_session,
    sample_real_forecast_models,
) -> list[coverages.ForecastModelGroup]:
    created = []
    forecast_model_ids = {fm.name: fm.id for fm in sample_real_forecast_models}

    for item_create in generate_forecast_model_groups(forecast_model_ids):
        created.append(db.create_forecast_model_group(arpav_db_session, item_create))
    return created


@pytest.fixture()
def sample_real_forecast_time_windows(
    arpav_db_session,
) -> list[coverages.ForecastTimeWindow]:
    created = []
    for time_window_to_create in generate_forecast_time_windows():
        created.append(
            db.create_forecast_time_window(arpav_db_session, time_window_to_create)
        )
    return created


@pytest.fixture()
def sample_real_climatic_indicators(
    arpav_db_session,
    sample_real_forecast_models,
) -> list[climaticindicators.ClimaticIndicator]:
    forecast_model_ids = {fm.name: fm.id for fm in sample_real_forecast_models}
    to_create = []
    for handler in (
        generate_cdd_climatic_indicators,
        generate_cdds_climatic_indicators,
        generate_fd_climatic_indicators,
        generate_hdds_climatic_indicators,
        generate_hwdi_climatic_indicators,
        generate_pr_climatic_indicators,
        generate_r95ptot_climatic_indicators,
        generate_snwdays_climatic_indicators,
        generate_su30_climatic_indicators,
        generate_tas_climatic_indicators,
        generate_tasmax_climatic_indicators,
        generate_tasmin_climatic_indicators,
        generate_tr_climatic_indicators,
    ):
        to_create.extend(handler(forecast_model_ids))
    created = []
    for indicator_to_create in to_create:
        created.append(
            db.create_climatic_indicator(arpav_db_session, indicator_to_create)
        )
    return created


@pytest.fixture()
def sample_real_observation_series_configurations(
    arpav_db_session,
    sample_real_climatic_indicators,
):
    climatic_indicator_ids = {
        ci.identifier: ci.id for ci in sample_real_climatic_indicators
    }
    to_create = generate_observation_series_configurations(climatic_indicator_ids)
    created = []
    for observation_series_conf_to_create in to_create:
        created.append(
            db.create_observation_series_configuration(
                arpav_db_session, observation_series_conf_to_create
            )
        )
    return created


@pytest.fixture()
def sample_real_observation_overview_series_configurations(
    arpav_db_session,
    sample_real_climatic_indicators,
):
    climatic_indicator_ids = {
        ci.identifier: ci.id for ci in sample_real_climatic_indicators
    }
    to_create = generate_observation_overview_series_configurations(
        climatic_indicator_ids
    )
    created = []
    for series_conf_to_create in to_create:
        created.append(
            db.create_observation_overview_series_configuration(
                arpav_db_session, series_conf_to_create
            )
        )
    return created


@pytest.fixture()
def sample_real_forecast_overview_series_configurations(
    arpav_db_session,
    sample_real_climatic_indicators,
):
    climatic_indicator_ids = {
        ci.identifier: ci.id for ci in sample_real_climatic_indicators
    }
    to_create = generate_forecast_overview_series_configurations(climatic_indicator_ids)
    created = []
    for series_conf_to_create in to_create:
        created.append(
            db.create_forecast_overview_series_configuration(
                arpav_db_session, series_conf_to_create
            )
        )
    return created


@pytest.fixture()
def sample_real_forecast_coverage_configurations(
    arpav_db_session,
    sample_real_spatial_regions,
    sample_real_climatic_indicators,
    sample_real_forecast_model_groups,
    sample_real_forecast_time_windows,
    sample_real_forecast_year_period_groups,
    sample_real_observation_series_configurations,
):
    spatial_region_ids = {sr.name: sr.id for sr in sample_real_spatial_regions}
    climatic_indicator_ids = {
        ci.identifier: ci.id for ci in sample_real_climatic_indicators
    }
    forecast_model_group_ids = {
        fmg.name: fmg.id for fmg in sample_real_forecast_model_groups
    }
    time_window_ids = {tw.name: tw.id for tw in sample_real_forecast_time_windows}
    obs_series_confs_ids = {
        osc.identifier: osc.id for osc in sample_real_observation_series_configurations
    }
    year_period_group_ids = {
        ypg.name: ypg.id for ypg in sample_real_forecast_year_period_groups
    }
    to_create = []
    for handler in (
        generate_cdd_forecast_coverage_configurations,
        generate_cdds_forecast_coverage_configurations,
        generate_fd_forecast_coverage_configurations,
        generate_hdds_forecast_coverage_configurations,
        generate_hwdi_forecast_coverage_configurations,
        generate_pr_forecast_coverage_configurations,
        generate_r95ptot_forecast_coverage_configurations,
        generate_snwdays_forecast_coverage_configurations,
        generate_su30_forecast_coverage_configurations,
        generate_tas_forecast_coverage_configurations,
        generate_tasmax_forecast_coverage_configurations,
        generate_tasmin_forecast_coverage_configurations,
        generate_tr_forecast_coverage_configurations,
    ):
        to_create.extend(
            handler(
                climatic_indicator_ids=climatic_indicator_ids,
                spatial_region_ids=spatial_region_ids,
                forecast_time_window_ids=time_window_ids,
                year_period_groups=year_period_group_ids,
                forecast_model_groups=forecast_model_group_ids,
                observation_series_configuration_ids=obs_series_confs_ids,
            )
        )
    created = []
    for forecast_cov_conf_to_create in to_create:
        created.append(
            db.create_forecast_coverage_configuration(
                arpav_db_session, forecast_cov_conf_to_create
            )
        )
    return created


@pytest.fixture()
def sample_real_historical_coverage_configurations(
    arpav_db_session,
    sample_real_spatial_regions,
    sample_real_climatic_indicators,
    sample_real_historical_year_period_groups,
    sample_real_observation_series_configurations,
):
    spatial_region_ids = {sr.name: sr.id for sr in sample_real_spatial_regions}
    climatic_indicator_ids = {
        ci.identifier: ci.id for ci in sample_real_climatic_indicators
    }
    obs_series_confs_ids = {
        osc.identifier: osc.id for osc in sample_real_observation_series_configurations
    }
    year_period_group_ids = {
        ypg.name: ypg.id for ypg in sample_real_historical_year_period_groups
    }
    to_create = []
    for handler in (
        generate_cdds_historical_coverage_configurations,
        generate_fd_historical_coverage_configurations,
        generate_hdds_historical_coverage_configurations,
        generate_pr_historical_coverage_configurations,
        generate_su30_historical_coverage_configurations,
        generate_tas_historical_coverage_configurations,
        generate_tasmax_historical_coverage_configurations,
        generate_tasmin_historical_coverage_configurations,
        generate_tr_historical_coverage_configurations,
    ):
        to_create.extend(
            handler(
                climatic_indicator_ids=climatic_indicator_ids,
                spatial_region_ids=spatial_region_ids,
                year_period_groups=year_period_group_ids,
                observation_series_configuration_ids=obs_series_confs_ids,
            )
        )
    created = []
    for cov_conf_to_create in to_create:
        created.append(
            db.create_historical_coverage_configuration(
                arpav_db_session, cov_conf_to_create
            )
        )
    return created


@pytest.fixture()
def sample_tas_historical_data_series(
    arpav_db_session,
    sample_real_historical_coverage_configurations,
    sample_tas_csv_data: dict[str, str],
) -> dataseries.HistoricalDataSeries:
    historical_cov = db.get_historical_coverage(
        arpav_db_session, "historical-tas-absolute-annual-arpa_v-all_seasons-winter"
    )
    raw_data_buffer = io.StringIO(sample_tas_csv_data["tas"])
    raw_data_buffer.seek(0)
    df = pd.read_csv(raw_data_buffer)
    df.index = pd.DatetimeIndex(pd.to_datetime(df["time"]))
    series = df['tas[unit="degC"]']
    result = dataseries.HistoricalDataSeries(
        coverage=historical_cov,
        dataset_type=static.DatasetType.MAIN,
        processing_method=static.HistoricalTimeSeriesProcessingMethod.NO_PROCESSING,
        temporal_start=df.index[0].date(),
        temporal_end=df.index[-1].date(),
        location=shapely.geometry.Point(
            df['longitude[unit="degrees_east"]'][0],
            df['latitude[unit="degrees_north"]'][0],
        ),
    )
    series.name = result.identifier
    result.data_ = series
    return result


@pytest.fixture()
def sample_tas_csv_data():
    csv_sample = """
    time,station,latitude[unit="degrees_north"],longitude[unit="degrees_east"],{variable}[unit="degC"]
    1976-02-15T12:00:00Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,2.640222
    1977-02-14T17:57:04.390Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.131799
    1978-02-14T23:54:08.780Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,2.9139953
    1979-02-15T05:51:13.171Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.9587035
    1980-02-15T11:48:17.561Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.5937133
    1981-02-14T17:45:21.951Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.7524657
    1982-02-14T23:42:26.341Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.8758483
    1983-02-15T05:39:30.732Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.5044188
    1984-02-15T11:36:35.122Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,2.284906
    1985-02-14T17:33:39.512Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.2877746
    1986-02-14T23:30:43.902Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.3630004
    1987-02-15T05:27:48.293Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,2.611383
    1988-02-15T11:24:52.683Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.5216613
    1989-02-14T17:21:57.073Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.7202392
    1990-02-14T23:19:01.463Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.1510253
    1991-02-15T05:16:05.854Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.5604796
    1992-02-15T11:13:10.244Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,2.830011
    1993-02-14T17:10:14.634Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.3071227
    1994-02-14T23:07:19.024Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.4500365
    1995-02-15T05:04:23.415Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.8746276
    1996-02-15T11:01:27.805Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.0703063
    1997-02-14T16:58:32.195Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.0519347
    1998-02-14T22:55:36.585Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.9186034
    1999-02-15T04:52:40.976Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.3369384
    2000-02-15T10:49:45.366Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.413568
    2001-02-14T16:46:49.756Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.7551513
    2002-02-14T22:43:54.146Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.6977477
    2003-02-15T04:40:58.537Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.3922668
    2004-02-15T10:38:02.927Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.298364
    2005-02-14T16:35:07.317Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.7203918
    2006-02-14T22:32:11.707Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,5.3815246
    2007-02-15T04:29:16.098Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.568109
    2008-02-15T10:26:20.488Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.08172
    2009-02-14T16:23:24.878Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.7300353
    2010-02-14T22:20:29.268Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.7169127
    2011-02-15T04:17:33.659Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.357843
    2012-02-15T10:14:38.049Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,2.469293
    2013-02-14T16:11:42.439Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.4914489
    2014-02-14T22:08:46.829Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.1174865
    2015-02-15T04:05:51.220Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,4.338098
    2016-02-15T10:02:55.610Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,5.111444
    2017-02-14T16:00:00Z,GridPointRequestedAt[44.952N_11.547E],44.953,11.547,3.911859
    """.strip()
    return {
        "tas": csv_sample.format(variable="tas"),
        "tas_stddown": csv_sample.format(variable="tas_stddown"),
        "tas_stdup": csv_sample.format(variable="tas_stdup"),
    }


@pytest.fixture()
def sample_monthly_measurements(
    arpav_db_session,
    sample_real_climatic_indicators,
    sample_real_station,
) -> list[observations.ObservationMeasurement]:
    raw_measurements = io.StringIO(
        """
    value,date
    -8.23,1987-01-01
    -4.34,1988-01-01
    -2.42,1989-01-01
    -3.319,1990-01-01
    -6.142,1991-01-01
    -3.258,1992-01-01
    -3.173,1993-01-01
    -3.869,1994-01-01
    -7.462,1995-01-01
    -4.689,1996-01-01
    -2.899,1997-01-01
    -4.719,1998-01-01
    -4.364,1999-01-01
    -5.684,2000-01-01
    -5.417,2001-01-01
    -3.836,2002-01-01
    -6.316,2003-01-01
    -7.396,2004-01-01
    -6.101,2005-01-01
    -6.783,2006-01-01
    -2.012,2007-01-01
    -2.732,2008-01-01
    -6.439,2009-01-01
    -7.29,2010-01-01
    -5.125,2011-01-01
    -5.426,2012-01-01
    -4.209,2013-01-01
    -2.847,2014-01-01
    -3.711,2015-01-01
    -4.264,2016-01-01
    -7.088,2017-01-01
    -3.445,2018-01-01
    -6.142,2019-01-01
    -2.529,2020-01-01
    -7.025,2021-01-01
    -2.885,2022-01-01
    -3.724,2023-01-01
    -3.711,2024-01-01
    -4.191,1987-02-01
    -6.257,1988-02-01
    -1.728,1989-02-01
    -1.483,1990-02-01
    -7.46,1991-02-01
    -3.505,1992-02-01
    -4.174,1993-02-01
    -5.704,1994-02-01
    -2.047,1995-02-01
    -7.12,1996-02-01
    -2.522,1997-02-01
    -0.488,1998-02-01
    -5.811,1999-02-01
    -3.198,2000-02-01
    -3.647,2001-02-01
    -2.02,2002-02-01
    -7.398,2003-02-01
    -3.356,2004-02-01
    -8.506,2005-02-01
    -5.09,2006-02-01
    -1.817,2007-02-01
    -2.206,2008-02-01
    -6.089,2009-02-01
    -5.43,2010-02-01
    -2.327,2011-02-01
    -6.829,2012-02-01
    -6.85,2013-02-01
    -2.385,2014-02-01
    -3.672,2015-02-01
    -2.108,2016-02-01
    -1.934,2017-02-01
    -7.353,2018-02-01
    -1.03,2019-02-01
    -1.433,2020-02-01
    -2.675,2021-02-01
    -2.621,2022-02-01
    -1.731,2023-02-01
    0.294,2024-02-01
    -6.552,1987-03-01
    -3.824,1988-03-01
    0.527,1989-03-01
    0.903,1990-03-01
    0.611,1991-03-01
    -1.327,1992-03-01
    -2.725,1993-03-01
    2.175,1994-03-01
    -3.626,1995-03-01
    -3.929,1996-03-01
    1.293,1997-03-01
    -1.795,1998-03-01
    -0.698,1999-03-01
    -0.537,2000-03-01
    0.439,2001-03-01
    0.567,2002-03-01
    1.007,2003-03-01
    -2.205,2004-03-01
    -2.307,2005-03-01
    -3.633,2006-03-01
    -0.684,2007-03-01
    -2.245,2008-03-01
    -2.051,2009-03-01
    -2.303,2010-03-01
    -0.555,2011-03-01
    2.592,2012-03-01
    -2.656,2013-03-01
    0.866,2014-03-01
    -0.489,2015-03-01
    -1.253,2016-03-01
    1.928,2017-03-01
    -2.235,2018-03-01
    0.07,2019-03-01
    -1.189,2020-03-01
    -1.764,2021-03-01
    -1.408,2022-03-01
    0.522,2023-03-01
    0.739,2024-03-01
    1.915,1987-04-01
    2.235,1988-04-01
    0.551,1990-04-01
    0.169,1991-04-01
    1.019,1992-04-01
    2.75,1993-04-01
    0.767,1994-04-01
    2.509,1995-04-01
    2.636,1996-04-01
    0.759,1997-04-01
    1.335,1998-04-01
    2.306,1999-04-01
    3.462,2000-04-01
    0.543,2001-04-01
    1.73,2002-04-01
    1.622,2003-04-01
    2.211,2004-04-01
    2.195,2005-04-01
    1.954,2006-04-01
    5.871,2007-04-01
    1.379,2008-04-01
    3.005,2009-04-01
    2.942,2010-04-01
    4.908,2011-04-01
    2.29,2012-04-01
    3.043,2013-04-01
    3.957,2014-04-01
    3.182,2015-04-01
    3.429,2016-04-01
    2.766,2017-04-01
    4.73,2018-04-01
    2.816,2019-04-01
    4.079,2020-04-01
    0.259,2021-04-01
    2.111,2022-04-01
    1.78,2023-04-01
    3.319,2024-04-01
    3.87,1987-05-01
    6.951,1988-05-01
    7.062,1990-05-01
    2.971,1991-05-01
    7.876,1993-05-01
    7.061,1994-05-01
    6.427,1995-05-01
    7.039,1996-05-01
    7.011,1997-05-01
    7.152,1998-05-01
    8.147,1999-05-01
    8.37,2000-05-01
    8.561,2001-05-01
    7.496,2002-05-01
    9.072,2003-05-01
    4.792,2004-05-01
    7.726,2005-05-01
    6.633,2006-05-01
    8.178,2007-05-01
    7.494,2008-05-01
    8.535,2009-05-01
    6.185,2010-05-01
    8.073,2011-05-01
    7.68,2012-05-01
    5.308,2013-05-01
    6.434,2014-05-01
    7.971,2015-05-01
    6.529,2016-05-01
    7.913,2017-05-01
    8.216,2018-05-01
    4.23,2019-05-01
    7.624,2020-05-01
    4.555,2021-05-01
    9.365,2022-05-01
    7.139,2023-05-01
    6.962,2024-05-01
    8.682,1987-06-01
    8.527,1988-06-01
    7.708,1989-06-01
    9.252,1990-06-01
    8.864,1991-06-01
    9.33,1992-06-01
    10.526,1993-06-01
    10.523,1994-06-01
    8.567,1995-06-01
    11.201,1996-06-01
    9.673,1997-06-01
    11.006,1998-06-01
    9.731,1999-06-01
    11.931,2000-06-01
    9.5,2001-06-01
    12.511,2002-06-01
    14.666,2003-06-01
    10.228,2004-06-01
    11.234,2005-06-01
    10.696,2006-06-01
    11.059,2007-06-01
    11.367,2008-06-01
    10.192,2009-06-01
    11.288,2010-06-01
    10.595,2011-06-01
    12.052,2012-06-01
    9.997,2013-06-01
    11.265,2014-06-01
    11.774,2015-06-01
    10.646,2016-06-01
    12.786,2017-06-01
    11.627,2018-06-01
    14.504,2019-06-01
    10.485,2020-06-01
    12.828,2021-06-01
    13.5,2022-06-01
    12.055,2023-06-01
    12.04,2024-06-01
    12.181,1987-07-01
    12.651,1988-07-01
    11.714,1989-07-01
    12.077,1990-07-01
    13.051,1991-07-01
    13.031,1992-07-01
    10.896,1993-07-01
    13.858,1994-07-01
    14.175,1995-07-01
    11.36,1996-07-01
    11.052,1997-07-01
    12.833,1998-07-01
    12.509,1999-07-01
    10.338,2000-07-01
    12.567,2001-07-01
    12.748,2002-07-01
    13.686,2003-07-01
    11.71,2004-07-01
    12.223,2005-07-01
    14.425,2006-07-01
    12.51,2007-07-01
    12.095,2008-07-01
    12.694,2009-07-01
    14.406,2010-07-01
    11.403,2011-07-01
    13.081,2012-07-01
    14.052,2013-07-01
    11.934,2014-07-01
    15.633,2015-07-01
    13.345,2016-07-01
    13.04,2017-07-01
    13.454,2018-07-01
    13.75,2019-07-01
    13.196,2020-07-01
    13.066,2021-07-01
    14.742,2022-07-01
    13.545,2023-07-01
    11.493,1987-08-01
    11.905,1988-08-01
    11.689,1990-08-01
    12.898,1991-08-01
    14.484,1992-08-01
    12.364,1993-08-01
    13.541,1994-08-01
    10.845,1995-08-01
    10.833,1996-08-01
    12.173,1997-08-01
    13.092,1998-08-01
    12.331,1999-08-01
    13.09,2000-08-01
    13.551,2001-08-01
    11.681,2002-08-01
    15.51,2003-08-01
    12.235,2004-08-01
    10.654,2005-08-01
    8.826,2006-08-01
    11.234,2007-08-01
    12.7,2008-08-01
    13.666,2009-08-01
    12.081,2010-08-01
    13.585,2011-08-01
    13.791,2012-08-01
    12.981,2013-08-01
    10.889,2014-08-01
    13.626,2015-08-01
    12.437,2016-08-01
    13.732,2017-08-01
    13.545,2018-08-01
    13.561,2019-08-01
    13.381,2020-08-01
    11.654,2021-08-01
    13.316,2022-08-01
    13.599,2023-08-01
    11.03,1987-09-01
    7.987,1988-09-01
    7.022,1990-09-01
    9.911,1991-09-01
    8.616,1992-09-01
    7.201,1993-09-01
    9.106,1994-09-01
    6.351,1995-09-01
    5.462,1996-09-01
    10.371,1997-09-01
    7.662,1998-09-01
    10.035,1999-09-01
    9.148,2000-09-01
    5.753,2001-09-01
    7.025,2002-09-01
    8.063,2003-09-01
    8.629,2004-09-01
    8.778,2005-09-01
    10.443,2006-09-01
    6.664,2007-09-01
    7.297,2008-09-01
    9.431,2009-09-01
    7.465,2010-09-01
    10.964,2011-09-01
    8.996,2012-09-01
    9.21,2013-09-01
    9.248,2014-09-01
    7.811,2015-09-01
    10.441,2016-09-01
    6.573,2017-09-01
    10.538,2018-09-01
    9.527,2019-09-01
    9.641,2020-09-01
    10.17,2021-09-01
    7.839,2022-09-01
    11.601,2023-09-01
    4.136,1987-10-01
    5.583,1988-10-01
    4.324,1989-10-01
    4.995,1990-10-01
    2.134,1991-10-01
    2.166,1992-10-01
    3.565,1993-10-01
    3.437,1994-10-01
    6.858,1995-10-01
    3.502,1996-10-01
    3.741,1997-10-01
    3.58,1998-10-01
    4.781,1999-10-01
    4.885,2000-10-01
    7.241,2001-10-01
    4.206,2002-10-01
    0.866,2003-10-01
    5.681,2004-10-01
    4.84,2005-10-01
    6.472,2006-10-01
    3.817,2007-10-01
    5.141,2008-10-01
    4.022,2009-10-01
    2.507,2010-10-01
    3.905,2011-10-01
    5.084,2012-10-01
    5.871,2013-10-01
    6.159,2014-10-01
    4.318,2015-10-01
    3.596,2016-10-01
    5.733,2017-10-01
    6.222,2018-10-01
    6.044,2019-10-01
    3.181,2020-10-01
    4.087,2021-10-01
    8.085,2022-10-01
    7.876,2023-10-01
    -0.533,1986-11-01
    -0.621,1987-11-01
    -3.028,1988-11-01
    -2.702,1989-11-01
    -2.181,1990-11-01
    -2.303,1991-11-01
    0.618,1992-11-01
    -2.749,1993-11-01
    2.975,1994-11-01
    -1.474,1995-11-01
    -1.001,1996-11-01
    -0.697,1997-11-01
    -3.651,1998-11-01
    -2.666,1999-11-01
    -0.542,2000-11-01
    -1.197,2001-11-01
    0.942,2002-11-01
    0.192,2003-11-01
    -0.464,2004-11-01
    -1.743,2005-11-01
    1.447,2006-11-01
    -2.142,2007-11-01
    -1.138,2008-11-01
    0.747,2009-11-01
    -0.769,2010-11-01
    1.399,2011-11-01
    0.646,2012-11-01
    -0.606,2013-11-01
    3.258,2014-11-01
    2.538,2015-11-01
    -0.501,2016-11-01
    -1.85,2017-11-01
    1.106,2018-11-01
    -0.014,2019-11-01
    1.659,2020-11-01
    0.002,2021-11-01
    0.434,2022-11-01
    -1.162,2023-11-01
    -5.438,1986-12-01
    -2.775,1987-12-01
    -3.338,1988-12-01
    -7.927,1990-12-01
    -5.621,1991-12-01
    -4.433,1992-12-01
    -4.776,1993-12-01
    -2.193,1994-12-01
    -4.72,1995-12-01
    -5.228,1996-12-01
    -4.019,1997-12-01
    -4.549,1998-12-01
    -5.98,1999-12-01
    -2.907,2000-12-01
    -6.907,2001-12-01
    -2.922,2002-12-01
    -3.921,2003-12-01
    -3.905,2004-12-01
    -7.154,2005-12-01
    -1.835,2006-12-01
    -3.997,2007-12-01
    -4.677,2008-12-01
    -6.197,2009-12-01
    -6.99,2010-12-01
    -3.525,2011-12-01
    -6.113,2012-12-01
    -1.745,2013-12-01
    -1.943,2014-12-01
    0.725,2015-12-01
    -0.938,2016-12-01
    -5.305,2017-12-01
    -3.189,2018-12-01
    -2.762,2019-12-01
    -3.645,2020-12-01
    -3.256,2021-12-01
    -2.997,2022-12-01
    -1.946,2023-12-01
    """.strip()
    )
    reader = csv.reader(raw_measurements, delimiter=",")
    indicators = {i.identifier: i.id for i in sample_real_climatic_indicators}
    measurements = []
    for idx, row in enumerate(reader):
        if idx == 0:  # skip the header
            continue
        value, raw_date = row[:2]
        measurements.append(
            observations.ObservationMeasurement(
                value=float(value),
                date=dt.datetime.strptime(raw_date, "%Y-%m-%d"),
                measurement_aggregation_type=static.MeasurementAggregationType.MONTHLY,
                climatic_indicator_id=indicators["tas-absolute-annual"],
                observation_station_id=sample_real_station.id,
            )
        )
    for db_measurement in measurements:
        arpav_db_session.add(db_measurement)
    arpav_db_session.commit()
    for db_measurement in measurements:
        arpav_db_session.refresh(db_measurement)
    return measurements


def _override_get_settings():
    standard_settings = config.get_settings()
    return standard_settings


def _override_get_db_engine(settings=Depends(dependencies.get_settings)):
    yield db.get_engine(settings, use_test_db=True)


def _override_get_db_session(engine=Depends(dependencies.get_db_engine)):
    with sqlmodel.Session(autocommit=False, autoflush=False, bind=engine) as session:
        yield session
