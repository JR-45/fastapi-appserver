"""Pydantic-Model für die Ausleihen."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from mitglied.entity import Ausleihe

__all__ = ["AusleiheModel"]


class AusleiheModel(BaseModel):
    """Pydantic-Model für die Ausleihe."""

    ausleihdatum: date
    """Das Ausleihdatum."""
    rueckgabedatum: date
    """Das Rückgabedatum."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        json_schema_extra={
            "example": {
                "ausleihdatum": "2023-01-31",
                "rueckgabedatum": "2023-01-31",
            },
        }
    )

    def to_ausleihe(self) -> Ausleihe:
        """Konvertierung in ein Ausleihe-Objekt für SQLAlchemy.

        :return: Ausleihe-Objekt für SQLAlchemy
        :rtype: Ausleihe
        """
        # Model von Pydantic in ein Dictionary konvertieren
        ausleihe_dict = self.model_dump()
        ausleihe_dict["id"] = None
        ausleihe_dict["mitglied_id"] = None
        ausleihe_dict["mitglied"] = None

        return Ausleihe(**ausleihe_dict)
