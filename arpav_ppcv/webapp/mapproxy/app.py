import logging

import mapproxy.wsgiapp
import sqlmodel
from fastapi.middleware.wsgi import WSGIMiddleware
from mapproxy.wsgiapp import make_wsgi_app as make_mapproxy_app
import mapproxy.config.loader
import mapproxy.config.spec
import mapproxy.config.validator

from ... import database
from ...config import ArpavPpcvSettings

logger = logging.getLogger(__name__)

mapproxy_app = make_mapproxy_app()


def create_mapproxy_app(settings: ArpavPpcvSettings) -> WSGIMiddleware:
    mapproxy_config = load_mapproxy_configuration(
        settings, seed=False, ignore_warnings=settings.debug, renderd=False
    )
    services = mapproxy_config.configured_services()
    app = mapproxy.wsgiapp.MapProxyApp(services, mapproxy_config.base_config)
    if settings.debug:
        app = mapproxy.wsgiapp.wrap_wsgi_debug(app, mapproxy_config)
    app.config_files = None
    return WSGIMiddleware(app)


def build_mapproxy_config(
    settings: ArpavPpcvSettings, session: sqlmodel.Session
) -> dict:
    all_covs = database.collect_all_coverages(session)
    internal_sources = {
        f"internal_source_{cov.identifier}": {
            "type": "WMS",
            "req": {
                "url": f"{settings.public_url}/coverages/{cov.identifier}/wms",
                "layers": ",".join(
                    (
                        cov.configuration.wms_main_layer_name,
                        cov.configuration.wms_secondary_layer_name,
                    )
                ),
                "transparent": True,
            },
        }
        for cov in all_covs
    }
    mapproxy_config = {
        "globals": {
            "image": "nearest",
        },
        "services": {
            "wms": {
                "md": {
                    "title": "",
                    "abstract": "",
                    "online_resource": settings.public_url,
                    "contact": {
                        "person": settings.contact.name,
                        "position": "",
                        "organization": "",
                        "address": "",
                        "city": "",
                        "postcode": "",
                        "state": "",
                        "country": "",
                        "phone": "",
                        "fax": "",
                        "email": settings.contact.email,
                    },
                    "access_constraints": "",
                    "fees": "",
                    "keyword_list": [],
                },
                "srs": ["EPSG:4326"],
            },
            "wmts": {
                "kvp": True,
                "restful": True,
                "featureinfo_formats": [
                    {"mimetype": "application/gml+xml", "suffix": "gml"},
                    {"mimetype": "text/html", "suffix": "html"},
                ],
            },
        },
        "sources": {
            **internal_sources,
        },
        "caches": {
            "main_cache": {
                "sources": [s for s in internal_sources.keys()],
            },
            "grids": [],
            "cache": {
                "type": "file",
            },
        },
        "layers": [
            {
                "name": cov.identifier,
                "title": cov.identifier,
                "sources": ["main_cache"],
            }
            for cov in all_covs
        ],
        "grids": None,
        "parts": None,
        "base": None,  # not supported
    }
    return mapproxy_config


def load_mapproxy_configuration(
    settings: ArpavPpcvSettings, seed: bool, ignore_warnings: bool, renderd: bool
) -> mapproxy.config.loader.ProxyConfiguration:
    mapproxy.config.loader.load_plugins()

    conf_dict = build_mapproxy_config(settings)
    errors, informal_only = mapproxy.config.spec.validate_options(conf_dict)
    for error in errors:
        logger.warning(error)
    if not informal_only or (errors and not ignore_warnings):
        raise mapproxy.config.loader.ConfigurationError("invalid configuration")

    errors = mapproxy.config.validator.validate(conf_dict)
    for error in errors:
        logger.warning(error)

    return mapproxy.config.loader.ProxyConfiguration(
        conf_dict, seed=seed, renderd=renderd
    )
