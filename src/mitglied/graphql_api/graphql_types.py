"""GraphQL Typen für Mitglied."""

from __future__ import annotations

from datetime import date, datetime

import strawberry

from mitglied.entity.ausweis import Ausweis
from mitglied.entity.geschlecht import Geschlecht
from mitglied.entity.interesse import Interesse
from mitglied.entity.mitglied import Mitglied
from mitglied.entity.mitgliedsstatus import Mitgliedsstatus

__all__ = ["AusweisType", "MitgliedType"]


@strawberry.type
class AusweisType:
    """GraphQL Typ für Ausweis."""

    id: int
    ausstellungsdatum: date
    ablaufdatum: date

    @staticmethod
    def from_entity(ausweis: Ausweis) -> AusweisType:
        """Ausweis-Entity in GraphQL-Typ umwandeln."""
        return AusweisType(
            id=ausweis.id,
            ausstellungsdatum=ausweis.ausstellungsdatum,
            ablaufdatum=ausweis.ablaufdatum,
        )


@strawberry.type
class MitgliedType:
    """GraphQL Typ für Mitglied."""

    id: int | None = None
    vorname: str
    nachname: str
    email: str
    geburtsdatum: date
    telefonnummer: str
    beitrittsdatum: date
    version: int
    geschlecht: Geschlecht | None = None
    mitgliedsstatus: Mitgliedsstatus | None = None
    interessen: list[Interesse] | None = None
    erzeugt: datetime | None = None
    aktualisiert: datetime | None = None
    ausweis: AusweisType | None = None

    @staticmethod
    def from_entity(mitglied: Mitglied) -> MitgliedType:
        """Mitglied-Entity in GraphQL-Typ umwandeln."""
        return MitgliedType(
            id=mitglied.id,
            vorname=mitglied.vorname,
            nachname=mitglied.nachname,
            email=mitglied.email,
            geburtsdatum=mitglied.geburtsdatum,
            telefonnummer=mitglied.telefonnummer,
            beitrittsdatum=mitglied.beitrittsdatum,
            version=mitglied.version,
            geschlecht=mitglied.geschlecht,
            mitgliedsstatus=mitglied.mitgliedsstatus,
            interessen=mitglied.interessen,  # pyright: ignore[reportAttributeAccessIssue]
            erzeugt=mitglied.erzeugt,
            aktualisiert=mitglied.aktualisiert,
            ausweis=(
                AusweisType.from_entity(mitglied.ausweis) if mitglied.ausweis else None
            ),
        )
