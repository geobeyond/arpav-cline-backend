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
    overviews,
)
from . import auth
from .middlewares import SqlModelDbSessionMiddleware
from .views import (
    base as base_views,
    climaticindicators as climaticindicators_views,
    coverages as coverage_views,
    observations as observations_views,
    overviews as overviews_views,
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
    admin.add_view(
        DropDown(
            "Overviews",
            icon="fa-regular fa-flag",
            always_open=False,
            views=[
                overviews_views.ForecastOverviewSeriesConfigurationView(
                    overviews.ForecastOverviewSeriesConfiguration
                ),
                overviews_views.ObservationOverviewSeriesConfigurationView(
                    overviews.ObservationOverviewSeriesConfiguration
                ),
            ],
        )
    )
    admin.add_view(
        DropDown(
            "Forecasts",
            icon="fa-solid fa-chart-line",
            always_open=False,
            views=[
                coverage_views.ForecastCoverageConfigurationView(
                    coverages.ForecastCoverageConfiguration
                ),
                coverage_views.ForecastModelView(coverages.ForecastModel),
                coverage_views.ForecastTimeWindowView(coverages.ForecastTimeWindow),
            ],
        )
    )
    admin.add_view(
        DropDown(
            "Historical",
            icon="fa-solid fa-clock-rotate-left",
            always_open=False,
            views=[
                coverage_views.HistoricalCoverageConfigurationView(
                    coverages.HistoricalCoverageConfiguration
                ),
            ],
        )
    )
    admin.add_view(
        DropDown(
            "Observations",
            icon="fa-solid fa-ruler",
            always_open=False,
            views=[
                observations_views.ObservationMeasurementView(
                    observations.ObservationMeasurement
                ),
                observations_views.ObservationSeriesConfigurationView(
                    observations.ObservationSeriesConfiguration
                ),
                observations_views.ObservationStationView(
                    observations.ObservationStation
                ),
            ],
        )
    )
    admin.add_view(
        DropDown(
            "Legacy",
            icon="fa-solid fa-circle-xmark",
            always_open=False,
            views=[
                coverage_views.ConfigurationParameterView(
                    coverages.ConfigurationParameter
                ),
                coverage_views.CoverageConfigurationView(
                    coverages.CoverageConfiguration
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
