"""Schema für GraphQL durch Strawberry."""

from collections.abc import Sequence
from typing import Final

import strawberry
from loguru import logger
from strawberry.fastapi import GraphQLRouter

from mitglied.graphql_api.graphql_types import MitgliedType
from mitglied.repository.mitglied_repository import MitgliedRepository
from mitglied.repository.pageable import Pageable
from mitglied.repository.session_factory import Session

__all__ = ["graphql_router"]

_repo: Final = MitgliedRepository()


@strawberry.type
class Query:
    """Queries für Mitgliedsdaten."""

    @strawberry.field
    def mitglied(self, mitglied_id: strawberry.ID) -> MitgliedType | None:
        """Mitglied anhand der ID suchen."""
        logger.debug("mitglied_id={}", mitglied_id)
        with Session() as session:
            m = _repo.find_by_id(mitglied_id=int(mitglied_id), session=session)
            if m is None:
                return None
            return MitgliedType(
                id=m.id,
                vorname=m.vorname,
                nachname=m.nachname,
                email=m.email,
                geburtsdatum=m.geburtsdatum,
                telefonnummer=m.telefonnummer,
                beitrittsdatum=m.beitrittsdatum,
                version=m.version,
                erzeugt=m.erzeugt,
                aktualisiert=m.aktualisiert,
            )

    @strawberry.field
    def mitglieder(self) -> Sequence[MitgliedType]:
        """Alle Mitglieder suchen."""
        logger.debug("mitglieder")
        with Session() as session:
            pageable = Pageable(size=0, number=0)
            result = _repo.find_all(pageable=pageable, session=session)
            return [
                MitgliedType(
                    id=m.id,
                    vorname=m.vorname,
                    nachname=m.nachname,
                    email=m.email,
                    geburtsdatum=m.geburtsdatum,
                    telefonnummer=m.telefonnummer,
                    beitrittsdatum=m.beitrittsdatum,
                    version=m.version,
                    erzeugt=m.erzeugt,
                    aktualisiert=m.aktualisiert,
                )
                for m in result.content
            ]


schema: Final = strawberry.Schema(query=Query)

graphql_router: Final = GraphQLRouter(schema)
