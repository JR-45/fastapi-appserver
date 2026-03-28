"""Entry point for the mitglied FastAPI application."""

import uvicorn


def main():
    """Start the uvicorn development server for the mitglied app."""
    uvicorn.run("mitglied.fastapi_app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
