import enum
import fastapi
from fastapi.middleware.cors import CORSMiddleware

from ... import config
from .routers.climaticindicators import router as climaticindicators_router
from .routers.coverages import router as coverages_router
from .routers.municipalities import router as municipalities_router
from .routers.observations import router as observations_router
from .routers.base import router as base_router


class WebAppOpenApiTag(enum.Enum):
    BASE = "base"
    CLIMATIC_INDICATORS = "climatic_indicators"
    COVERAGES = "coverages"
    MUNICIPALITIES = "municipalities"
    OBSERVATIONS = "observations"

    def get_description(self) -> str:
        return {
            self.BASE: "Operations that provide information about this API",
            self.CLIMATIC_INDICATORS: "Operations related to climatic indicators",
            self.COVERAGES: (
                "Operations that deal with coverages of forecast and " "historical data"
            ),
            self.MUNICIPALITIES: "Operations related to municipalities",
            self.OBSERVATIONS: (
                "Operations related to observation stations and measurements"
            ),
        }.get(self)

    def as_app_tag(self) -> dict:
        return {
            "name": self.value,
            "description": self.get_description(),
        }


def create_app(settings: config.ArpavPpcvSettings) -> fastapi.FastAPI:
    app = fastapi.FastAPI(
        debug=settings.debug,
        title="arpav cline backend v2",
        description=(
            "### Developer API for arpav cline backend v2\n"
            "This is the documentation for API v2, which is the new implementation "
            "of the system and is the recommended way to interact with it."
        ),
        contact={
            "name": settings.contact.name,
            "url": settings.contact.url,
            "email": settings.contact.email,
        },
        servers=[{"url": "/".join((settings.public_url, "api/v2"))}],
        root_path_in_servers=False,
        openapi_tags=[
            WebAppOpenApiTag.COVERAGES.as_app_tag(),
            WebAppOpenApiTag.OBSERVATIONS.as_app_tag(),
            WebAppOpenApiTag.CLIMATIC_INDICATORS.as_app_tag(),
            WebAppOpenApiTag.MUNICIPALITIES.as_app_tag(),
            WebAppOpenApiTag.BASE.as_app_tag(),
        ],
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.allow_cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=["*"],
    )
    app.include_router(
        base_router,
        prefix="/base",
        tags=[
            WebAppOpenApiTag.BASE,
        ],
    )
    app.include_router(
        coverages_router,
        prefix="/coverages",
        tags=[
            WebAppOpenApiTag.COVERAGES,
        ],
    )
    app.include_router(
        observations_router,
        prefix="/observations",
        tags=[
            WebAppOpenApiTag.OBSERVATIONS,
        ],
    )
    app.include_router(
        municipalities_router,
        prefix="/municipalities",
        tags=[
            WebAppOpenApiTag.MUNICIPALITIES,
        ],
    )
    app.include_router(
        climaticindicators_router,
        prefix="/climatic-indicators",
        tags=[
            WebAppOpenApiTag.CLIMATIC_INDICATORS,
        ],
    )
    return app
