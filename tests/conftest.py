import csv
import datetime as dt
import io
import random

import geojson_pydantic
import pytest
import shapely.io
import shapely.geometry
import sqlmodel
import typer
from fastapi import Depends
from fastapi.testclient import TestClient
from geoalchemy2.shape import from_shape
from typer.testing import CliRunner

from arpav_ppcv import (
    config,
    database,
    main,
)
from arpav_ppcv.schemas import (
    coverages,
    observations,
)
from arpav_ppcv.webapp import dependencies
from arpav_ppcv.webapp.app import create_app_from_settings
from arpav_ppcv.webapp.api_v2.app import create_app as create_v2_app
from arpav_ppcv.bootstrapper.configurationparameters import (
    generate_configuration_parameters as bootstrappable_configuration_parameters,
)
from arpav_ppcv.bootstrapper.coverage_configurations.forecast import (
    tas as tas_forecast_bootstrappable_configurations,
)
from arpav_ppcv.bootstrapper.variables import (
    generate_variable_configurations as bootstrappable_variables,
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
def sample_real_station(arpav_db_session) -> observations.Station:
    db_station = observations.Station(
        code="91",
        altitude_m=1621,
        name="Passo Monte Croce Comelico",
        type_="meteo",
        active_since=dt.date(1986, 10, 30),
        active_until=None,
        geom=from_shape(
            shapely.io.from_geojson(
                geojson_pydantic.Point(
                    type="Point", coordinates=(12.42397152, 46.65215334)
                ).model_dump_json()
            )
        ),
    )
    arpav_db_session.add(db_station)
    arpav_db_session.commit()
    arpav_db_session.refresh(db_station)
    return db_station


@pytest.fixture()
def sample_stations(arpav_db_session) -> list[observations.Station]:
    db_stations = []
    for i in range(50):
        db_stations.append(
            observations.Station(
                code=f"teststation{i}",
                geom=from_shape(
                    shapely.io.from_geojson(
                        geojson_pydantic.Point(
                            type="Point", coordinates=(i, 2 * i)
                        ).model_dump_json()
                    )
                ),
                altitude_m=2,
                name=f"teststation{i}name",
                type_="sometype",
            )
        )
    for db_station in db_stations:
        arpav_db_session.add(db_station)
    arpav_db_session.commit()
    for db_station in db_stations:
        arpav_db_session.refresh(db_station)
    return db_stations


@pytest.fixture()
def sample_variables(arpav_db_session) -> list[observations.Variable]:
    db_variables = []
    for i in range(20):
        db_variables.append(
            observations.Variable(
                name=f"testvariable{i}",
                description=f"Description for test variable {i}",
            )
        )
    for db_variable in db_variables:
        arpav_db_session.add(db_variable)
    arpav_db_session.commit()
    for db_station in db_variables:
        arpav_db_session.refresh(db_station)
    return db_variables


@pytest.fixture()
def sample_real_variables(arpav_db_session) -> list[observations.Variable]:
    created = []
    for var_to_create in bootstrappable_variables():
        created.append(database.create_variable(arpav_db_session, var_to_create))
    return created


@pytest.fixture()
def sample_monthly_measurements(
    arpav_db_session, sample_variables, sample_stations
) -> list[observations.MonthlyMeasurement]:
    db_monthly_measurements = []
    unique_measurement_instances = set()
    while len(unique_measurement_instances) < 200:
        sampled_date = dt.date(random.randrange(1920, 2020), random.randrange(1, 13), 1)
        sampled_station_id = random.choice(sample_stations).id
        sampled_variable_id = random.choice(sample_variables).id
        unique_measurement_instances.add(
            (sampled_date, sampled_station_id, sampled_variable_id)
        )

    for date_, station_id, variable_id in unique_measurement_instances:
        db_monthly_measurements.append(
            observations.MonthlyMeasurement(
                value=random.random() * 20 - 10,
                date=date_,
                station_id=station_id,
                variable_id=variable_id,
            )
        )
    for db_monthly_measurement in db_monthly_measurements:
        arpav_db_session.add(db_monthly_measurement)
    arpav_db_session.commit()
    for db_station in db_monthly_measurements:
        arpav_db_session.refresh(db_station)
    return db_monthly_measurements


@pytest.fixture()
def sample_real_configuration_parameters(arpav_db_session):
    params_to_create = bootstrappable_configuration_parameters()
    created_params = []
    for param_to_create in params_to_create:
        created_param = database.create_configuration_parameter(
            arpav_db_session, param_to_create
        )
        created_params.append(created_param)
    return created_params


@pytest.fixture()
def sample_configuration_parameters(arpav_db_session):
    db_conf_params = []
    for i in range(5):
        allowed_values = []
        for j in range(4):
            allowed_values.append(
                coverages.ConfigurationParameterValue(
                    internal_value=f"fake-param{j}",
                    name=f"fake_parameter_value{j}",
                    description_english=f"Description for fake param value {j}",
                )
            )
        db_conf_params.append(
            coverages.ConfigurationParameter(
                name=f"fake_parameter_{i}",
                description_english=f"Description for fake param {i}",
                allowed_values=allowed_values,
            )
        )
    for db_conf_param in db_conf_params:
        arpav_db_session.add(db_conf_param)
    arpav_db_session.commit()
    for db_conf_param in db_conf_params:
        arpav_db_session.refresh(db_conf_param)
    return db_conf_params


@pytest.fixture()
def sample_coverage_configurations(
    arpav_db_session, sample_configuration_parameters
) -> list[coverages.CoverageConfiguration]:
    db_cov_confs = []
    for i in range(10):
        params_to_use = random.sample(sample_configuration_parameters, k=2)
        param_values_to_use = []
        for param in params_to_use:
            possible_value = coverages.ConfigurationParameterPossibleValue(
                configuration_parameter_value=random.choice(param.allowed_values)
            )
            param_values_to_use.append(possible_value)
        db_cov_confs.append(
            coverages.CoverageConfiguration(
                name=f"coverage_configuration{i}",
                netcdf_main_dataset_name="some-dataset-name",
                thredds_url_pattern=(
                    f"the_thredds-param_"
                    f"{{"
                    f"{random.choice(param_values_to_use).configuration_parameter_value.configuration_parameter.name}"
                    f"}}"
                ),
                palette="fake",
                possible_values=param_values_to_use,
            )
        )
    for db_cov_conf in db_cov_confs:
        arpav_db_session.add(db_cov_conf)
    arpav_db_session.commit()
    for db_cov_conf in db_cov_confs:
        arpav_db_session.refresh(db_cov_conf)
    return db_cov_confs


@pytest.fixture()
def sample_real_coverage_configurations(
    arpav_db_session,
    sample_real_configuration_parameters,
    sample_real_variables,
):
    all_vars = database.collect_all_variables(arpav_db_session)
    all_conf_param_values = database.collect_all_configuration_parameter_values(
        arpav_db_session
    )
    cov_confs_to_create = (
        tas_forecast_bootstrappable_configurations.generate_configurations(
            conf_param_values={
                (pv.configuration_parameter.name, pv.name): pv
                for pv in all_conf_param_values
            },
            variables={v.name: v for v in all_vars},
        )
    )
    created_cov_confs = {}
    for cov_conf_to_create in cov_confs_to_create:
        cov_conf = database.create_coverage_configuration(
            arpav_db_session, cov_conf_to_create
        )
        created_cov_confs[cov_conf.name] = cov_conf

    to_update = {}
    for name, related_names in {
        **tas_forecast_bootstrappable_configurations.get_related_map(),
    }.items():
        to_update[name] = {
            "related": related_names,
        }

    for name, uncertainties in {
        **tas_forecast_bootstrappable_configurations.get_uncertainty_map(),
    }.items():
        info = to_update.setdefault(name, {})
        info["uncertainties"] = uncertainties
    for name, info in to_update.items():
        main_cov_conf = created_cov_confs[name]
        secondaries = info.get("related")
        uncertainties = info.get("uncertainties")
        update_kwargs = {}
        if secondaries is not None:
            secondary_cov_confs = [
                cc for name, cc in created_cov_confs.items() if name in secondaries
            ]
            update_kwargs["secondary_coverage_configurations_ids"] = [
                cc.id for cc in secondary_cov_confs
            ]
        else:
            update_kwargs["secondary_coverage_configurations_ids"] = []
        if uncertainties is not None:
            lower_uncert_id = [
                cc.id
                for name, cc in created_cov_confs.items()
                if name == uncertainties[0]
            ][0]
            upper_uncert_id = [
                cc.id
                for name, cc in created_cov_confs.items()
                if name == uncertainties[1]
            ][0]
            update_kwargs.update(
                uncertainty_lower_bounds_coverage_configuration_id=lower_uncert_id,
                uncertainty_upper_bounds_coverage_configuration_id=upper_uncert_id,
            )
        cov_update = coverages.CoverageConfigurationUpdate(
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
                coverages.ConfigurationParameterPossibleValueUpdate(
                    configuration_parameter_value_id=pv.configuration_parameter_value_id
                )
                for pv in main_cov_conf.possible_values
            ],
        )
        database.update_coverage_configuration(
            arpav_db_session,
            main_cov_conf,
            cov_update,
        )


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
def sample_real_monthly_measurements(
    arpav_db_session,
    sample_real_variables,
    sample_real_station,
) -> observations.MonthlyMeasurement:
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
    vars = {v.name: v for v in sample_real_variables}
    measurements = []
    for idx, row in enumerate(reader):
        if idx == 0:  # skip the header
            continue
        value, raw_date = row[:2]
        measurements.append(
            observations.MonthlyMeasurement(
                station_id=sample_real_station.id,
                variable_id=vars["TDd"].id,
                value=float(value),
                date=dt.datetime.strptime(raw_date, "%Y-%m-%d"),
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
    yield database.get_engine(settings, use_test_db=True)


def _override_get_db_session(engine=Depends(dependencies.get_db_engine)):
    with sqlmodel.Session(autocommit=False, autoflush=False, bind=engine) as session:
        yield session
