# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Entity-Klasse für Mitgliedsdaten."""

from dataclasses import InitVar
from datetime import date, datetime
from typing import Any, Self

from loguru import logger
from sqlalchemy import JSON, Identity, func
from sqlalchemy.orm import (
    Mapped,
    MappedColumn,
    mapped_column,
    reconstructor,
    relationship,
)

from mitglied.entity.ausleihe import Ausleihe
from mitglied.entity.ausweis import Ausweis
from mitglied.entity.base import Base
from mitglied.entity.geschlecht import Geschlecht
from mitglied.entity.interesse import Interesse
from mitglied.entity.mitgliedsstatus import Mitgliedsstatus


class Mitglied(Base):
    """Entity Klasse fuer Mitgliedsdaten."""

    __tablename__ = "mitglied"

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID gemäß der zugehörigen IDENTITY-Spalte."""

    vorname: Mapped[str]
    """Vorname des Mitglieds."""

    nachname: Mapped[str]
    """Nachname des Mitglieds."""

    email: Mapped[str] = mapped_column(unique=True)
    """E-Mail-Adresse des Mitglieds."""

    geburtsdatum: Mapped[date]
    """Geburtsdatum des Mitglieds."""

    telefonnummer: Mapped[str] = mapped_column(unique=True)
    """Telefonnummer des Mitglieds."""

    geschlecht: Mapped[Geschlecht | None]
    """Das optionale Geschlecht."""

    mitgliedsstatus: Mapped[Mitgliedsstatus | None]
    """Der optionale Mitgliedsstatus."""

    interessen: InitVar[list[Interesse] | None] = None
    """Die transistente Liste mit Interessen als Enum-Werte."""

    beitrittsdatum: Mapped[date]
    """Das Beitrittsdatum des Mitglieds."""

    ausweis: Mapped[Ausweis | None] = relationship(
        back_populates="mitglied",
        innerjoin=True,
        cascade="save-update, delete",
    )
    """Die in eienr 1:1 Beziehung referenzierte Ausweis."""

    ausleihen: Mapped[list[Ausleihe]] = relationship(
        back_populates="mitglied",
        cascade="save-update, delete",
    )
    """Die in einer 1:N Beziehung referenzierten Ausleihen."""

    interessen_json: Mapped[list[str] | None] = mapped_column(
        JSON, name="interessen", init=False
    )
    """Die persistente Liste mit Interessen als JSON-Array."""

    version: Mapped[int] = mapped_column(nullable=False, default=0)
    """Die Versionsnummer für optimistische Synchronisation."""

    erzeugt: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
        default=None,
    )
    """Der Zeitstempel für das initiale INSERT in die DB-Tabelle."""

    aktualisiert: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now(),
        default=None,
    )
    """Der Zeitstempel vom letzen UPDATE in der DB-Tabelle."""

    __mapper_args__: dict[str, MappedColumn[Any]] = {"version_id_col": version}

    def __post_init__(
        self,
        interessen: list[Interesse] | None,
    ) -> None:
        """Für SQLAlchemy: JSON-Array für DB-Spalte setzen für INSERT oder UPDATE.

        :param interessen: Liste mit Interessen als Enum
        """
        logger.debug("interessen={}", interessen)
        logger.debug("self={}", self)
        self.interessen_json = (
            [interesse_enum.name for interesse_enum in interessen]
            if interessen is not None
            else None
        )
        logger.debug("self.interessen_json={}", self.interessen_json)

    @reconstructor
    def on_load(self) -> None:
        """Auslesen aus der DB: die Enum-Liste durch die DB-Strings initialisieren."""
        self.interessen = (  # pyright: ignore[reportAttributeAccessIssue]
            [Interesse[interesse_name] for interesse_name in self.interessen_json]
            if self.interessen_json is not None
            else []
        )
        logger.debug(
            "interessen={}",
            self.interessen,  # pyright: ignore[reportAttributeAccessIssue]
        )

    def set(self, mitglied: Self) -> None:
        """Primitive Attributwerte überschreiben, z.B. vor DB-Update.

        :param mitglied: mitglied-Objekt mit den aktuellen Daten
        """
        self.vorname: str = mitglied.vorname
        self.nachname: str = mitglied.nachname
        self.email: str = mitglied.email
        self.geburtsdatum: date = mitglied.geburtsdatum
        self.telefonnummer: str = mitglied.telefonnummer
        self.beitrittsdatum: date = mitglied.beitrittsdatum

    def __eq__(self, other: Any) -> bool:
        """Vergleich auf Gleicheit, ohne Joins zu verursachen."""
        # Vergleich der Referenzen: id(self) == id(other)
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False
        return self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        """Hash-Funktion anhand der ID, ohne Joins zu verursachen."""
        return hash(self.id) if self.id is not None else hash(type(self))

    def __repr__(self) -> str:
        """Ausgabe eines Mitglieds als String, ohne Joins zu verursachen."""
        return (
            f"Mitglied(id={self.id}, "
            + f"vorname={self.vorname}, "
            + f"nachname={self.nachname}, "
            + f"email={self.email}, "
            + f"geburtsdatum={self.geburtsdatum}, "
            + f"telefonnummer={self.telefonnummer}, "
            + f"beitrittsdatum={self.beitrittsdatum}, "
            + f"geschlecht={self.geschlecht}, "
            + f"mitgliedsstatus={self.mitgliedsstatus}, "
            + f"interessen={self.interessen}, "
            + f"version={self.version}, "
            + f"erzeugt={self.erzeugt}, "
            + f"aktualisiert={self.aktualisiert})"
        )
