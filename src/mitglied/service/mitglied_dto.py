"""DTO-Klasse für Mitgliedsdaten im Service-Ordner."""

from dataclasses import dataclass
from datetime import date, datetime

import strawberry

from mitglied.entity.geschlecht import Geschlecht
from mitglied.entity.interesse import Interesse
from mitglied.entity.mitglied import Mitglied
from mitglied.entity.mitgliedsstatus import Mitgliedsstatus

__all__ = ["MitgliedDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type
class MitgliedDTO:
    """DTO-Klasse für Mitgliedsdaten (Service-Schicht)."""

    id: int
    version: int
    vorname: str
    nachname: str
    email: str
    geburtsdatum: date
    telefonnummer: str
    geschlecht: Geschlecht | None
    mitgliedsstatus: Mitgliedsstatus | None
    beitrittsdatum: date
    interessen: list[Interesse]
    erzeugt: datetime | None
    aktualisiert: datetime | None

    def __init__(self, mitglied: Mitglied):
        """Initialisierung von MitgliedDTO durch ein Entity-Objekt von Mitglied.

        :param mitglied: Mitglied-Objekt mit Decorators zu SQLAlchemy
        """
        mitglied_id = mitglied.id
        self.id = mitglied_id if mitglied_id is not None else -1
        self.version = mitglied.version
        self.vorname = mitglied.vorname
        self.nachname = mitglied.nachname
        self.email = mitglied.email
        self.geburtsdatum = mitglied.geburtsdatum
        self.telefonnummer = mitglied.telefonnummer
        self.geschlecht = mitglied.geschlecht
        self.mitgliedsstatus = mitglied.mitgliedsstatus
        self.beitrittsdatum = mitglied.beitrittsdatum
        self.interessen = (
            [Interesse[interesse] for interesse in mitglied.interessen_json]
            if mitglied.interessen_json is not None
            else []
        )
