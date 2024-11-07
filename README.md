# Backend - Piattaforma Proiezioni Climatiche per il Nord-Est

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/geobeyond/Arpav-PPCV-backend/ci.yaml)

This work is licensed under a <a rel="license" href="https://creativecommons.org/licenses/by-sa/3.0/it/deed.en">Creative Commons Attribution-ShareAlike 3.0 IT License</a>.
<br/><a rel="license" href="https://creativecommons.org/licenses/by-sa/3.0/it/deed.en"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/3.0/88x31.png" /></a>

Commissioned by & Data credits to <br/>
<a href="https://www.arpa.veneto.it/"><img src="https://github.com/inkode-it/Arpav-PPCV/raw/main/public/img/logo_arpav.png" alt="ARPAV" style="background-color:white;padding:4px"></a>

Current version was designed and developed in Italy by <br/>
<a rel="author" href="mailto:info@geobeyond.it"><img src="https://avatars.githubusercontent.com/u/1163234?s=200&v=4" alt="Geobeyond"></a>

A previous version had originally been developed by [inkode](http://inkode.it)

---

This repository contains source code for the backend components of the ARPAV-PPCV platform.

Its main goal is to serve climate-related data in the form of both historical observations and forecast models.

Briefly, the backend component consists of two main services:

1. A web application that serves an OpenAPI API that is consumed by the frontend.
2. A worker that is used to execute workflows outside the request/response cycle of a webapplication

The backend contains some additional services, which are used to support it and provide additional functionality, namely:

- a vector tile server
- The integration with ARPA's THREDDS server, which is used for tasks related to model data (WMS service, download of
  NetCDF files, data subsetting for time series visualizations)

The main applications are launched by means of custom CLI commands. This CLI additionally provides a multitude of
maintenance commands, such as upgrading the database schema, refreshing historical observations data, etc.

This is implemented in Python, using these main libraries and frameworks:

- FastAPI
- geoalchemy2
- httpx
- pydantic
- shapely
- starlette
- starlette_admin
- sqlalchemy
- uvicorn
- prefect


### Installation

The primary means of installing the various backend components is by using docker compose. Use the `compose.*` files
provided in the `docker` directory.

For example, for development:

```shell
docker compose -f docker/compose.yaml -f compose.dev.yaml up -d
```

Standing up the various components without docker is also possible, check out the compose file for how to do it. The
main web application uses [poetry](https://python-poetry.org/), so installing it is just a matter
of doing `poetry install`.


### Configuration

This application is configured via environment variables. By defaul all settings are prefixed with `ARPAV_PPCV__`, but
this can also be modified if needed. The system recognizes the following environment variables:

- `ARPAV_PPCV__DEBUG` - (bool - `False`) Whether the application runs in debug mode or not. Debug mode outputs more logging
  information and can be slower. Additionally, it may leak sensitive data to the console. Use it only during development
- `ARPAV_PPCV__BIND_HOST` - (str - `"127.0.0.1"`) Which host is allowed to make requests to the web application server.
  When running under docker, be sure to set this to allow all hosts (`*`).
- `ARPAV_PPCV__BIND_PORT` - (int - `5001`) Which port is the web application server accepting requests on.
- `ARPAV_PPCV__PUBLIC_URL` - (str - `"http://localhost:5001"`) The public URL of the web application.
- `ARPAV_PPCV__DB_DSN` - (pydantic.PostgresDsn - `"postgresql://user:password@localhost:5432/arpav_ppcv"`) Connection
  string to be used for accessing the backend database. This application only works with postgresql as the DB server.
- `ARPAV_PPCV__TEST_DB_DSN` - (pydantic.PostgresDsn - `None`) Connection string used to connect to the test database.
  This is only needed for running the tests.
- `ARPAV_PPCV__VERBOSE_DB_LOGS` - (bool - `False`) Whether to output verbose logs related to database-related commands.
  Use this only in development, as it will slow down the system.
- `ARPAV_PPCV__CONTACT__NAME` - (str - `"info@geobeyond.it"`)
- `ARPAV_PPCV__CONTACT__URL` - (str - `"http://geobeyond.it"`)
- `ARPAV_PPCV__CONTACT__EMAIL` - (str - `"info@geobeyond.it"`)
- `ARPAV_PPCV__TEMPLATES_DIR` - (Path - `"webapp/templates"`) Where to store custom templates. This is mainly useful
  for development, so avoid modifying it.
- `ARPAV_PPCV__STATIC_DIR` - (Path - `"webapp/static"`) Where to store static files. This is mainly useful for
  development, so avoid modifying it.
- `ARPAV_PPCV__THREDDS_SERVER__BASE_URL` - (str - `"http://localhost:8080/thredds"`) Base URL of the THREDDS server
- `ARPAV_PPCV__THREDDS_SERVER__WMS_SERVICE_URL_FRAGMENT` - (str - `"wms"`) URL fragment used by the THREDDS server's
  WMS service. This is mainly useful for development, so avoid modifying it.
- `ARPAV_PPCV__THREDDS_SERVER__NETCDF_SUBSET_SERVICE_URL_FRAGMENT` - (str - `"ncss/grid"`) URL fragment used by the
  THREDDS server's NetCDF subset service. This is mainly useful for development, so avoid modifying it.
- `ARPAV_PPCV__THREDDS_SERVER__UNCERTAINTY_VISUALIZATION_SCALE_RANGE` - (tuple[float, float] - `(0, 9)`) - Min, max
  values for the uncertainty pattern used in the WMS uncertainty visualization display.
- `ARPAV_PPCV__MARTIN_TILE_SERVER_BASE_URL` - (str - "http://localhost:3000") Base URL of the Martin vector tile server.
- `ARPAV_PPCV__NEAREST_STATION_RADIUS_METERS` - (int - 10_000) Distance to use when looking for the nearest
  observation station.
- `ARPAV_PPCV__PREFECT__NUM_FLOW_RETRIES` - (int - 5) Number of times a prefect flow will retry when it fails
- `ARPAV_PPCV__PREFECT__FLOW_RETRY_DELAY_SECONDS` - (int - 5) How many seconds should prefect wait after retrying a failed flow
- `ARPAV_PPCV__PREFECT__NUM_TASK_RETRIES` - (int - 5) Number of times a prefect task will retry when it fails
- `ARPAV_PPCV__PREFECT__TASK_RETRY_DELAY_SECONDS` - (int - 5) How many seconds should prefect wait after retrying a failed task
- `ARPAV_PPCV__PREFECT__OBSERVATION_STATIONS_REFRESHER_FLOW_CRON_SCHEDULE` - (str - `"0 1 * * 1"`) Cron schedule for
  running the flow that refreshes observation stations. The default value should be read like this: run once every week,
  at 01:00 on Monday
- `ARPAV_PPCV__PREFECT__OBSERVATION_MONTHLY_MEASUREMENTS_REFRESHER_FLOW_CRON_SCHEDULE` - (str - `"0 2 * * 1"`) Cron
  schedule for running the flow that refreshes monthly measurements. The default value should be read like this: run
  once every week, at 02:00 on Monday
- `ARPAV_PPCV__PREFECT__OBSERVATION_SEASONAL_MEASUREMENTS_REFRESHER_FLOW_CRON_SCHEDULE` - (str - `"0 3 * * 1"`) Cron
  schedule for running the flow that refreshes seasonal measurements. The default value should be read like this: run
  once every week, at 03:00 on Monday
- `ARPAV_PPCV__PREFECT__OBSERVATION_YEARLY_MEASUREMENTS_REFRESHER_FLOW_CRON_SCHEDULE` - (str - `"0 4 * * 1"`) Cron
  schedule for running the flow that refreshes yearly measurements. The default value should be read like this: run
  once every week, at 04:00 on Monday
- `ARPAV_PPCV__V2_API_MOUNT_PREFIX` - (str - "/api/v2") URL prefix of the web application API. Do not modify this unless
  you know what you are doing, as other parts of the system rely on it.
- `ARPAV_PPCV__LOG_CONFIG_FILE` - (Path - `None`) - Path to the config file for the logging of the application.
- `ARPAV_PPCV__SESSION_SECRET_KEY` - (str - `"changeme"`) - Secret key used by starlette sessions. Set this to a big
  random string.
- `ARPAV_PPCV__ADMIN_USER__USERNAME` - (str - `"arpavadmin"`) username of the admin user
- `ARPAV_PPCV__ADMIN_USER__PASSWORD` - (str - `"arpavpassword"`) password of the admin user. Change it to a hard
  to guess string.
- `ARPAV_PPCV__ADMIN_USER__NAME` - (str - `"Admin"`) Name for the admin user. It gets displayed on the admin section.
- `ARPAV_PPCV__ADMIN_USER__AVATAR` - (str - `None`) Optional URL for admin user's avatar image.
- `ARPAV_PPCV__ADMIN_USER__COMPANY_LOGO_URL` - (str - `None`) Optional URL for the admin user's company image
- `ARPAV_PPCV__ADMIN_USER__ROLES` - (list[str] - `["read", "create", "edit", "delete", "action_make_published"]`) User
  roles of the admin user. This is mainly useful for development, so avoid modifying it.
- `ARPAV_PPCV__CORS_ORIGINS` - (list[str] - `[]`) Origins that are allowed to make cross-origin requests.
- `ARPAV_PPCV__CORS_METHODS` - (list[str] - `[]`) Methods allowed for cross-origin requests.
- `ARPAV_PPCV__ALLOW_CORS_CREDENTIALS` - (bool - `False`) Whether to allow credentials on cross-origin requests.


### Operations

##### Accessing the CLI

The CLI is named `arpav-ppcv`. When running under docker compose, it can be used with the following incantation:

```shell
docker exec -ti arpav-ppcv-webapp-1 poetry run arpav-ppcv <sub-command>
```

There are numerous sub-commands and each may accept additional arguments, so please check the help of the sub-command
you want to run, by passing the `--help` flag.

For example, running the web application  server can be achieved with:

```shell
docker exec -ti poetry run arpav-ppcv run-server
```

##### Accessing the web API

When using the development docker compose file(s), the web application server is accessible at:

    http://localhost:8877

The auto-generated API docs are accessible at the `/api/v2/docs` endpoint


##### Using the web admin

When using the development docker compose file(s), the admin section is available at:

    http://localhost:8877/admin


### Deployment

##### Development environment

dev environment is located at individual devs machine(s). In order to get a working dev deployment set up:

- Ensure you have `git` installed
- Clone (or fork+clone) this repo to your local machine
- Ensure you have docker installed
- Run the following command:

    ```shell
    docker compose -f docker/compose.yaml -f docker/compose.dev.yaml up -d
    ```

- The system will eventually be initialized. Now bootstrap the system by running:

    ```shell
    docker exec -ti arpav-ppcv-webapp-1 poetry run arpav-ppcv db upgrade
    docker exec -ti arpav-ppcv-webapp-1 poetry run arpav-ppcv bootstrap municipalities
    docker exec -ti arpav-ppcv-webapp-1 poetry run arpav-ppcv bootstrap observation-variables
    docker exec -ti arpav-ppcv-webapp-1 poetry run arpav-ppcv bootstrap coverage-configuration-parameters
    docker exec -ti arpav-ppcv-webapp-1 poetry run arpav-ppcv bootstrap coverage-configurations
    ```

- If needed, you can download some NetCDF datasets from the remote THREDDS server by running
  the `arpav-ppcv dev import-thredds-datasets` command. Check its help for more detail. As an example:

    ```shell
    # downloads all su30 netcdf datasets in order to use them in the dev environment
    docker exec -ti arpav-ppcv-webapp-1 poetry run arpav-ppcv dev import-thredds-datasets \
        https://thredds.arpa.veneto.it/thredds \
        /home/appuser/data/datasets \
        --name-filter su30
    ```

- The system shall be available at

    ```shell
    http://localhost:8877
    ```

- Since this is a dev deployment, your local source code directory is mounted inside the container and you can modify it
  and have the web application server automatically reload. Look into the contents of the docker compose file(s) in
  order to check which env variables are set and how to further interact with the system


##### Building the docker image locally

Build the docker image by running this command:

```shell
docker build --tag ghcr.io/geobeyond/arpav-ppcv-backend/arpav-ppcv-backend
```

If you want to build an image for the current branch, such as when you added a new third-party dependency as part of
an ongoing task, add the branch name to the build image:

```shell
docker build --tag ghcr.io/geobeyond/arpav-ppcv-backend/arpav-ppcv-backend:$(git branch --show-current)
```

In order to use this custom named image on your local development, set the `CURRENT_GIT_BRANCH` env variable before
launching the docker compose stack, _i.e._:

```shell
export CURRENT_GIT_BRANCH=$(git branch --show-current)
docker compose -f docker/compose.yaml -f docker/compose.dev.yaml up -d
```


##### Staging environment

Deployments to the staging environment are automated and happen whenever a new docker image is published to the
project's container registry. This is governed by a two-stage workflow, orchestrated via github actions:

- When a new change is merged into the `main` branch, a new docker image is built and published to the container
  registry;
- After being published a webhook is triggered, which causes github to send a request to the staging environment,
  notifying it of the availability of this new docker image;
- The staging environment's infrastructure then takes care of downloading the new docker image and restarting its
  own deployment in such a way as to have the system run with the updated code

The strategy described above employs an installation of the [webhook](https://github.com/adnanh/webhook) server,
together with some custom deployment scripts.

Relevant places to look for configuration in the staging environment, in addition to the `${HOME}` directory:

- `/opt/traefik`
- `/etc/system/system/docker.service.d`
- `/etc/system/system/traefik.service`
- `/etc/system/system/webhook.service`


##### Production environment

Deployments to the production environment are automated. They are based on git tags and are governed by a two-stage
workflow, orchestrated via github actions:

- When a new git tag is pushed into the code repository, a new docker image is built and published to the container
  registry;
- After the publication of the docker image in the registry, github sends a request to the production environment,
  notifying it of the availability of this new tagged docker image;
- The production environment's infrastructure then takes care of downloading the new docker image and restarting its
  own deployment in such a way as to have the system run with the updated code.


###### NOTES

- In order for this strategy to work, there are a couple of sensitive details which must be stored on the code
  repository. Access to this information should therefore be controlled
- Since the production deployment is triggered by pushing a new git tag to the repository, this is a privileged action,
and therefore should only be granted to whomever is responsible for managing production deployments.


### Testing

The system has a set of automated tests which run whenever a new PR is submitted and also whenever a change is merged
to the repository's `main` branch. This is triggered by means of a github actions workflow and uses
(dagger)[https://dagger.io/] for the actual testing pipeline. Running the same pipeline locally can be achieved by:

- Ensuring both dagger and poetry are installed locally
- Running the following command:

    ```shell
    dagger run poetry run python tests/ci/main.py \
        --with-formatter \
        --with-linter \
        --with-tests
    ```

Testing uses these main additional libraries/frameworks:

- pytest
- ruff


##### Git pre-commit

In order to ensure a speedier cycle between making a PR and having the changes reviewed and merged, you can
install [pre-commit](https://pre-commit.com/) and enable the configuration provided in this repo. This will ensure that
commits will be suitably formatted and checked and that when they are pushed to the official repo they will be in a
clean state.


### Vulnerability scanning

There is a github actions workflow that runs daily and checks the code for known vulnerabilities. This uses
[trivy](https://aquasecurity.github.io/trivy/v0.38/). The vulnerability scan can also be run locally by using the
command:

```shell
    dagger run poetry run python tests/ci/main.py --with-security-scan
```
