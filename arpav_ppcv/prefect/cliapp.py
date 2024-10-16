import prefect
import typer

from ..config import ArpavPpcvSettings
from .flows import observations as observations_flows

app = typer.Typer()


@app.command()
def start_periodic_tasks(
    ctx: typer.Context,
    refresh_stations: bool = False,
    refresh_monthly_measurements: bool = False,
    refresh_seasonal_measurements: bool = False,
    refresh_yearly_measurements: bool = False,
    refresh_station_variables: bool = False,
):
    """Starts a prefect worker to perform background tasks.

    This starts a prefect worker that periodically performs the following tasks (if
    enabled via the respective flags):

    - refreshing observation stations
    - refreshing observation monthly measurements for known stations
    - refreshing observation seasonal measurements for known stations
    - refreshing observation yearly measurements for known stations
    - refreshing the database views which contain available observation stations for
      each indicator

    """
    settings: ArpavPpcvSettings = ctx.obj["settings"]
    to_serve = []
    if refresh_stations:
        stations_refresher_deployment = (
            observations_flows.refresh_stations.to_deployment(
                name="stations_refresher",
                cron=settings.prefect.observation_stations_refresher_flow_cron_schedule,
            )
        )
        to_serve.append(stations_refresher_deployment)
    if refresh_monthly_measurements:
        monthly_measurement_refresher_deployment = observations_flows.refresh_monthly_measurements.to_deployment(
            name="monthly_measurement_refresher",
            cron=settings.prefect.observation_monthly_measurements_refresher_flow_cron_schedule,
        )
        to_serve.append(monthly_measurement_refresher_deployment)
    if refresh_seasonal_measurements:
        seasonal_measurement_refresher_deployment = observations_flows.refresh_seasonal_measurements.to_deployment(
            name="seasonal_measurement_refresher",
            cron=settings.prefect.observation_seasonal_measurements_refresher_flow_cron_schedule,
        )
        to_serve.append(seasonal_measurement_refresher_deployment)
    if refresh_yearly_measurements:
        yearly_measurement_refresher_deployment = observations_flows.refresh_yearly_measurements.to_deployment(
            name="yearly_measurement_refresher",
            cron=settings.prefect.observation_yearly_measurements_refresher_flow_cron_schedule,
        )
        to_serve.append(yearly_measurement_refresher_deployment)
    if refresh_station_variables:
        station_variables_deployment = (
            observations_flows.refresh_station_variables.to_deployment(
                name="station_variables_refresher",
                cron=settings.prefect.station_variables_refresher_flow_cron_schedule,
            )
        )
        to_serve.append(station_variables_deployment)
    prefect.serve(*to_serve)
