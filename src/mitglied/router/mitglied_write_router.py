"""MitgliedWriteRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import Response
from loguru import logger

from mitglied.router.dependencies import get_write_service
from mitglied.router.mitglied_model import MitgliedModel
from mitglied.service import MitgliedWriteService

__all__ = ["mitglied_write_router"]


mitglied_write_router: Final = APIRouter(tags=["Schreiben"])


@mitglied_write_router.post("")
def post(
    mitglied_model: MitgliedModel,
    request: Request,
    service: Annotated[MitgliedWriteService, Depends(get_write_service)],
) -> Response:
    """POST-Request, um einen neuen Mitglied anzulegen.

    :param mitglied_model: Mitgliedsdaten als Pydantic-Model
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit der Request-URL
    :param service: Injizierter Service für Geschäftslogik
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die Emailadresse bereits existiert
    """
    logger.debug("mitglied_model={}", mitglied_model)
    mitglied_dto: Final = service.create(mitglied=mitglied_model.to_mitglied())
    logger.debug("mitglied_dto={}", mitglied_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{mitglied_dto.id}"},
    )
