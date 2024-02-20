import argparse
import asyncio
import logging
import os
import shlex
import sys
from pathlib import Path

import dagger

logger = logging.getLogger(__name__)
POSTGIS_IMAGE_VERSION = "postgis/postgis:16-3.4"


def sanitize_docker_image_name(docker_image_name: str) -> str:
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
            "Docker image name's host section cannot contain the '_' character.")
    return f"{host}/{path.lower()}:{tag or 'latest'}"


def get_env_variables() -> dict[str, str | None]:
    return {
        "DEBUG": os.getenv("DEBUG", "0"),
        "PGPASSWORD": os.getenv("PGPASSWORD", "postgres"),
        "POSTGRES_DB_NAME": os.getenv("POSTGRES_DB_NAME", "postgres"),
        "POSTGRES_PORT_5432_TCP_ADDR": os.getenv("POSTGRES_PORT_5432_TCP_ADDR", "postgis"),
        "POSTGRES_USER": os.getenv("POSTGRES_USER", "postgres"),
        "REDIS_HOST": os.getenv("REDIS_HOST", "redis"),
        "SECRET_KEY": os.getenv("SECRET_KEY", "generate it e.g. from https://djecrety.ir/"),
        "SSL_CERTIFICATE": os.getenv("SSL_CERTIFICATE", "/etc/letsencrypt/live/yourdomain/fullchain.pem"),
        "SSL_KEY": os.getenv("SSL_KEY", "/etc/letsencrypt/live/yourdomain/privkey.pem"),
        "THREDDS_AUTH_URL": os.getenv("THREDDS_AUTH_URL", "https://thredds.arpa.veneto.it/thredds/restrictedAccess/dati_accordo"),
        "THREDDS_HOST": os.getenv("THREDDS_HOST", "https://thredds.arpa.veneto.it/thredds/"),
        "THREDDS_PASSWORD": os.getenv("THREDDS_PASSWORD", ""),
        "THREDDS_USER": os.getenv("THREDDS_USER", ""),
    }


async def run_security_scan(built_container: dagger.Container):
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
        .with_exec(
            shlex.split("sh install-trivy.sh -b /usr/local/bin v0.49.1"))
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


async def run_tests(
        client: dagger.Client,
        built_container: dagger.Container,
        env_variables: dict[str, str]
):
    postgis_service = (
        client.container()
        .from_(POSTGIS_IMAGE_VERSION)
        .with_env_variable("PGDATA", "/var/lib/postgresql/data/pgdata")
        .with_env_variable("POSTGRES_DB", env_variables["POSTGRES_DB_NAME"])
        .with_env_variable("POSTGRES_PASSWORD", env_variables["PGPASSWORD"])
        .with_env_variable("POSTGRES_USER", env_variables["POSTGRES_USER"])
        .with_exposed_port(5432)
        .as_service()
    )
    return await (
        built_container.with_service_binding("db", postgis_service)
        .without_entrypoint()
        # .with_mounted_directory("/opt/api/tests", client.host().directory("./tests"))
        .with_env_variable("DEBUG", env_variables["DEBUG"])
        .with_env_variable("POSTGRES_DB_NAME", env_variables["POSTGRES_DB_NAME"])
        .with_env_variable("POSTGRES_USER", env_variables["POSTGRES_USER"])
        .with_env_variable("PGPASSWORD", env_variables["PGPASSWORD"])
        .with_env_variable("POSTGRES_PORT_5432_TCP_ADDR", "db")
        .with_env_variable("REDIS_HOST", env_variables["REDIS_HOST"])
        .with_env_variable("SECRET_KEY", env_variables["SECRET_KEY"])
        .with_env_variable("THREDDS_HOST", env_variables["THREDDS_HOST"])
        .with_env_variable("THREDDS_PASSWORD", env_variables["THREDDS_PASSWORD"])
        .with_env_variable("THREDDS_USER", env_variables["THREDDS_USER"])
        .with_exec(shlex.split("poetry install --with dev"))
        .with_exec(
            shlex.split(
                "poetry run django-admin makemigrations "
                "users "
                "groups "
                "forecastattributes "
                "places "
                "thredds"
            )
        )
        .with_exec(shlex.split("poetry run django-admin migrate"))
        .with_exec(
            shlex.split(
                "poetry run pytest --verbose --cov --reuse-db tests")
        )
    ).stdout()


async def run_pipeline(
        *,
        with_tests: bool,
        with_security_scan: bool,
        publish_docker_image: str | None = None
):
    env_variables = get_env_variables()
    conf = dagger.Config(
        log_output=sys.stderr,
    )
    repo_root = Path(__file__).parents[2]
    async with dagger.Connection(conf) as client:
        src = client.host().directory(str(repo_root))
        built_container = (
            client.container()
            .build(
                context=src,
                dockerfile="docker/Dockerfile"
            )
            .with_label(
                "org.opencontainers.image.source",
                "https://github.com/geobeyond/Arpav-PPCV-backend"
            )
        )
        if with_security_scan:
            await run_security_scan(built_container)
        if with_tests:
            await run_tests(client, built_container, env_variables)
        if publish_docker_image is not None:
            sanitized_name = sanitize_docker_image_name(publish_docker_image)
            await built_container.publish(sanitized_name)

        print("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--with-security-scan",
        action="store_true",
        help=(
            "Run the trivy security scanner on the built container image in order "
            "to find known vulnerabilities of level HIGH and CRITICAL. Exits with "
            "an error if any vulnerabilities are found."
        )
    )
    parser.add_argument(
        "--with-tests",
        action="store_true",
        help=(
            "Run automated tests on the built container and exit with an error if a "
            "test fails."
        )
    )
    parser.add_argument(
        "--publish-docker-image",
        help=(
            "Full URI to an image registry where the built container image should be "
            "published, including the image tag. This assumes that logging in to the "
            "registry has already been made (for example by running the "
            "`docker login` command beforehand)."
            "Example: ghcr.io/geobeyond/arpav-ppcv-backend:latest"
        )
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        run_pipeline(
            with_tests=args.with_tests,
            with_security_scan=args.with_security_scan,
            publish_docker_image=args.publish_docker_image,
        )
    )
