import decimal
import logging
from decimal import Decimal
from pathlib import Path
from typing import Optional

import babel
import babel.support
import pydantic
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

LOCALE_IT = babel.Locale.parse("it")
LOCALE_EN = babel.Locale.parse("en")


class ContactSettings(pydantic.BaseModel):
    name: str = "info@geobeyond.it"
    url: str = "http://geobeyond.it"  # noqa
    email: str = "info@geobeyond.it"


class PrefectSettings(pydantic.BaseModel):
    num_flow_retries: int = 5
    flow_retry_delay_seconds: int = 5
    num_task_retries: int = 5
    task_retry_delay_seconds: int = 5
    observation_stations_refresher_flow_cron_schedule: str = (
        "0 1 * * 1"  # run once every week, at 01:00 on monday
    )
    observation_monthly_measurements_refresher_flow_cron_schedule: str = (
        "0 2 * * 1"  # run once every week, at 02:00 on monday
    )
    observation_seasonal_measurements_refresher_flow_cron_schedule: str = (
        "0 3 * * 1"  # run once every week, at 03:00 on monday
    )
    observation_yearly_measurements_refresher_flow_cron_schedule: str = (
        "0 4 * * 1"  # run once every week, at 04:00 on monday
    )
    station_variables_refresher_flow_cron_schedule: str = (
        "0 5 * * 1"  # run once every week, at 05:00 on monday
    )


class ThreddsServerSettings(pydantic.BaseModel):
    base_url: str = "http://localhost:8080/thredds"
    wms_service_url_fragment: str = "wms"
    netcdf_subset_service_url_fragment: str = "ncss/grid"  # noqa
    opendap_service_url_fragment: str = "dodsC"  # noqa
    uncertainty_visualization_scale_range: tuple[float, float] = pydantic.Field(
        default=(0, 9)
    )

    @pydantic.model_validator(mode="after")
    def strip_slashes_from_urls(self):
        self.base_url = self.base_url.strip("/")
        self.wms_service_url_fragment = self.wms_service_url_fragment.strip("/")
        self.netcdf_subset_service_url_fragment = (
            self.netcdf_subset_service_url_fragment.strip("/")
        )
        return self


class AdminUserSettings(pydantic.BaseModel):
    username: str = "arpavadmin"
    password: str = "arpavpassword"
    name: str = "Admin"
    avatar: Optional[str] = None
    company_logo_url: Optional[str] = None
    roles: list[str] = pydantic.Field(
        default_factory=lambda: [
            "read",
            "create",
            "edit",
            "delete",
            "action_make_published",
        ]
    )


class CoverageDownloadSpatialGrid(pydantic.BaseModel):
    min_lon: decimal.Decimal = Decimal("10.279")
    min_lat: decimal.Decimal = Decimal("44.697")
    max_lon: decimal.Decimal = Decimal("13.979")
    max_lat: decimal.Decimal = Decimal("47.097")
    num_rows: int = 24
    num_cols: int = 37


class CoverageDownloadSettings(pydantic.BaseModel):
    spatial_grid: CoverageDownloadSpatialGrid = CoverageDownloadSpatialGrid()
    temporal_snap: int = 5
    cache_dir: Optional[Path] = (
        Path(__file__).parents[1] / "arpav-cache/coverage-downloads"
    )


class ArpavPpcvSettings(BaseSettings):  # noqa
    model_config = SettingsConfigDict(
        env_prefix="ARPAV_PPCV__",  # noqa
        env_nested_delimiter="__",
    )

    debug: bool = False
    bind_host: str = "127.0.0.1"
    bind_port: int = 5001
    public_url: str = "http://localhost:5001"
    db_dsn: pydantic.PostgresDsn = pydantic.PostgresDsn(
        "postgresql://user:password@localhost:5432/arpav_ppcv"
    )
    test_db_dsn: Optional[pydantic.PostgresDsn] = None
    verbose_db_logs: bool = False
    contact: ContactSettings = ContactSettings()
    templates_dir: Optional[Path] = Path(__file__).parent / "webapp/templates"
    static_dir: Optional[Path] = Path(__file__).parent / "webapp/static"
    thredds_server: ThreddsServerSettings = ThreddsServerSettings()
    palettes_dir: Path = Path(__file__).parents[1] / "data/palettes"
    palette_num_stops: int = 5
    prefect: PrefectSettings = PrefectSettings()
    martin_tile_server_base_url: str = "http://localhost:3000"
    nearest_station_radius_meters: int = 1000
    v2_api_mount_prefix: str = "/api/v2"
    log_config_file: Path | None = None
    session_secret_key: str = "changeme"
    admin_user: AdminUserSettings = AdminUserSettings()
    cors_origins: list[str] = []
    cors_methods: list[str] = []
    allow_cors_credentials: bool = False
    coverage_download_settings: CoverageDownloadSettings = CoverageDownloadSettings()
    variable_stations_db_schema: str = "stations"

    @pydantic.model_validator(mode="after")
    def ensure_test_db_dsn(self):
        if self.test_db_dsn is None:
            rest, standard_db_name = self.db_dsn.unicode_string().rpartition("/")[::2]
            test_db_name = f"test_{standard_db_name}"
            self.test_db_dsn = pydantic.PostgresDsn(f"{rest}/{test_db_name}")
        return self


def get_settings() -> ArpavPpcvSettings:
    return ArpavPpcvSettings()


def get_translations(locale: babel.Locale) -> babel.support.NullTranslations:
    base_dir = Path(__file__).parent / "translations"
    return babel.support.Translations.load(dirname=base_dir, locales=[locale])
