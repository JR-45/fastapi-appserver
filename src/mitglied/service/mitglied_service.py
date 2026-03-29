"""Geschäftslogik für Mitgliedsdaten."""

from loguru import logger

from mitglied.entity.mitglied import Mitglied

__all__ = ["MitgliedService"]


class MitgliedService:
    """Service-Klasse mit Geschäftslogik für Mitglied."""

    def find_by_id(self, mitglied_id: int) -> Mitglied | None:
        """Suche mit der Mitglied-ID.

        :param mitglied_id: ID für die Suche
        :return: Das gefundene Mitglied oder None
        """
        logger.debug("mitglied_id={}", mitglied_id)
        # TODO: später durch Repository ersetzen
        return None

    def find_alle(self) -> list[Mitglied]:
        """Alle Mitglieder zurückgeben.

        :return: Liste aller Mitglieder
        """
        logger.debug("find_alle")
        # TODO: später durch Repository ersetzen
        return []
