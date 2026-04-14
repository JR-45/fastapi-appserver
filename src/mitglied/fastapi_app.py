"""MainApp."""

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Final

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from mitglied.config.dev.db_populate import db_populate
from mitglied.entity.base import Base
from mitglied.graphql_api import graphql_router
from mitglied.repository.session_factory import engine
from mitglied.router import mitglied_router, mitglied_write_router
from mitglied.security.auth_router import router as auth_router
from mitglied.security.exceptions import AuthorizationError, LoginError
from mitglied.security.role import Role
from mitglied.security.roles_required import RolesRequired
from mitglied.service.exceptions import (
    EmailExistsError,
    ForbiddenError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:  # noqa: RUF029
    """Startup und Shutdown."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db_populate()
    logger.info("Server startet...")
    yield
    logger.info("Server wird heruntergefahren...")


app: Final = FastAPI(lifespan=lifespan)

app.add_middleware(GZipMiddleware, minimum_size=500)

app.include_router(mitglied_router, prefix="/rest")

app.include_router(mitglied_write_router, prefix="/rest")

app.include_router(auth_router, prefix="/auth")

app.include_router(
    graphql_router,
    prefix="/graphql",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.MITGLIED]))],
)


@app.exception_handler(AuthorizationError)
def authorization_error_handler(
    _request: Request, _err: AuthorizationError
) -> Response:
    """Errorhandler für AuthorizationError."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": "Nicht autorisiert"},
    )


@app.exception_handler(LoginError)
def login_error_handler(_request: Request, err: LoginError) -> Response:
    """Errorhandler für LoginError."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": str(err)},
    )


@app.exception_handler(NotFoundError)
def not_found_error_handler(_request: Request, _err: NotFoundError) -> Response:
    """Errorhandler für NotFoundError."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "Nicht gefunden"},
    )


@app.exception_handler(EmailExistsError)
def email_exists_error_handler(_request: Request, err: EmailExistsError) -> Response:
    """Errorhandler für EmailExistsError."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": f"Emailadresse bereits vorhanden: {err.email}"},
    )


@app.exception_handler(UsernameExistsError)
def username_exists_error_handler(
    _request: Request, err: UsernameExistsError
) -> Response:
    """Errorhandler für UsernameExistsError."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": f"Benutzername bereits vorhanden: {err.username}"},
    )


@app.exception_handler(ForbiddenError)
def forbidden_error_handler(_request: Request, _err: ForbiddenError) -> Response:
    """Errorhandler für ForbiddenError."""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"message": "Zugriff verweigert"},
    )


@app.exception_handler(VersionOutdatedError)
def version_outdated_error_handler(
    _request: Request, err: VersionOutdatedError
) -> Response:
    """Errorhandler für VersionOutdatedError."""
    return JSONResponse(
        status_code=status.HTTP_412_PRECONDITION_FAILED,
        content={"message": f"Versionsnummer veraltet: {err.version}"},
    )
