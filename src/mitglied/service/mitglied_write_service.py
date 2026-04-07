"""Geschäftslogik zum Schreiben von Mitgliedsdaten."""

from typing import Final

from loguru import logger

from mitglied.entity.mitglied import Mitglied
from mitglied.repository import MitgliedRepository, Session
from mitglied.service.exceptions import EmailExistsError
from mitglied.service.mitglied_dto import MitgliedDTO

__all__ = ["MitgliedWriteService"]


class MitgliedWriteService:
    """Service-Klasse mit Geschäftslogik für Mitglied."""

    def __init__(self, repo: MitgliedRepository) -> None:
        """Konstruktor mit abhängigem MitgliedRepository."""
        self.repo: MitgliedRepository = repo

    def create(self, mitglied: Mitglied) -> MitgliedDTO:
        """Einen neuen Mitglied anlegen.

        :param mitglied: Das neue Mitglied ohne ID
        :return: Das neu angelegte Mitglied mit generierter ID
        :rtype: MitgliedDTO
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug(
            "mitglied={}, ausweis={}, ausleihen={}",
            mitglied,
            mitglied.ausweis,
            mitglied.ausleihen,
        )

        email: Final = mitglied.email

        with Session() as session:
            if self.repo.exists_email(email=email, session=session):
                raise EmailExistsError(email=email)

            mitglied_db: Final = self.repo.create(mitglied=mitglied, session=session)
            mitglied_dto: Final = MitgliedDTO(mitglied_db)
            session.commit()

        logger.debug("mitglied_dto={}", mitglied_dto)
        return mitglied_dto
