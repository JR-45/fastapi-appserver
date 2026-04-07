"""Pydantic-Model für den Ausweis."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from mitglied.entity import Ausweis

__all__ = ["AusweisModel"]


class AusweisModel(BaseModel):
    """Pydantic-Model für die Ausweisdaten."""

    ausstellungsdatum: date
    """Ausstellungsdatum"""
    ablaufdatum: date
    """Ablaufdatum"""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        json_schema_extra={
            "example": {
                "ausstellungsdatum": "2023-01-31",
                "ablaufdatum": "2023-01-31",
            },
        }
    )

    def to_ausweis(self) -> Ausweis:
        """Konvertierung in ein Ausweis-Objekt für SQLAlchemy.

        :return: Ausweis-Objekt für SQLAlchemy
        :rtype: Ausweis
        """
        # Model von Pydantic in ein Dictionary konvertieren
        ausweis_dict = self.model_dump()
        ausweis_dict["id"] = None
        ausweis_dict["mitglied_id"] = None
        ausweis_dict["mitglied"] = None

        return Ausweis(**ausweis_dict)
