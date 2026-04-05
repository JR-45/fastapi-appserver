"""Geschäftslogik für Mitgliedsdaten."""

from collections.abc import Mapping
from typing import Final

from loguru import logger

from mitglied.repository import MitgliedRepository, Session
from mitglied.repository.pageable import Pageable
from mitglied.repository.slice import Slice
from mitglied.service.exceptions import NotFoundError
from mitglied.service.mitglied_dto import MitgliedDTO

__all__ = ["MitgliedService"]


class MitgliedService:
    """Service-Klasse mit Geschäftslogik für Mitglied."""

    def __init__(self, repo: MitgliedRepository) -> None:
        """Konstruktor mit abhängigem MitgliedRepository."""
        self.repo: MitgliedRepository = repo

    def find_by_id(self, mitglied_id: int) -> MitgliedDTO:
        """Suche mit der Mitglied-ID.

        :param mitglied_id: ID für die Suche
        :return: Das gefundene Mitglied
        :rtype: MitgliedDTO
        :raises NotFoundError: Falls kein Mitglied gefunden wurde
        """
        logger.debug("mitglied_id={}", mitglied_id)
        with Session() as session:
            mitglied = self.repo.find_by_id(mitglied_id=mitglied_id, session=session)
            if mitglied is None:
                logger.debug("Mitglied nicht gefunden: {}", mitglied_id)
                raise NotFoundError(mitglied_id=mitglied_id)
            logger.debug("{}", mitglied)
            mitglied_dto: Final = MitgliedDTO(mitglied)
            return mitglied_dto

    def find(
        self,
        suchparameter: Mapping[str, str],
        pageable: Pageable,
    ) -> Slice[MitgliedDTO]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter
        :return: Liste der gefundenen Mitglieder
        :rtype: Slice[MitgliedDTO]
        :raises NotFoundError: Falls keine Mitglieder gefunden wurden
        """
        logger.debug("{}", suchparameter)
        with Session() as session:
            mitglied_slice: Final = self.repo.find(
                suchparameter=suchparameter, pageable=pageable, session=session
            )
            if len(mitglied_slice.content) == 0:
                raise NotFoundError(suchparameter=suchparameter)

            mitglieder_dto: Final = tuple(
                MitgliedDTO(mitglied) for mitglied in mitglied_slice.content
            )
            session.commit()
        mitglieder_dto_slice = Slice(
            content=mitglieder_dto, total_elements=mitglied_slice.total_elements
        )
        logger.debug("{}", mitglieder_dto_slice)
        return mitglieder_dto_slice
