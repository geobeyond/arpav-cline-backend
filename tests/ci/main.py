import asyncio
import logging
import shlex
import sys
from pathlib import Path
from typing import Annotated

import dagger
import typer

logger = logging.getLogger(__name__)
POSTGIS_IMAGE_VERSION = "postgis/postgis:16-3.4"
REPO_ROOT = Path(__file__).parents[2]

cli_app = typer.Typer()


@cli_app.command()
def run_ci_pipeline(
    with_tests: Annotated[
        bool,
        typer.Option(
            help=(
                "Run automated tests on the built container and exit with an "
                "error if a test fails."
            )
        ),
    ] = False,
    with_load_tests: Annotated[bool, typer.Option(help="Run load tests")] = False,
    with_security_scan: Annotated[
        bool,
        typer.Option(
            help=(
                "Full URI to an image registry where the built container image should be "
                "published, including the image tag. This assumes that logging in to the "
                "registry has already been made (for example by running the "
                "`docker login` command beforehand)."
                "Example: ghcr.io/geobeyond/arpav-ppcv-backend:latest"
            )
        ),
    ] = False,
    with_linter: Annotated[
        bool,
        typer.Option(
            help=(
                "Apply linting to the code and exit with an error if there are static "
                "analysis issues."
            )
        ),
    ] = False,
    with_formatter: Annotated[
        bool,
        typer.Option(
            help=(
                "Check the code for formatting issues and exit with an error if "
                "found."
            )
        ),
    ] = False,
    publish_docker_image: str | None = None,
    git_commit: Annotated[
        str, typer.Option(help=("Hash of the current version's git commit"))
    ] = None,
):
    """Command-line interface for running CI pipeline."""

    logging.basicConfig(level=logging.INFO)
    return asyncio.run(
        _run_pipeline(
            with_tests=with_tests,
            with_load_tests=with_load_tests,
            with_security_scan=with_security_scan,
            with_linter=with_linter,
            with_formatter=with_formatter,
            publish_docker_image=publish_docker_image,
            git_commit=git_commit,
        )
    )


def _sanitize_docker_image_name(docker_image_name: str) -> str:
    """Ensure input docker_image_name is valid.

    This function sanitizes the input according to the rules described in
    the docker docs at:

    https://docs.docker.com/engine/reference/commandline/image_tag/#extended-description

    Most notably, this will ensure the path portion of the image name is
    lowercase, which may sometimes not be the case for images being pushed to
    the github container registry.
    """
    host, rest = docker_image_name.partition("/")[::2]
    path, tag = rest.partition(":")[::2]
    if "_" in host:
        logger.warning(
            "Docker image name's host section cannot contain the '_' character."
        )
    return f"{host}/{path.lower()}:{tag or 'latest'}"


async def _run_linter(built_container: dagger.Container):
    return await (
        built_container.with_user("appuser")
        .without_entrypoint()
        .with_exec(shlex.split("poetry install --with dev"))
        .with_exec(shlex.split("poetry run ruff check ."))
    )


async def _run_formatter(built_container: dagger.Container):
    return await (
        built_container.with_user("appuser")
        .without_entrypoint()
        .with_exec(shlex.split("poetry install --with dev"))
        .with_exec(shlex.split("poetry run ruff format --check ."))
    )


async def _run_security_scan(built_container: dagger.Container):
    return await (
        built_container.with_user("root")
        .without_entrypoint()
        .with_exec(shlex.split("apt-get update"))
        .with_exec(shlex.split("apt-get install --yes curl tar"))
        .with_exec(
            shlex.split(
                "curl --silent --fail "
                "--location https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh "
                "--output install-trivy.sh"
            )
        )
        .with_exec(shlex.split("sh install-trivy.sh -b /usr/local/bin v0.49.1"))
        .with_exec(
            shlex.split(
                "trivy rootfs "
                "--ignore-unfixed "
                "--severity HIGH,CRITICAL "
                "--exit-code 1 "
                "/"
            )
        )
    ).stdout()


async def _run_tests(
    client: dagger.Client,
    built_container: dagger.Container,
    env_variables: dict[str, str],
):
    db_params = _get_db_parameters(env_variables["ARPAV_PPCV__TEST_DB_DSN"])
    arpav_db_service = _get_arpav_db_service(
        client,
        db_params["db"],
        db_params["user"],
        db_params["password"],
        db_params["port"],
    )
    test_container = built_container.with_service_binding(
        db_params["host"], arpav_db_service
    ).without_entrypoint()
    for var_name, var_value in env_variables.items():
        test_container = test_container.with_env_variable(var_name, var_value)
    return await (
        test_container.with_exec(shlex.split("poetry install --with dev"))
        .with_exec(shlex.split("poetry run arpav-ppcv translations compile"))
        .with_exec(shlex.split("poetry run pytest "))
    ).stdout()


def _get_arpav_db_service(
    client: dagger.Client,
    db_name: str,
    db_user: str,
    db_password: str,
    db_port: str | int,
) -> dagger.Service:
    return (
        client.container()
        .from_(POSTGIS_IMAGE_VERSION)
        .with_env_variable("PGDATA", "/var/lib/postgresql/data/pgdata")
        .with_env_variable("POSTGRES_DB", db_name)
        .with_env_variable("POSTGRES_PASSWORD", db_password)
        .with_env_variable("POSTGRES_USER", db_user)
        .with_exposed_port(int(db_port))
        .as_service()
    )


async def _run_load_tests(
    client: dagger.Client,
    test_container: dagger.Container,
    num_users: int = 20,
    spawn_rate_users_second: int = 5,
    run_time_seconds: int = 60,
):
    # "ARPAV_PPCV__DB_DSN": "postgresql://arpav:arpavpassword@db:5432/arpav_ppcv",
    db_user = "arpav"
    db_password = "arpavpassword"
    db_host = "db"
    db_port = 5432
    db_name = "arpav_ppcv"
    db_service = _get_arpav_db_service(client, db_name, db_user, db_password, db_port)
    db_dsn = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # modifications made to the test container:
    # - add a proper ARPAV_PPCV__DB_DSN env var, because we are simulating the live
    #   system
    webap_service = (
        test_container.without_entrypoint()
        .with_env_variable("ARPAV_PPCV__DB_DSN", db_dsn)
        .with_service_binding(db_host, db_service)
        .with_exec(shlex.split("poetry run arpav-ppcv db upgrade"))
        .with_exec(shlex.split("poetry run arpav-ppcv bootstrap observation-variables"))
        .with_exec(
            shlex.split(
                "poetry run arpav-ppcv bootstrap coverage-configuration-parameters"
            )
        )
        .with_exec(
            shlex.split("poetry run arpav-ppcv bootstrap coverage-configurations")
        )
        .with_exec(shlex.split("poetry run arpav-ppcv translations compile"))
        .with_exec(shlex.split("poetry run arpav-ppcv run-server"))
        .with_exposed_port(5001)
        .as_service()
    )
    webapp_service_alias = "webapp"
    locust_dir_mount_path = "/mnt/locust"
    locust_container = (
        client.container()
        .from_("locustio/locust")
        .with_mounted_directory(
            locust_dir_mount_path,
            client.host().directory(str(REPO_ROOT / "tests/loadtests")),
        )
        # .with_service_binding(db_host, db_service)
        .with_service_binding(webapp_service_alias, webap_service)
    )
    return await (
        locust_container.with_exec(
            shlex.split(
                f"--headless --users {num_users} "
                f"--spawn-rate {spawn_rate_users_second} "
                f"--host http://{webapp_service_alias}:5001 "
                f"--locustfile {locust_dir_mount_path}/locustfile.py "
                f"--run-time {run_time_seconds}s "
                f"--stop-timeout 10s"
            )
        )
    ).stdout()


async def _run_pipeline(
    *,
    with_tests: bool,
    with_load_tests: bool,
    with_security_scan: bool,
    with_linter: bool,
    with_formatter: bool,
    publish_docker_image: str | None,
    git_commit: str | None,
):
    # env_variables = _get_env_variables()
    env_variables = {
        "ARPAV_PPCV__BIND_HOST": "0.0.0.0",
        "ARPAV_PPCV__BIND_PORT": "5001",
        "ARPAV_PPCV__PUBLIC_URL": "http://localhost:5001",
        # "ARPAV_PPCV__DB_DSN": "postgresql://arpav:arpavpassword@db:5432/arpav_ppcv",
        "ARPAV_PPCV__TEST_DB_DSN": "postgresql://arpavtest:arpavtestpassword@test-db:5432/arpav_ppcv_test",
        "ARPAV_PPCV__LOG_CONFIG_FILE": "/home/appuser/app/dev-log-config.yml",
    }

    conf = dagger.Config(
        log_output=sys.stderr,
    )
    build_args = []
    if git_commit is not None:
        build_args.append(dagger.BuildArg(name="GIT_COMMIT", value=git_commit))
    async with dagger.Connection(conf) as client:
        src = client.host().directory(str(REPO_ROOT))
        built_container = (
            client.container()
            .build(context=src, dockerfile="docker/Dockerfile", build_args=build_args)
            .with_label(
                "org.opencontainers.image.source",
                "https://github.com/geobeyond/Arpav-PPCV-backend",
            )
        )
        if with_formatter:
            await _run_formatter(built_container)
        if with_linter:
            await _run_linter(built_container)
        if with_security_scan:
            await _run_security_scan(built_container)
        if with_tests or with_load_tests:
            test_container = built_container
            for var_name, var_value in env_variables.items():
                test_container = test_container.with_env_variable(var_name, var_value)
            if with_tests:
                await _run_tests(client, built_container, env_variables)
            if with_load_tests:
                await _run_load_tests(
                    client,
                    test_container,
                )
        if publish_docker_image is not None:
            sanitized_name = _sanitize_docker_image_name(publish_docker_image)
            await built_container.publish(sanitized_name)
        print("Done")


def _get_db_parameters(db_connection_string: str) -> dict[str, str]:
    db_parts = db_connection_string.split("://")[-1]
    other_parts, db_name = db_parts.rpartition("/")[::2]
    user_details, host_details = other_parts.split("@")
    username, password = user_details.split(":")
    host, port = host_details.split(":")
    return {
        "db": db_name,
        "user": username,
        "password": password,
        "host": host,
        "port": port,
    }


if __name__ == "__main__":
    cli_app()
