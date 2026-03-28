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

"""Entity-Klasse für Ausleihe."""

from datetime import date

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitglied.entity.base import Base


class Ausleihe(Base):
    """Entity-Klasse für Ausleihe."""

    __tablename__ = "ausleihe"

    id: Mapped[int] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID gemäß der zugehörigen IDENTITY-Spalte."""

    ausleihdatum: Mapped[date]
    """Das Datum der Ausleihe."""

    rueckgabedatum: Mapped[date]
    """Das Datum der Rückgabe."""

    mitglied_id: Mapped[int] = mapped_column(ForeignKey("mitglied.id"))
    """ID des zugehörigen Mitglieds als Fremdschlüssel in der DB-Tabelle."""

    mitglied: Mapped[Mitglied] = relationship(  # noqa: F821 # ty: ignore[unresolved-reference] # pyright: ignore[reportUndefinedVariable ]
        back_populates="ausleihen",
    )
    """Das zugehörige transiente Mitglied-Objekt."""

    # __repr__ fuer Entwickler/innen, __str__ fuer User
    def __repr__(self) -> str:
        """Ausgabe der Ausleihe als String ohne die Mitgliedsdaten."""
        return (
            f"Ausleihe(id={self.id}, ausleihdatum={self.ausleihdatum}, "
            + f"rueckgabedatum={self.rueckgabedatum})"
        )
