# ARPAV-PPCV deployment script
#
# This script is to be run by the `webhook` server whenever there
# is a push to the arpav-ppcv-backend repository.
#
# NOTE: IN ORDER TO SIMPLIFY DEPLOYMENT, THIS SCRIPT SHALL ONLY USE STUFF FROM THE
# PYTHON STANDARD LIBRARY

import argparse
import dataclasses
import hashlib
import json
import logging
import os
import shlex
import shutil
import socket
import urllib.request
from pathlib import Path
from subprocess import run
import sys
from typing import (
    Optional,
    Protocol,
    Sequence,
)
from urllib.error import HTTPError

logger = logging.getLogger(__name__)


class DeployStepProtocol(Protocol):
    name: str

    def handle(self) -> None:
        ...


@dataclasses.dataclass
class _ValidateRequestPayload:
    raw_payload: str
    valid_repositories: Sequence[str]
    name: str = "validate request payload"

    def handle(self) -> bool:
        try:
            payload = json.loads(self.raw_payload)
        except json.JSONDecodeError as err:
            raise RuntimeError("Could not decode payload as valid JSON") from err
        else:
            return all(
                (
                    payload.get("event") == "push",
                    payload.get("ref") == "refs/heads/main",
                    payload.get("repository", "").lower() in self.valid_repositories,
                )
            )


@dataclasses.dataclass
class _FindDockerDir:
    docker_dir: Path
    name: str = "confirm docker dir exists"

    def handle(self) -> None:
        if not self.docker_dir.exists():
            raise RuntimeError(f"Docker dir {str(self.docker_dir)!r} does not exist")


@dataclasses.dataclass
class _StopCompose:
    docker_dir: Path
    compose_files_fragment: str
    name: str = "stop docker compose"

    def handle(self) -> None:
        print("Stopping docker compose stack...")
        run_result = run(
            shlex.split(f"docker compose {self.compose_files_fragment} down"),
        )
        if run_result.returncode == 14:
            logger.info("docker compose stack was not running, no need to stop")
        else:
            run_result.check_returncode()


@dataclasses.dataclass
class _CloneRepo:
    clone_destination: Path
    repo_url: str
    name: str = "clone git repository"

    def handle(self) -> None:
        print("Cloning repo...")
        if self.clone_destination.exists():
            shutil.rmtree(self.clone_destination)
        run(
            shlex.split(f"git clone {self.repo_url} {self.clone_destination}"),
            check=True,
        )


@dataclasses.dataclass
class _SelfUpdate:
    repo_dir: Path
    original_call_args: list[str]
    name: str = "Update the deployment script"

    def handle(self) -> None:
        print("Updating the deployment script...")
        current_deployment_script_path = Path(__file__)
        digest_algorithm = hashlib.sha256

        current_contents = current_deployment_script_path.read_bytes()
        current_contents_hash = digest_algorithm(current_contents).hexdigest()

        new_deployment_script_path = (
            self.repo_dir / "deployments/staging/hook-scripts/deploy.py"
        )

        new_contents = new_deployment_script_path.read_bytes()
        new_contents_hash = digest_algorithm(new_contents).hexdigest()
        if current_contents_hash != new_contents_hash:
            logger.debug("Deployment script changed, updating and relaunching...")
            current_deployment_script_path.write_bytes(
                new_deployment_script_path.read_bytes()
            )
            call_args = self.original_call_args[:]
            if (update_flag_index := args.index("--auto-update")) != -1:
                call_args.pop(update_flag_index)
            os.execv(sys.executable, call_args)
        else:
            logger.debug("Deployment script did not change, skipping...")


@dataclasses.dataclass
class _ReplaceDockerDir:
    docker_dir: Path
    repo_dir: Path
    name: str = "copy docker directory"

    def handle(self) -> None:
        # copy the `docker` directory and delete the rest - we are deploying docker
        # images, so no need for the source code
        repo_docker_dir = self.repo_dir / "docker"
        print(
            f"Copying the docker dir in {repo_docker_dir!r} "
            f"to {self.docker_dir!r}..."
        )
        shutil.rmtree(self.docker_dir, ignore_errors=True)
        shutil.copytree(repo_docker_dir, self.docker_dir)
        shutil.rmtree(str(repo_docker_dir), ignore_errors=True)


@dataclasses.dataclass
class _FindEnvFiles:
    env_files: dict[str, Path]
    name: str = "find environment file"

    def handle(self) -> None:
        print("Looking for env_file...")
        for env_file_path in self.env_files.values():
            if not env_file_path.exists():
                raise RuntimeError(
                    f"Could not find environment file {env_file_path!r}, aborting..."
                )


@dataclasses.dataclass
class _PullImages:
    images: Sequence[str]
    name: str = "pull new docker images from container registry"

    def handle(self) -> None:
        print("Pulling updated docker images...")
        for image in self.images:
            run(shlex.split(f"docker pull {image}"), check=True)


@dataclasses.dataclass
class _StartCompose:
    env_file_db_service: Path
    env_file_webapp_service: Path
    env_file_frontend_service: Path
    env_file_martin_service: Path
    env_file_prefect_db_service: Path
    env_file_prefect_server_service: Path
    env_file_prefect_static_worker_service: Path
    compose_files_fragment: str
    working_dir: Path
    name: str = "start docker compose"

    def handle(self) -> None:
        print("Restarting the docker compose stack...")
        run(
            shlex.split(
                f"docker compose {self.compose_files_fragment} up --detach "
                f"--force-recreate"
            ),
            cwd=self.working_dir,
            env={
                **os.environ,
                "ARPAV_PPCV_DEPLOYMENT_ENV_FILE_DB_SERVICE": self.env_file_db_service,
                "ARPAV_PPCV_DEPLOYMENT_ENV_FILE_WEBAPP_SERVICE": self.env_file_webapp_service,  # noqa
                "ARPAV_PPCV_DEPLOYMENT_ENV_FILE_FRONTEND_SERVICE": self.env_file_frontend_service,  # noqa
                "ARPAV_PPCV_DEPLOYMENT_ENV_FILE_MARTIN_SERVICE": self.env_file_martin_service,  # noqa
                "ARPAV_PPCV_DEPLOYMENT_ENV_FILE_PREFECT_DB_SERVICE": self.env_file_prefect_db_service,  # noqa
                "ARPAV_PPCV_DEPLOYMENT_ENV_FILE_PREFECT_SERVER_SERVICE": self.env_file_prefect_server_service,  # noqa
                "ARPAV_PPCV_DEPLOYMENT_ENV_FILE_PREFECT_STATIC_WORKER_SERVICE": self.env_file_prefect_static_worker_service,  # noqa
            },
            check=True,
        )


@dataclasses.dataclass
class _CompileTranslations:
    webapp_service_name: str
    name: str = "compile static translations"

    def handle(self) -> None:
        print("Compiling translations...")
        run(
            shlex.split(
                f"docker exec {self.webapp_service_name} poetry run "
                f"arpav-ppcv translations compile"
            ),
            check=True,
        )


@dataclasses.dataclass
class _RunMigrations:
    webapp_service_name: str
    name: str = "run DB migrations"

    def handle(self) -> None:
        print("Upgrading database...")
        run(
            shlex.split(
                f"docker exec {self.webapp_service_name} poetry run "
                f"arpav-ppcv db upgrade"
            ),
            check=True,
        )


@dataclasses.dataclass
class _SendDiscordChannelNotification:
    webhook_url: str
    content: str
    name: str = "send a notification to a discord channel"

    def handle(self) -> None:
        print("Sending discord channel notification...")
        request = urllib.request.Request(self.webhook_url, method="POST")
        request.add_header("Content-Type", "application/json")

        # the discord server blocks the default user-agent sent by urllib, the
        # one sent by httpx works, so we just use that
        request.add_header("User-Agent", "python-httpx/0.27.0")
        try:
            with urllib.request.urlopen(
                request, data=json.dumps({"content": self.content}).encode("utf-8")
            ) as response:
                if 200 <= response.status <= 299:
                    print("notification sent")
                else:
                    print(
                        f"notification response was not successful: {response.status}"
                    )
        except HTTPError:
            print("sending notification failed")


def perform_deployment(
    *,
    raw_request_payload: str,
    deployment_root: Path,
    discord_webhook_url: Optional[str] = None,
    confirmed: bool = False,
    auto_update: bool = False,
):
    if not confirmed:
        print("Performing a dry-run")
    logger.info(f"{deployment_root=}")
    docker_dir = deployment_root / "docker"
    compose_files = (
        f"-f {docker_dir}/compose.yaml " f"-f {docker_dir}/compose.staging.yaml"
    )
    clone_destination = Path("/tmp/arpav-ppcv-backend")
    deployment_env_files = {
        "db_service": deployment_root / "environment-files/db-service.env",
        "webapp_service": deployment_root / "environment-files/webapp-service.env",
        "frontend_service": deployment_root / "environment-files/frontend-service.env",
        "martin_service": deployment_root / "environment-files/martin-service.env",
        "prefect_db_service": deployment_root
        / "environment-files/prefect-db-service.env",
        "prefect_server_service": deployment_root
        / "environment-files/prefect-server-service.env",
        "prefect_static_worker_service": deployment_root
        / "environment-files/prefect-static-worker-service.env",
    }
    webapp_service_name = "arpav-ppcv-staging-webapp-1"
    deployment_steps = [
        _ValidateRequestPayload(
            raw_payload=raw_request_payload,
            valid_repositories=(
                "geobeyond/arpav-ppcv",
                "geobeyond/arpav-ppcv-backend",
            ),
        ),
        _FindEnvFiles(env_files=deployment_env_files),
        _CloneRepo(
            clone_destination=clone_destination,
            repo_url="https://github.com/geobeyond/Arpav-PPCV-backend.git ",
        ),
    ]
    if auto_update:
        deployment_steps.append(
            _SelfUpdate(repo_dir=clone_destination, original_call_args=sys.argv),
        )
    deployment_steps.extend(
        [
            _FindDockerDir(docker_dir=docker_dir),
            _StopCompose(docker_dir=docker_dir, compose_files_fragment=compose_files),
            _ReplaceDockerDir(repo_dir=clone_destination, docker_dir=docker_dir),
            _PullImages(
                images=(
                    "ghcr.io/geobeyond/arpav-ppcv-backend/arpav-ppcv-backend",
                    "ghcr.io/geobeyond/arpav-ppcv/arpav-ppcv",
                )
            ),
            _StartCompose(
                env_file_db_service=deployment_env_files["db_service"],
                env_file_webapp_service=deployment_env_files["webapp_service"],
                env_file_frontend_service=deployment_env_files["frontend_service"],
                env_file_martin_service=deployment_env_files["martin_service"],
                env_file_prefect_db_service=deployment_env_files["prefect_db_service"],
                env_file_prefect_server_service=deployment_env_files[
                    "prefect_server_service"
                ],
                env_file_prefect_static_worker_service=deployment_env_files[
                    "prefect_static_worker_service"
                ],
                compose_files_fragment=compose_files,
                working_dir=deployment_root,
            ),
            _RunMigrations(webapp_service_name=webapp_service_name),
            _CompileTranslations(webapp_service_name=webapp_service_name),
        ]
    )
    if discord_webhook_url is not None:
        deployment_steps.append(
            _SendDiscordChannelNotification(
                webhook_url=discord_webhook_url,
                content=(
                    f"A new deployment of ARPAV-PPCV to "
                    f"{socket.gethostname()!r} has finished"
                ),
            )
        )
    for step in deployment_steps:
        print(f"Running step: {step.name!r}...")
        if confirmed:
            step.handle()


if __name__ == "__main__":
    discord_notification_env_var_name = (
        "ARPAV_PPCV_DEPLOYMENT_STATUS_DISCORD_WEBHOOK_URL"
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "deployment_root", help="Root directory of the deployment", type=Path
    )
    parser.add_argument("payload", help="Trigger request's body payload")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help=(
            "Perform the actual deployment. If this is not provided the script runs "
            "in dry-run mode, just showing what steps would be performed"
        ),
    )
    parser.add_argument(
        "--auto-update",
        action="store_true",
        help=(
            "Auto-update this deployment script with the current version from the "
            "repo and then relaunch"
        ),
    )
    parser.add_argument(
        "--send-discord-notification",
        action="store_true",
        help=(
            f"Send a notification to the discord channel. This only works if "
            f"the {discord_notification_env_var_name} environment variable is set"
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Turn on debug logging level",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)
    webhook_url = None
    if (notification_url := os.getenv(discord_notification_env_var_name)) is not None:
        if args.send_discord_notification:
            webhook_url = notification_url
    else:
        if args.send_discord_notification:
            logger.warning(
                f"Not sending discord notification because "
                f"{discord_notification_env_var_name} is not set"
            )
    try:
        perform_deployment(
            raw_request_payload=args.payload,
            deployment_root=args.deployment_root,
            discord_webhook_url=webhook_url,
            confirmed=args.confirm,
            auto_update=args.auto_update,
        )
    except RuntimeError as err:
        raise SystemExit(err) from err
