"""Pydantic-Model zum Aktualisieren von Mitgliedsdaten."""

from datetime import date
from typing import Annotated, Any

from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints

from mitglied.entity import Mitglied
from mitglied.entity.geschlecht import Geschlecht
from mitglied.entity.mitgliedsstatus import Mitgliedsstatus

__all__ = ["MitgliedUpdateModel"]


class MitgliedUpdateModel(BaseModel):
    """Pydantic-Model zum Aktualisieren von Mitgliedsdaten."""

    vorname: Annotated[
        str,
        StringConstraints(
            pattern="^[A-ZÄÖÜ][a-zäöüß]+(-[A-ZÄÖÜ][a-zäöüß])?$",
            max_length=64,
        ),
    ]
    """Der Vorname."""
    nachname: Annotated[
        str,
        StringConstraints(
            pattern="^[A-ZÄÖÜ][a-zäöüß]+(-[A-ZÄÖÜ][a-zäöüß])?$",
            max_length=64,
        ),
    ]
    """Der Nachname."""
    email: EmailStr
    """Die eindeutige Emailadresse."""
    geburtsdatum: date
    """Das Geburtsdatum."""
    telefonnummer: str
    """Die Telefonnummer."""
    geschlecht: Geschlecht | None = None
    """Das optionale Geschlecht."""
    mitgliedsstatus: Mitgliedsstatus | None = None
    """Der optionale Mitgliedsstatus."""
    beitrittsdatum: date
    """Das Beitrittsdatum."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        json_schema_extra={
            "example": {
                "vorname": "Test",
                "nachname": "Test",
                "email": "test@acme.com",
                "geburtsdatum": "2023-01-31",
                "telefonnummer": "123456789",
                "geschlecht": "W",
                "mitgliedsstatus": "A",
                "beitrittsdatum": "2023-01-31",
            },
        }
    )

    def to_dict(self) -> dict[str, Any]:
        """Konvertierung der primitiven Attribute in ein Dictionary.

        :return: Dictionary mit den primitiven Mitglied-Attributen
        :rtype: dict[str, Any]
        """
        # Model von Pydantic in ein Dictionary konvertieren
        # https://docs.pydantic.dev/latest/concepts/serialization
        mitglied_dict = self.model_dump()
        mitglied_dict["id"] = None
        mitglied_dict["ausweis"] = None
        mitglied_dict["ausleihen"] = []
        mitglied_dict["interessen"] = []
        mitglied_dict["erzeugt"] = None
        mitglied_dict["aktualisiert"] = None

        return mitglied_dict

    def to_mitglied(self) -> Mitglied:
        """Konvertierung in ein Mitglied-Objekt für SQLAlchemy.

        :return: Mitglied-Objekt für SQLAlchemy
        :rtype: Mitglied
        """
        logger.debug("self={}", self)
        # Model von Pydantic in ein Dictionary konvertieren
        mitglied_dict = self.to_dict()

        # double star operator = double asterisk operator:
        # Dictionary auspacken als Schluessel-Wert-Paare
        # -> Namen der Schluessel = Namen der Funktionsargumente
        mitglied = Mitglied(**mitglied_dict)
        logger.debug("mitglied={}", mitglied)
        return mitglied
