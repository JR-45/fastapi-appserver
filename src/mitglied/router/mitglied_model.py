"""Pydantic-Model für die Mitgliedsdaten."""

from typing import Final

from loguru import logger

from mitglied.entity import Mitglied
from mitglied.entity.interesse import Interesse
from mitglied.router.ausleihe_model import AusleiheModel
from mitglied.router.ausweis_model import AusweisModel
from mitglied.router.mitglied_update_model import MitgliedUpdateModel

__all__ = ["MitgliedModel"]


class MitgliedModel(MitgliedUpdateModel):
    """Pydantic-Model für die Mitgliedsdaten."""

    ausweis: AusweisModel | None
    """Die zugehörige Ausweisdaten."""
    ausleihen: list[AusleiheModel]
    """Die Liste der Ausleihvorgänge."""
    interessen: list[Interesse]
    """Die Liste mit Interessen als Enum-Werte."""

    def to_mitglied(self) -> Mitglied:
        """Konvertierung in ein Mitglied-Objekt für SQLAlchemy.

        :return: Mitglied-Objekt für SQLAlchemy
        :rtype: Mitglied
        """
        logger.debug("self={}", self)
        mitglied_dict = self.to_dict()
        mitglied_dict["interessen"] = self.interessen

        mitglied: Final = Mitglied(**mitglied_dict)
        mitglied.ausweis = self.ausweis.to_ausweis() if self.ausweis else None
        mitglied.ausleihen = [
            ausleihe_model.to_ausleihe() for ausleihe_model in self.ausleihen
        ]
        logger.debug("mitglied={}", mitglied)
        return mitglied
