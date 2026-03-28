"""MainApp."""

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Final

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger

from mitglied.router.mitglied_router import router as mitglied_router

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:  # noqa: RUF029
    """Startup und Shutdown."""
    logger.info("Server startet...")
    yield
    logger.info("Server wird heruntergefahren...")


app: Final = FastAPI(lifespan=lifespan)

app.add_middleware(GZipMiddleware, minimum_size=500)

app.include_router(mitglied_router, prefix="/rest")
