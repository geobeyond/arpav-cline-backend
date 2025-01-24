import logging
import prefect
import typer
import uuid
from prefect.client.orchestration import SyncPrefectClient

from ..config import ArpavPpcvSettings
from .flows import observations as observations_flows
from .static import PrefectTaskTag

logger = logging.getLogger(__name__)
app = typer.Typer()


@app.command()
def start_periodic_tasks(
    ctx: typer.Context,
    refresh_stations: bool = False,
    refresh_measurements: bool = False,
    refresh_station_variables: bool = False,
):
    """Starts a prefect worker to perform background tasks.

    This starts a prefect worker that periodically performs the following tasks (if
    enabled via the respective flags):

    - refreshing observation stations
    - refreshing observation measurements for known stations
    - refreshing the database views which contain available observation stations for
      each indicator

    Additionally, it creates prefect task concurrency limits in order to keep it from
    executing too many concurrent tasks.
    """
    settings: ArpavPpcvSettings = ctx.obj["settings"]
    to_serve = []
    with prefect.get_client(sync_client=True) as client:
        maybe_create_prefect_task_concurrency_limit(
            client,
            PrefectTaskTag.USES_DB,
            settings.prefect.use_db_task_concurrency_limit,
        )
        maybe_create_prefect_task_concurrency_limit(
            client,
            PrefectTaskTag.USES_ARPA_V_REST_API,
            settings.prefect.arpav_rest_api_task_concurrency_limit,
        )
        maybe_create_prefect_task_concurrency_limit(
            client,
            PrefectTaskTag.USES_ARPA_FVG_REST_API,
            settings.prefect.arpafvg_rest_api_task_concurrency_limit,
        )
    if refresh_stations:
        stations_refresher_deployment = (
            observations_flows.refresh_stations.to_deployment(
                name="stations_refresher",
                cron=settings.prefect.observation_stations_refresher_flow_cron_schedule,
            )
        )
        to_serve.append(stations_refresher_deployment)
    if refresh_measurements:
        measurement_refresher_deployment = observations_flows.refresh_measurements.to_deployment(
            name="measurement_refresher",
            cron=settings.prefect.observation_measurements_refresher_flow_cron_schedule,
        )
        to_serve.append(measurement_refresher_deployment)
    if refresh_station_variables:
        station_variables_deployment = (
            observations_flows.refresh_station_variables.to_deployment(
                name="station_variables_refresher",
                cron=settings.prefect.station_variables_refresher_flow_cron_schedule,
            )
        )
        to_serve.append(station_variables_deployment)
    prefect.serve(*to_serve)


def maybe_create_prefect_task_concurrency_limit(
    client: SyncPrefectClient,
    tag: PrefectTaskTag,
    limit_value: int,
) -> uuid.UUID | None:
    existing_limit_tag_names = [
        lim.tag for lim in client.read_concurrency_limits(limit=100, offset=0)
    ]
    logger.info(
        f"existing task concurrency limits: {', '.join(existing_limit_tag_names)}"
    )
    if tag.value not in existing_limit_tag_names:
        limit_id = client.create_concurrency_limit(
            tag=tag.value, concurrency_limit=limit_value
        )
        logger.info(f"Created task concurrency limit {tag.value!r} ({str(limit_id)})")
        result = limit_id
    else:
        logger.info(f"Task concurrency limit {tag.value!r} already exists, skipping...")
        result = None
    return result
