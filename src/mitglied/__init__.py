"""FastAPI-Anwendungspaket."""

from mitglied.asgi_server import run
from mitglied.fastapi_app import app

__all__: list[str] = ["app", "main"]


def main():  # noqa: RUF067
    """Starte die Anwendung."""  # noqa: D401
    run()
