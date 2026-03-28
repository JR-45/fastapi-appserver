"""MitgliedRouter."""

from typing import Final

from fastapi import APIRouter
from loguru import logger

router: Final = APIRouter(tags=["Mitglieder"])


@router.get("")
def get_alle() -> dict[str, list[object]]:
    """Alle Mitglieder zurückgeben."""
    logger.debug("GET alle Mitglieder")
    return {"mitglieder": []}


@router.get("/{mitglied_id}")
def get_by_id(mitglied_id: int) -> dict[str, object]:
    """Suche mit der Mitglied-ID."""
    logger.debug("mitglied_id={}", mitglied_id)
    return {"id": mitglied_id, "name": "Max Mustermann"}
