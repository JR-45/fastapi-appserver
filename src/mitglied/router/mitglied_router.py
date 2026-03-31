"""MitgliedRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends
from loguru import logger

from mitglied.service.mitglied_service import MitgliedService
from mitglied.repository import MitgliedRepository

router: Final = APIRouter(tags=["Mitglieder"])


def get_service() -> MitgliedService:
    """Service als Dependency."""
    repo = MitgliedRepository()
    return MitgliedService(repo=repo)


@router.get("")
def get_alle(
    service: Annotated[MitgliedService, Depends(get_service)],
) -> list:
    """Alle Mitglieder zurückgeben."""
    logger.debug("GET alle Mitglieder")
    return service.find_all()


@router.get("/{mitglied_id}")
def get_by_id(
    mitglied_id: int,
    service: Annotated[MitgliedService, Depends(get_service)],
) -> dict:
    """Suche mit der Mitglied-ID."""
    logger.debug("mitglied_id={}", mitglied_id)
    mitglied = service.find_by_id(mitglied_id=mitglied_id)
    return {"mitglied": mitglied}
