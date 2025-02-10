import contextlib

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .. import (
    config,
    database,
)
from .api_v2.app import create_app as create_v2_app
from .admin.app import create_admin
from .routes import routes


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    yield
    # ensure the database engine is properly disposed of, closing any connections
    database._DB_ENGINE.dispose()  # noqa
    database._DB_ENGINE = None


def create_app_from_settings(settings: config.ArpavPpcvSettings) -> Starlette:
    app = Starlette(
        debug=settings.debug,
        routes=routes,
        lifespan=lifespan,
    )
    settings.static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
    admin = create_admin(settings)
    admin.mount_to(app, settings)
    v2_api = create_v2_app(settings)
    app.state.settings = settings
    app.state.templates = Jinja2Templates(str(settings.templates_dir))
    app.state.v2_api_docs_url = "".join(
        (settings.public_url, settings.v2_api_mount_prefix, v2_api.docs_url)
    )
    app.mount(settings.v2_api_mount_prefix, v2_api)
    return app


def create_app() -> Starlette:
    settings = config.get_settings()
    return create_app_from_settings(settings)
