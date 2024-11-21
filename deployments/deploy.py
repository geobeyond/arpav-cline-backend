"""Deployment script

This is used for managing semi-automated deployments of the system.
"""

# NOTE: IN ORDER TO SIMPLIFY DEPLOYMENT, THIS SCRIPT SHALL ONLY USE STUFF FROM THE
# PYTHON STANDARD LIBRARY

import argparse
import dataclasses
import configparser
import json
import logging
import os
import shlex
import shutil
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path
from string import Template
from typing import Protocol
from urllib.error import HTTPError

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class DeploymentConfiguration:
    backend_image: str
    db_image_tag: str
    db_name: str
    db_password: str
    db_user: str
    deployment_files_repo: str
    deployment_root: Path
    discord_notification_urls: list[str]
    frontend_image: str
    martin_conf_path: Path
    martin_env_database_url: str
    martin_image_tag: str
    prefect_db_name: str
    prefect_db_password: str
    prefect_db_user: str
    prefect_server_env_allow_ephemeral_mode: bool
    prefect_server_env_api_database_connection_url: str
    prefect_server_env_api_host: str
    prefect_server_env_api_port: int
    prefect_server_env_api_url: str
    prefect_server_env_cli_prompt: bool
    prefect_server_env_csrf_protection_enabled: bool
    prefect_server_env_debug_mode: bool
    prefect_server_env_home: Path
    prefect_server_env_serve_base: str
    prefect_server_env_ui_api_url: str
    prefect_server_env_ui_url: str
    prefect_server_image_tag: str
    prefect_static_worker_env_api_url: str
    prefect_static_worker_env_db_dsn: str
    prefect_static_worker_env_debug: bool
    prefect_static_worker_env_debug_mode: bool
    reverse_proxy_image_tag: str
    tls_cert_path: Path
    tls_cert_key_path: Path
    tolgee_app_env_server_port: int
    tolgee_app_env_server_spring_datasource_url: str
    tolgee_app_env_spring_datasource_password: str
    tolgee_app_env_spring_datasource_username: str
    tolgee_app_env_tolgee_authentication_create_demo_for_initial_user: bool
    tolgee_app_env_tolgee_authentication_enabled: bool
    tolgee_app_env_tolgee_authentication_initial_password: str
    tolgee_app_env_tolgee_authentication_jwt_secret: str
    tolgee_app_env_tolgee_file_storage_fs_data_path: Path
    tolgee_app_env_tolgee_frontend_url: str
    tolgee_app_env_tolgee_postgres_autostart_enabled: bool
    tolgee_app_env_tolgee_telemetry_enabled: bool
    tolgee_app_image_tag: str
    tolgee_db_name: str
    tolgee_db_password: str
    tolgee_db_user: str
    traefik_conf_path: Path
    webapp_env_admin_user_password: str
    webapp_env_admin_user_username: str
    webapp_env_allow_cors_credentials: bool
    webapp_env_bind_host: str
    webapp_env_bind_port: int
    webapp_env_cors_methods: list[str]
    webapp_env_cors_origins: list[str]
    webapp_env_db_dsn: str
    webapp_env_debug: bool
    webapp_env_num_uvicorn_worker_processes: int
    webapp_env_public_url: str
    webapp_env_session_secret_key: str
    webapp_env_thredds_server_base_url: str
    webapp_env_uvicorn_log_config_file: Path
    compose_project_name: str = "arpav-cline"
    executable_webapp_service_name: str = "arpav-cline-webapp-1"
    git_repo_clone_destination: Path = Path("/tmp/arpav-cline")

    @classmethod
    def from_config_parser(cls, config_parser: configparser.ConfigParser):
        return cls(
            backend_image=config_parser["main"]["backend_image"],
            db_image_tag=config_parser["main"]["db_image_tag"],
            db_name=config_parser["db"]["name"],
            db_password=config_parser["db"]["password"],
            db_user=config_parser["db"]["user"],
            deployment_files_repo=config_parser["main"]["deployment_files_repo"],
            deployment_root=Path(config_parser["main"]["deployment_root"]),
            discord_notification_urls=[
                i.strip()
                for i in config_parser["main"]["discord_notification_urls"].split(",")
            ],
            frontend_image=config_parser["main"]["frontend_image"],
            martin_conf_path=Path(config_parser["martin"]["conf_path"]),
            martin_env_database_url=config_parser["martin"]["env_database_url"],
            martin_image_tag=config_parser["martin"]["image_tag"],
            prefect_db_name=config_parser["prefect_db"]["name"],
            prefect_db_password=config_parser["prefect_db"]["password"],
            prefect_db_user=config_parser["prefect_db"]["user"],
            prefect_server_env_allow_ephemeral_mode=config_parser.getboolean(
                "prefect_server", "env_allow_ephemeral_mode"
            ),
            prefect_server_env_api_database_connection_url=config_parser[
                "prefect_server"
            ]["env_api_database_connection_url"],
            prefect_server_env_api_host=config_parser["prefect_server"]["env_api_host"],
            prefect_server_env_api_port=config_parser.getint(
                "prefect_server", "env_api_port"
            ),
            prefect_server_env_api_url=config_parser["prefect_server"]["env_api_url"],
            prefect_server_env_cli_prompt=config_parser.getboolean(
                "prefect_server", "env_cli_prompt"
            ),
            prefect_server_env_csrf_protection_enabled=config_parser.getboolean(
                "prefect_server", "env_csrf_protection_enabled"
            ),
            prefect_server_env_debug_mode=config_parser.getboolean(
                "prefect_server", "env_debug_mode"
            ),
            prefect_server_env_home=Path(config_parser["prefect_server"]["env_home"]),
            prefect_server_env_serve_base=config_parser["prefect_server"][
                "env_serve_base"
            ],
            prefect_server_env_ui_api_url=config_parser["prefect_server"][
                "env_ui_api_url"
            ],
            prefect_server_env_ui_url=config_parser["prefect_server"]["env_ui_url"],
            prefect_server_image_tag=config_parser["prefect_server"]["image_tag"],
            prefect_static_worker_env_api_url=config_parser["prefect_static_worker"][
                "env_api_url"
            ],
            prefect_static_worker_env_db_dsn=config_parser["prefect_static_worker"][
                "env_db_dsn"
            ],
            prefect_static_worker_env_debug=config_parser.getboolean(
                "prefect_static_worker", "env_debug"
            ),
            prefect_static_worker_env_debug_mode=config_parser.getboolean(
                "prefect_static_worker", "env_debug_mode"
            ),
            reverse_proxy_image_tag=config_parser["reverse_proxy"]["image_tag"],
            tls_cert_path=Path(config_parser["reverse_proxy"]["tls_cert_path"]),
            tls_cert_key_path=Path(config_parser["reverse_proxy"]["tls_cert_key_path"]),
            tolgee_app_env_server_port=config_parser.getint(
                "tolgee_app", "env_server_port"
            ),
            tolgee_app_env_server_spring_datasource_url=config_parser["tolgee_app"][
                "env_server_spring_datasource_url"
            ],
            tolgee_app_env_spring_datasource_password=config_parser["tolgee_app"][
                "env_spring_datasource_password"
            ],
            tolgee_app_env_spring_datasource_username=config_parser["tolgee_app"][
                "env_spring_datasource_username"
            ],
            tolgee_app_env_tolgee_authentication_create_demo_for_initial_user=config_parser.getboolean(
                "tolgee_app", "env_tolgee_authentication_create_demo_for_initial_user"
            ),
            tolgee_app_env_tolgee_authentication_enabled=config_parser.getboolean(
                "tolgee_app", "env_tolgee_authentication_enabled"
            ),
            tolgee_app_env_tolgee_authentication_initial_password=config_parser[
                "tolgee_app"
            ]["env_tolgee_authentication_initial_password"],
            tolgee_app_env_tolgee_authentication_jwt_secret=config_parser["tolgee_app"][
                "env_tolgee_authentication_jwt_secret"
            ],
            tolgee_app_env_tolgee_file_storage_fs_data_path=Path(
                config_parser["tolgee_app"]["env_tolgee_file_storage_fs_path"]
            ),
            tolgee_app_env_tolgee_frontend_url=config_parser["tolgee_app"][
                "env_tolgee_frontend_url"
            ],
            tolgee_app_env_tolgee_postgres_autostart_enabled=config_parser.getboolean(
                "tolgee_app", "env_tolgee_postgres_autostart_enabled"
            ),
            tolgee_app_env_tolgee_telemetry_enabled=config_parser.getboolean(
                "tolgee_app", "env_tolgee_telemetry_enabled"
            ),
            tolgee_app_image_tag=config_parser["tolgee_app"]["image_tag"],
            tolgee_db_name=config_parser["tolgee_db"]["name"],
            tolgee_db_password=config_parser["tolgee_db"]["password"],
            tolgee_db_user=config_parser["tolgee_db"]["user"],
            traefik_conf_path=Path(config_parser["reverse_proxy"]["traefik_conf_path"]),
            webapp_env_admin_user_password=config_parser["webapp"][
                "env_admin_user_password"
            ],
            webapp_env_admin_user_username=config_parser["webapp"][
                "env_admin_user_username"
            ],
            webapp_env_allow_cors_credentials=config_parser.getboolean(
                "webapp", "env_allow_cors_credentials"
            ),
            webapp_env_bind_host=config_parser["webapp"]["env_bind_host"],
            webapp_env_bind_port=config_parser.getint("webapp", "env_bind_port"),
            webapp_env_cors_methods=[
                m.strip()
                for m in config_parser["webapp"]["env_cors_methods"].split(",")
            ],
            webapp_env_cors_origins=[
                o.strip()
                for o in config_parser["webapp"]["env_cors_origins"].split(",")
            ],
            webapp_env_db_dsn=config_parser["webapp"]["env_db_dsn"],
            webapp_env_debug=config_parser.getboolean("webapp", "env_debug"),
            webapp_env_num_uvicorn_worker_processes=config_parser.getint(
                "webapp", "env_num_uvicorn_worker_processes"
            ),
            webapp_env_public_url=config_parser["webapp"]["env_public_url"],
            webapp_env_session_secret_key=config_parser["webapp"][
                "env_session_secret_key"
            ],
            webapp_env_thredds_server_base_url=config_parser["webapp"][
                "env_thredds_server_base_url"
            ],
            webapp_env_uvicorn_log_config_file=Path(
                config_parser["webapp"]["env_uvicorn_log_config_file"]
            ),
        )

    def ensure_paths_exist(self):
        paths_to_test = (
            self.deployment_root,
            self.martin_conf_path,
            self.prefect_server_env_home,
            self.tls_cert_path,
            self.tls_cert_key_path,
            self.tolgee_app_env_tolgee_file_storage_fs_data_path,
            self.traefik_conf_path,
            self.webapp_env_uvicorn_log_config_file,
        )
        for path in paths_to_test:
            if not path.exists():
                raise RuntimeError(
                    f"Could not find referenced configuration file {path!r}"
                )


class DeployStepProtocol(Protocol):
    name: str
    config: DeploymentConfiguration

    def handle(self) -> None:
        ...


@dataclasses.dataclass
class _CloneRepo:
    config: DeploymentConfiguration
    name: str = "clone git repository to a temporary directory"

    def handle(self) -> None:
        print("Cloning repo...")
        if self.config.git_repo_clone_destination.exists():
            shutil.rmtree(self.config.git_repo_clone_destination)
        subprocess.run(
            shlex.split(
                f"git clone {self.config.deployment_files_repo} "
                f"{self.config.git_repo_clone_destination}"
            ),
            check=True,
        )


@dataclasses.dataclass
class _CopyRelevantRepoFiles:
    config: DeploymentConfiguration
    name: str = (
        "Copy files relevant to the deployment from temporary git clone "
        "to target location"
    )

    def handle(self) -> None:
        to_copy_paths = (
            self.config.git_repo_clone_destination / "deployments/deploy.py",
            self.config.git_repo_clone_destination / "docker/compose.yaml",
            self.config.git_repo_clone_destination
            / "docker/compose.production.template.yaml",
        )
        for to_copy_path in to_copy_paths:
            if not to_copy_path.exists():
                raise RuntimeError(f"Could not find expected file {to_copy_path!r}")
            else:
                shutil.copyfile(
                    to_copy_path, self.config.deployment_root / to_copy_path.name
                )


@dataclasses.dataclass
class _CreateDeploymentReadme:
    config: DeploymentConfiguration
    name: str = "Create deployment README file"

    def handle(self) -> None:
        contents = """
            ## Deployment README

            This directory contains the following deployment-related files:

            - compose.yaml - Base docker compose file, to be used together with `compose.production.yaml`
            - compose.production.yaml - Production-specific compose file, to be used together with the base `compose.yaml` file
            - deploy.py - Deployment script, which can be used to trigger a deployment

            Relevant actions that can be taken using the files in this directory:

            -  Stand up/bring down the system - make use of the existing docker compose files, like this

               ```shell
               # stand up the system
               docker compose -f compose.yaml -f compose.production.yaml up --detach --force-recreate

               # bring down the system
               docker compose -f compose.yaml -f compose.production.yaml down
               ```

            - (Re)deploy the system - Call the `deploy.py` python module, like this:

               ```shell
               # get help on how to call the command
               python3 deploy --help

               # redeploy the system
               python3 deploy --configuration-file <path to config file>
               ```
        """.strip()
        target_path = Path(self.config.deployment_root) / "README.md"
        target_path.write_text(contents)


@dataclasses.dataclass
class _RelaunchDeploymentScript:
    config: DeploymentConfiguration
    original_call_args: list[str]
    name: str = "Relaunch the updated deployment script"

    def handle(self) -> None:
        call_args = self.original_call_args[:]
        if (update_flag_index := args.index("--auto-update")) != -1:
            call_args.pop(update_flag_index)
        os.execv(sys.executable, call_args)


@dataclasses.dataclass
class _GenerateComposeFile:
    config: DeploymentConfiguration
    name: str = "generate docker compose file"

    def handle(self) -> None:
        compose_teplate_path = (
            self.config.deployment_root / "compose.production.template.yaml"
        )
        compose_template = Template(compose_teplate_path.read_text())
        rendered = compose_template.substitute(dataclasses.asdict(self.config))
        target_path = Path(
            self.config.deployment_root / "docker/compose.production.yaml"
        )
        target_path.write_text(rendered)
        compose_teplate_path.unlink(missing_ok=True)


@dataclasses.dataclass
class _ComposeCommandExecutor:
    config: DeploymentConfiguration
    environment: dict[str, str] | None = None

    def handle(self) -> None:
        raise NotImplementedError

    def _run_compose_command(self, suffix: str) -> subprocess.CompletedProcess:
        compose_files = [
            self.config.deployment_root / "compose.yaml",
            self.config.deployment_root / "compose.production.yaml",
        ]
        compose_files_fragment = " ".join(f"-f {p}" for p in compose_files)
        return subprocess.run(
            shlex.split(f"docker compose {compose_files_fragment} {suffix}"),
            cwd=self.config.deployment_root,
            env=self.environment or os.environ,
            check=True,
        )


class _StartCompose(_ComposeCommandExecutor):
    name: str = "start docker compose"

    def handle(self) -> None:
        print("Restarting the docker compose stack...")
        self._run_compose_command("up --detach --force-recreate")


class _StopCompose(_ComposeCommandExecutor):
    name: str = "stop docker compose"

    def handle(self) -> None:
        print("Stopping docker compose stack...")
        run_result = self._run_compose_command("down")
        if run_result.returncode == 14:
            logger.info("docker compose stack was not running, no need to stop")
        else:
            run_result.check_returncode()


@dataclasses.dataclass
class _PullImages(_ComposeCommandExecutor):
    name: str = "pull new docker images from their respective container registries"

    def handle(self) -> None:
        self._run_compose_command("pull")


@dataclasses.dataclass
class _CompileTranslations:
    config: DeploymentConfiguration
    name: str = "compile static translations"

    def handle(self) -> None:
        print("Compiling translations...")
        subprocess.run(
            shlex.split(
                f"docker exec {self.config.executable_webapp_service_name} poetry run "
                f"arpav-ppcv translations compile"
            ),
            check=True,
        )


@dataclasses.dataclass
class _RunMigrations:
    config: DeploymentConfiguration
    name: str = "run DB migrations"

    def handle(self) -> None:
        print("Upgrading database...")
        subprocess.run(
            shlex.split(
                f"docker exec {self.config.executable_webapp_service_name} poetry run "
                f"arpav-ppcv db upgrade"
            ),
            check=True,
        )


@dataclasses.dataclass
class _SendDiscordChannelNotification:
    config: DeploymentConfiguration
    content: str
    name: str = "send a notification to a discord channel"

    def handle(self) -> None:
        for webhook_url in self.config.discord_notification_urls:
            request = urllib.request.Request(webhook_url, method="POST")
            request.add_header("Content-Type", "application/json")

            # the discord server blocks the default user-agent sent by urllib, the
            # one sent by httpx works, so we just use that
            request.add_header("User-Agent", "python-httpx/0.27.0")
            try:
                print(f"Sending notification to {webhook_url!r}...")
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


def get_configuration(config_file: Path) -> DeploymentConfiguration:
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return DeploymentConfiguration.from_config_parser(config_parser)


def perform_deployment(
    *,
    configuration: DeploymentConfiguration,
    confirmed: bool = False,
):
    logger.info(f"{configuration=}")
    deployment_steps = [
        _CreateDeploymentReadme(config=configuration),
        _CloneRepo(config=configuration),
        _CopyRelevantRepoFiles(config=configuration),
        _RelaunchDeploymentScript(config=configuration, original_call_args=sys.argv),
        _StopCompose(config=configuration),
        _GenerateComposeFile(config=configuration),
        _PullImages(config=configuration),
        _StartCompose(config=configuration),
        _RunMigrations(config=configuration),
        _CompileTranslations(config=configuration),
    ]
    this_host = socket.gethostname()
    if len(configuration.discord_notification_urls) > 0:
        deployment_steps.append(
            _SendDiscordChannelNotification(
                config=configuration,
                content=(
                    f"A new deployment of ARPAV-Cline to {this_host!r} has finished"
                ),
            )
        )
    if not confirmed:
        print("Performing a dry-run")
    for step in deployment_steps:
        print(f"Running step: {step.name!r}...")
        if confirmed:
            step.handle()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config-file",
        default=f"{Path.home()}/arpav-cline/production-deployment.cfg",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Turn on debug logging level",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help=(
            "Perform the actual deployment. If this is not provided the script runs "
            "in dry-run mode, just showing what steps would be performed"
        ),
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)
    deployment_config = get_configuration(args.config_file)
    deployment_config.ensure_paths_exist()
    try:
        perform_deployment(
            configuration=deployment_config,
            confirmed=args.confirm,
        )
    except RuntimeError as err:
        raise SystemExit(err) from err
