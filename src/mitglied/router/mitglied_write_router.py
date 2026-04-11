"""MitgliedWriteRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import Response
from loguru import logger

from mitglied.problem_details import create_problem_details
from mitglied.router.constants import IF_MATCH, IF_MATCH_MIN_LEN
from mitglied.router.dependencies import get_write_service
from mitglied.router.mitglied_model import MitgliedModel
from mitglied.router.mitglied_update_model import MitgliedUpdateModel
from mitglied.security.role import Role
from mitglied.security.roles_required import RolesRequired
from mitglied.service import MitgliedWriteService

__all__ = ["mitglied_write_router"]


mitglied_write_router: Final = APIRouter(
    tags=["Schreiben"],
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)


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


@mitglied_write_router.put("/{mitglied_id}")
def put(
    mitglied_id: int,
    mitglied_update_model: MitgliedUpdateModel,
    request: Request,
    service: Annotated[MitgliedWriteService, Depends(get_write_service)],
) -> Response:
    """PUT-Request, um einen Mitglied zu aktualisieren.

    :param mitglied_id: ID des zu aktualisierenden Mitglieds als Pfadparameter
    :param mitglied_update_model: Mitgliedsdaten für das Update
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    :raises EmailExistsError: Falls die neue Emailadresse bereits existiert
    :raises NotFoundError: Falls kein Mitglied mit der ID existiert
    :raises VersionOutdatedError: Falls die Version veraltet ist
    """
    if_match_value: Final = request.headers.get(IF_MATCH)
    logger.debug(
        "mitglied_id={}, if_match={}, mitglied_update_model={}",
        mitglied_id,
        if_match_value,
        mitglied_update_model,
    )
    if if_match_value is None:
        return create_problem_details(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
        )

    if (
        len(if_match_value) < IF_MATCH_MIN_LEN
        or not if_match_value.startswith('"')
        or not if_match_value.endswith('"')
    ):
        return create_problem_details(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        )
    version: Final = if_match_value[1:-1]
    try:
        version_int: Final = int(version)
    except ValueError:
        return Response(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        )

    mitglied: Final = mitglied_update_model.to_mitglied()
    mitglied_modified: Final = service.update(
        mitglied=mitglied,
        mitglied_id=mitglied_id,
        version=version_int,
    )
    logger.debug("mitglied_modified={}", mitglied_modified)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": f'"{mitglied_modified.version}"'},
    )
