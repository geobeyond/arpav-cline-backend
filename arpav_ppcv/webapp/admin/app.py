import logging

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException
from starlette_admin.contrib.sqlmodel import Admin
from starlette_admin.views import (
    DropDown,
    Link,
)

from ... import (
    config,
    database,
)
from ...schemas import (
    base,
    climaticindicators,
    coverages,
    observations,
)
from . import auth
from .middlewares import SqlModelDbSessionMiddleware
from .views import (
    base as base_views,
    climaticindicators as climaticindicators_views,
    coverages as coverage_views,
    observations as observations_views,
)

logger = logging.getLogger(__name__)


class ArpavPpcvAdmin(Admin):
    def mount_to(self, app: Starlette, settings: config.ArpavPpcvSettings) -> None:
        """Reimplemented in order to pass settings to the admin app."""
        admin_app = Starlette(
            routes=self.routes,
            middleware=self.middlewares,
            debug=self.debug,
            exception_handlers={HTTPException: self._render_error},
        )
        admin_app.state.ROUTE_NAME = self.route_name
        admin_app.state.settings = settings
        app.mount(
            self.base_url,
            app=admin_app,
            name=self.route_name,
        )


def create_admin(settings: config.ArpavPpcvSettings) -> ArpavPpcvAdmin:
    engine = database.get_engine(settings)
    admin = ArpavPpcvAdmin(
        engine,
        debug=settings.debug,
        templates_dir=str(settings.templates_dir / "admin"),
        auth_provider=auth.UsernameAndPasswordProvider(),
        middlewares=[
            Middleware(SessionMiddleware, secret_key=settings.session_secret_key),
            Middleware(SqlModelDbSessionMiddleware, engine=engine),
        ],
    )
    admin.add_view(
        climaticindicators_views.ClimaticIndicatorView(
            climaticindicators.ClimaticIndicator
        )
    )
    admin.add_view(base_views.SpatialRegionView(base.SpatialRegion))
    admin.add_view(coverage_views.ForecastModelView(coverages.ForecastModel))
    admin.add_view(coverage_views.ForecastTimeWindowView(coverages.ForecastTimeWindow))
    admin.add_view(
        coverage_views.ForecastCoverageConfigurationView(
            coverages.ForecastCoverageConfiguration
        )
    )
    admin.add_view(
        observations_views.ObservationStationView(observations.ObservationStation)
    )
    admin.add_view(
        observations_views.ObservationSeriesConfigurationView(
            observations.ObservationSeriesConfiguration
        )
    )
    admin.add_view(
        DropDown(
            "Legacy",
            icon="fa-solid fa-vials",
            views=[
                coverage_views.ConfigurationParameterView(
                    coverages.ConfigurationParameter
                ),
                coverage_views.CoverageConfigurationView(
                    coverages.CoverageConfiguration
                ),
                observations_views.StationView(observations.Station),
            ],
        )
    )
    admin.add_view(
        DropDown(
            "Measurements",
            icon="fa-solid fa-vials",
            views=[
                observations_views.MonthlyMeasurementView(
                    observations.MonthlyMeasurement
                ),
                observations_views.SeasonalMeasurementView(
                    observations.SeasonalMeasurement
                ),
                observations_views.YearlyMeasurementView(
                    observations.YearlyMeasurement
                ),
            ],
        )
    )
    admin.add_view(
        Link(
            "V2 API docs",
            icon="fa fa-link",
            url=f"{settings.public_url}{settings.v2_api_mount_prefix}/docs",
            target="blank_",
        )
    )
    admin.add_view(
        Link(
            "Public site",
            icon="fa fa-link",
            url=f"{settings.public_url}",
            target="blank_",
        )
    )
    return admin
