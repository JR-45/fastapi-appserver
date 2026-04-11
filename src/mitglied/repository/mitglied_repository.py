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

    def find(
        self,
        suchparameter: Mapping[str, str],
        pageable: Pageable,
        session: Session,
    ) -> Slice[Mitglied]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter als Dictionary
        :param pageable: Anzahl Datensätze und Seitennummer
        :param session: Session für SQLAlchemy
        :return: Tupel, d.h. readonly Liste, der gefundenen Mitglieder oder leeres Tupel
        :rtype: Slice[Mitglied]
        """
        log_str: Final = "{}"
        logger.debug(log_str, suchparameter)
        if not suchparameter:
            return self.find_all(pageable=pageable, session=session)

        for key, value in suchparameter.items():
            if key == "email":
                mitglied = self.find_by_email(email=value, session=session)
                logger.debug(log_str, mitglied)
                return (
                    Slice(content=(mitglied,), total_elements=1)
                    if mitglied is not None
                    else Slice(content=(), total_elements=0)
                )
            if key == "nachname":
                mitglieder = self.find_by_nachname(
                    teil=value, pageable=pageable, session=session
                )
                logger.debug(log_str, mitglieder)
                return mitglieder
        return Slice(content=(), total_elements=0)

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

    def find_by_email(self, email: str, session: Session) -> Mitglied | None:
        """Einen Mitglied anhand der Emailadresse suchen.

        :param email: Emailadresse
        :param session: Session für SQLAlchemy
        :return: Gefundener Mitglied, falls es einen Mitglied gibt, sonst None
        :rtype: Mitglied | None
        """
        logger.debug("email={}", email)  # NOSONAR
        statement: Final = (
            select(Mitglied)
            .options(joinedload(Mitglied.ausweis))
            .where(Mitglied.email == email)
        )
        mitglied: Final = session.scalar(statement)
        logger.debug("{}", mitglied)
        return mitglied

    def find_by_nachname(
        self,
        teil: str,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Mitglied]:
        logger.debug("teil={}", teil)
        offset = pageable.number * pageable.size
        statement: Final = (
            (
                select(Mitglied)
                .options(joinedload(Mitglied.ausweis))
                .filter(Mitglied.nachname.ilike(f"%{teil}%"))
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (
                select(Mitglied)
                .options(joinedload(Mitglied.ausweis))
                .filter(Mitglied.nachname.ilike(f"%{teil}%"))
            )
        )
        mitglieder: Final = session.scalars(statement).all()
        anzahl: Final = self.count_rows_nachname(teil, session)
        mitglied_slice: Final = Slice(content=tuple(mitglieder), total_elements=anzahl)
        logger.debug("{}", mitglied_slice)
        return mitglied_slice

    def count_rows_nachname(self, teil: str, session: Session) -> int:
        statement: Final = (
            select(func.count())
            .select_from(Mitglied)
            .filter(Mitglied.nachname.ilike(f"%{teil}%"))
        )
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

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

    def exists_email_other_id(
        self,
        email: str,
        mitglied_id: int,
        session: Session,
    ) -> bool:
        """Abfrage, ob es die Emailadresse bei einer anderen Mitglied-ID bereits gibt.

        :param email: Emailadresse
        :param mitglied_id: eigene Mitglied-ID
        :param session: Session für SQLAlchemy
        :return: True, falls es die Emailadresse bereits gibt, False sonst
        :rtype: bool
        """
        logger.debug("email={}", email)

        statement: Final = select(Mitglied.id).where(Mitglied.email == email)
        id_db: Final = session.scalar(statement)
        logger.debug("id_db={}", id_db)
        return id_db is not None and id_db != mitglied_id

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

    def update(self, mitglied: Mitglied, session: Session) -> Mitglied | None:
        """Aktualisiere ein Mitglied.

        :param mitglied: Die neuen Mitgliedsdaten
        :param session: Session für SQLAlchemy
        :return: Das aktualisierte Mitglied oder None, falls kein Mitglied mit der ID
        existiert
        :rtype: Mitglied | None
        """
        logger.debug("{}", mitglied)

        if (
            mitglied_db := self.find_by_id(mitglied_id=mitglied.id, session=session)
        ) is None:
            return None
        logger.debug("{}", mitglied_db)
        return mitglied_db
