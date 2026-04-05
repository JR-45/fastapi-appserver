from collections.abc import Mapping, Sequence
from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from mitglied.entity import Mitglied
from mitglied.repository.pageable import Pageable
from mitglied.repository.slice import Slice


class MitgliedRepository:
    """Repository für Mitglied entity mit CRUD-Methoden"""

    def find_by_id(self, mitglied_id: int | None, session: Session) -> Mitglied | None:
        """Suche nach Mitglied über die ID

        :param mitglied_id: ID des Mitglieds
        :return: Mitglied oder None, falls nicht gefunden
        :rtype: Mitglied | None
        """
        logger.debug("mitglied_id=|{}", mitglied_id)

        if mitglied_id is None:
            return None
        statement: Final = (
            select(Mitglied)
            .options(joinedload(Mitglied.ausweis))
            .where(Mitglied.id == mitglied_id)
        )

        mitglied: Final = session.scalar(statement)

        logger.debug("{}", mitglied)
        return mitglied

    def find_all(self, pageable: Pageable, session: Session) -> Slice[Mitglied]:
        """Suche nach allen Mitgliedern.

        :param pageable: Pagination Parameter
        :param session: Session für SQLAlchemy
        :return: Liste aller Mitglieder
        :rtype: Sequence[Mitglied]
        """
        logger.debug("find_all")
        offset: Final = pageable.number * pageable.size
        statement: Final = (
            (
                select(Mitglied)
                .options(joinedload(Mitglied.ausweis))
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (select(Mitglied).options(joinedload(Mitglied.ausweis)))
        )
        mitglieder: Final = (session.scalars(statement)).all()
        anzahl: Final = self._count_all_rows(session)
        mitglied_slice: Final = Slice(content=tuple(mitglieder), total_elements=anzahl)
        logger.debug("mitglied_slice={}", mitglied_slice)
        return mitglied_slice

    def _count_all_rows(self, session: Session) -> int:
        statement: Final = select(func.count()).select_from(Mitglied)
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

    def exists_email(self, email: str, session: Session) -> bool:
        """Abfrage, ob es die Emailadresse bereits gibt.

        :param email: Emailadresse
        :param session: Session für SQLAlchemy
        :return: True, falls es die Emailadresse bereits gibt, False sonst
        :rtype: bool
        """
        logger.debug("email={}", email)

        statement: Final = select(func.count()).where(Mitglied.email == email)
        anzahl: Final = session.scalar(statement)
        logger.debug("anzahl={}", anzahl)
        return anzahl is not None and anzahl > 0

    def create(self, mitglied: Mitglied, session: Session) -> Mitglied:
        """Speichere ein neues Mitglied ab.

        :param mitglied: Die Daten des neuen Mitglieds ohne ID
        :param session: Session für SQLAlchemy
        :return: Das neu angelegte Mitglied mit generierter ID
        :rtype: Mitglied
        """
        logger.debug(
            "mitglied={}, mitglied.ausweis={}, mitglied.ausleihen={}",
            mitglied,
            mitglied.ausweis,
            mitglied.ausleihen,
        )
        session.add(instance=mitglied)
        session.flush(objects=[mitglied])
        logger.debug("mitglied_id={}", mitglied.id)
        return mitglied
