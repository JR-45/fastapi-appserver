"""Schema für GraphQL durch Strawberry."""

from collections.abc import Sequence
from typing import Final

import strawberry
from loguru import logger
from strawberry.fastapi import GraphQLRouter

from mitglied.graphql_api.graphql_types import (
    CreatePayload,
    MitgliedInput,
    MitgliedType,
)
from mitglied.repository.mitglied_repository import MitgliedRepository
from mitglied.repository.pageable import Pageable
from mitglied.repository.session_factory import Session
from mitglied.router.ausweis_model import AusweisModel
from mitglied.router.mitglied_model import MitgliedModel
from mitglied.service.mitglied_write_service import MitgliedWriteService

__all__ = ["graphql_router"]

_repo: Final = MitgliedRepository()
_write_service: Final = MitgliedWriteService(repo=_repo)


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
            return MitgliedType.from_entity(m)

    @strawberry.field
    def mitglieder(self) -> Sequence[MitgliedType]:
        """Alle Mitglieder suchen."""
        logger.debug("mitglieder")
        with Session() as session:
            pageable = Pageable(size=0, number=0)
            result = _repo.find_all(pageable=pageable, session=session)
            return [MitgliedType.from_entity(m) for m in result.content]


@strawberry.type
class Mutation:
    """Mutations für Mitgliedsdaten."""

    @strawberry.mutation
    def create(self, mitglied_input: MitgliedInput) -> CreatePayload:
        """Neues Mitglied anlegen."""
        logger.debug("mitglied_input={}", mitglied_input)

        ausweis_model = None
        if mitglied_input.ausweis:
            ausweis_model = AusweisModel(
                ausstellungsdatum=mitglied_input.ausweis.ausstellungsdatum,
                ablaufdatum=mitglied_input.ausweis.ablaufdatum,
            )

        mitglied_model = MitgliedModel(
            vorname=mitglied_input.vorname,
            nachname=mitglied_input.nachname,
            email=mitglied_input.email,
            geburtsdatum=mitglied_input.geburtsdatum,
            telefonnummer=mitglied_input.telefonnummer,
            beitrittsdatum=mitglied_input.beitrittsdatum,
            geschlecht=mitglied_input.geschlecht,
            mitgliedsstatus=mitglied_input.mitgliedsstatus,
            interessen=mitglied_input.interessen or [],
            ausweis=ausweis_model,
            ausleihen=[],
        )

        mitglied_dto = _write_service.create(mitglied=mitglied_model.to_mitglied())
        return CreatePayload(id=mitglied_dto.id)


schema: Final = strawberry.Schema(query=Query, mutation=Mutation)

graphql_router: Final = GraphQLRouter(schema)
