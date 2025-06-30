import fastapi
from fastapi.middleware.cors import CORSMiddleware

from ... import config
from .routers.climaticindicators import router as climaticindicators_router
from .routers.base import router as base_router


def create_app(settings: config.ArpavPpcvSettings) -> fastapi.FastAPI:
    app = fastapi.FastAPI(
        debug=settings.debug,
        title="arpav cline backend v3",
        description="Developer API for arpav cline backend v3",
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
        climaticindicators_router,
        prefix="/climatic-indicators",
        tags=[
            "climatic-indicators",
        ],
    )
    return app
