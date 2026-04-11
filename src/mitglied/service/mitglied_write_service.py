"""Geschäftslogik zum Schreiben von Mitgliedsdaten."""

from typing import Final

from loguru import logger

from mitglied.entity.mitglied import Mitglied
from mitglied.repository import MitgliedRepository, Session
from mitglied.service.exceptions import (
    EmailExistsError,
    NotFoundError,
    VersionOutdatedError,
)
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

        # durch "with" erhaelt man einen "Context Manager", der die Ressource/Session
        # am Endes des Blocks schliesst
        with Session() as session:
            if self.repo.exists_email(email=email, session=session):
                raise EmailExistsError(email=email)

            mitglied_db: Final = self.repo.create(mitglied=mitglied, session=session)
            mitglied_dto: Final = MitgliedDTO(mitglied_db)
            session.commit()

        logger.debug("mitglied_dto={}", mitglied_dto)
        return mitglied_dto

    def update(self, mitglied: Mitglied, mitglied_id: int, version: int) -> MitgliedDTO:
        """Ein Mitglied aktualisieren.

        :param mitglied: Die neuen Daten
        :param mitglied_id: ID des zu aktualisierenden Mitglieds
        :param version: Version des zu aktualisierenden Mitglieds
        :return: Der aktualisierte Mitglied
        :rtype: MitgliedDTO
        :raises NotFoundError: Falls der zu aktualisierende Mitglied nicht existiert
        :raises VersionOutdatedError: Falls die Version veraltet ist
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug("mitglied_id={}, {}", mitglied_id, mitglied)
        with Session() as session:
            if (
                mitglied_db := self.repo.find_by_id(
                    mitglied_id=mitglied_id, session=session
                )
            ) is None:
                raise NotFoundError(mitglied_id)
            if mitglied_db.version > version:
                raise VersionOutdatedError(version)

            email: Final = mitglied.email
            if email != mitglied_db.email and self.repo.exists_email_other_id(
                mitglied_id=mitglied_id,
                email=email,
                session=session,
            ):
                raise EmailExistsError(email)

            mitglied_db.set(mitglied)

            if (
                mitglied_updated := self.repo.update(
                    mitglied=mitglied_db, session=session
                )
            ) is None:
                raise NotFoundError(mitglied_id)
            mitglied_dto: Final = MitgliedDTO(mitglied_updated)
            logger.debug("mitglied_dto={}", mitglied_dto)

            session.commit()
            mitglied_dto.version += 1
            return mitglied_dto
