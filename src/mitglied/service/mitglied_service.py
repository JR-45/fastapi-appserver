"""Geschäftslogik für Mitgliedsdaten."""

from loguru import logger

from mitglied.entity.mitglied import Mitglied
from mitglied.repository import MitgliedRepository, Session
from mitglied.repository.pageable import Pageable
from mitglied.service.exceptions import NotFoundError

__all__ = ["MitgliedService"]


class MitgliedService:
    """Service-Klasse mit Geschäftslogik für Mitglied."""

    def __init__(self, repo: MitgliedRepository) -> None:
        """Konstruktor mit abhängigem MitgliedRepository."""
        self.repo: MitgliedRepository = repo

    def find_by_id(self, mitglied_id: int) -> Mitglied:
        """Suche mit der Mitglied-ID.

        :param mitglied_id: ID für die Suche
        :return: Das gefundene Mitglied
        :raises NotFoundError: Falls kein Mitglied gefunden wurde
        """
        logger.debug("mitglied_id={}", mitglied_id)
        with Session() as session:
            mitglied = self.repo.find_by_id(mitglied_id=mitglied_id, session=session)
            if mitglied is None:
                logger.debug("Mitglied nicht gefunden: {}", mitglied_id)
                raise NotFoundError(mitglied_id=mitglied_id)
            logger.debug("{}", mitglied)
            return mitglied

    def find_all(self) -> list[Mitglied]:
        """Alle Mitglieder zurückgeben.

        :return: Liste aller Mitglieder
        """
        with Session() as session:
            pageable = Pageable(size=0, number=0)
            mitglieder = self.repo.find_all(pageable=pageable, session=session)
            logger.debug("{}", mitglieder)
            return list(mitglieder.content)
