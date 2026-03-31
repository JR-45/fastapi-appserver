from collections.abc import Mapping, Sequence
from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from mitglied.entity import Mitglied


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

    def find_all(self, session: Session) -> Sequence[Mitglied]:
        """Suche nach allen Mitgliedern.

        :param session: Datenbank-Session
        :return: Liste aller Mitglieder
        :rtype: Sequence[Mitglied]
        """
        logger.debug("find_all")

        statement: Final = select(Mitglied).options(joinedload(Mitglied.ausweis))
        mitglieder: Final = session.scalars(statement).all()

        logger.debug("Anzahl gefunden: {}", len(mitglieder))
        return mitglieder
