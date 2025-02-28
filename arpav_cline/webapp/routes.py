"""Routes for the main starlette application."""

from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette.routing import Route


def landing_page(request: Request):
    templates: Jinja2Templates = request.app.state.templates
    return templates.TemplateResponse(
        request,
        "landing_page.html",
        context={
            "v1_api_docs_url": request.app.state.v1_api_docs_url,
            "v2_api_docs_url": request.app.state.v2_api_docs_url,
            "legacy_base_url": request.app.state.legacy_base_url,
        },
    )


routes = [
    Route("/", landing_page),
]
