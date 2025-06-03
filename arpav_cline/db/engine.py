import typing
import sqlmodel

if typing.TYPE_CHECKING:
    from .. import config

_DB_ENGINE = None
_TEST_DB_ENGINE = None


def get_engine(
    settings: "config.ArpavPpcvSettings",
    use_test_db: typing.Optional[bool] = False,
):
    # This function implements caching of the sqlalchemy engine, relying on the
    # value of the module global `_DB_ENGINE` variable. This is done in order to
    # - reuse the same database engine throughout the lifecycle of the application
    # - provide an opportunity to clear the cache when needed (e.g.: in the fastapi
    # lifespan function)
    #
    # Note: this function cannot use the `functools.cache` decorator because
    # the `settings` parameter is not hashable
    if use_test_db:
        global _TEST_DB_ENGINE
        if _TEST_DB_ENGINE is None:
            _TEST_DB_ENGINE = sqlmodel.create_engine(
                settings.test_db_dsn.unicode_string(),
                echo=True if settings.verbose_db_logs else False,
            )
        result = _TEST_DB_ENGINE
    else:
        global _DB_ENGINE
        if _DB_ENGINE is None:
            _DB_ENGINE = sqlmodel.create_engine(
                settings.db_dsn.unicode_string(),
                echo=True if settings.verbose_db_logs else False,
                pool_size=settings.db_pool_size,
            )
        result = _DB_ENGINE
    return result
