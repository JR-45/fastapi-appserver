"""Entry point for the mitglied FastAPI application."""

from mitglied.asgi_server import run

__all__: list[str] = ["run"]


if __name__ == "__main__":
    run()
