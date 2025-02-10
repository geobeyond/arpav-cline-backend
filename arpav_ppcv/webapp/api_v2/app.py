import fastapi
from fastapi.middleware.cors import CORSMiddleware

from ... import config
from .routers.coverages import router as coverages_router
from .routers.municipalities import router as municipalities_router
from .routers.observations import router as observations_router
from .routers.base import router as base_router


def create_app(settings: config.ArpavPpcvSettings) -> fastapi.FastAPI:
    app = fastapi.FastAPI(
        debug=settings.debug,
        title="ARPAV PPCV backend v2",
        description=(
            "### Developer API for ARPAV-PPCV backend v2\n"
            "This is the documentation for API v2, which is the new implementation "
            "of the system and is the recommended way to interact with it."
        ),
        contact={
            "name": settings.contact.name,
            "url": settings.contact.url,
            "email": settings.contact.email,
        },
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
            "base",
        ],
    )
    app.include_router(
        coverages_router,
        prefix="/coverages",
        tags=[
            "coverages",
        ],
    )
    app.include_router(
        observations_router,
        prefix="/observations",
        tags=[
            "observations",
        ],
    )
    app.include_router(
        municipalities_router,
        prefix="/municipalities",
        tags=[
            "municipalities",
        ],
    )
    return app
