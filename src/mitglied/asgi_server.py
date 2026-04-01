"""Funktion `run` für die FastAPI-Applikation mit dem ASGI-Server _uvicorn_."""

from ssl import PROTOCOL_TLS_SERVER

import uvicorn

from mitglied.config import (
    host_binding,
    port,
    tls_certfile,
    tls_keyfile,
)
from mitglied.fastapi_app import app  # noqa: F401

__all__ = ["run"]


def run() -> None:
    """Start der Anwendung mit uvicorn."""
    uvicorn.run(
        "mitglied:app",
        loop="asyncio",
        http="h11",
        interface="asgi3",
        host=host_binding,
        port=port,
        ssl_keyfile=tls_keyfile,
        ssl_certfile=tls_certfile,
        ssl_version=PROTOCOL_TLS_SERVER,  # DevSkim: ignore DS440070
    )
