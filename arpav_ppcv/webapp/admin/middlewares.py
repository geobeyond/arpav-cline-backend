from contextlib import contextmanager
from typing import Generator

import sqlalchemy
import sqlmodel
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.contrib.sqla.middleware import DBSessionMiddleware


@contextmanager
def get_sqlmodel_session(
    engine: sqlalchemy.Engine,
) -> Generator[sqlmodel.Session, None, None]:
    session: sqlmodel.Session = sqlmodel.Session(engine, expire_on_commit=False)
    try:
        yield session
    except Exception as e:  # pragma: no cover
        session.rollback()
        raise e
    finally:
        session.close()


class SqlModelDbSessionMiddleware(DBSessionMiddleware):
    """Middleware for DB that uses sqlmodel.Session.

    This is derived from the starlette_admin DBSessionMiddleware because we
    want to use sqlmodel `Session` instances in our admin, rather than the
    default sqlalchemy `Session`. This is because our DB-handling
    functions, defined in `arpav_ppcv.database`, expect to use an
    sqlmodel.Session. The main differences between these two sessuin classes
    are described in the sqlmodel docs:

    https://sqlmodel.tiangolo.com/tutorial/select/#sqlmodels-sessionexec

    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if isinstance(self.engine, AsyncEngine):
            async with AsyncSession(self.engine, expire_on_commit=False) as session:
                request.state.session = session
                return await call_next(request)
        else:
            with get_sqlmodel_session(self.engine) as session:
                request.state.session = session
                return await call_next(request)
