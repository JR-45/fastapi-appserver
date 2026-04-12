"""MitgliedRouter."""

from dataclasses import asdict
from typing import Annotated, Any, Final

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse, Response
from loguru import logger

from mitglied.repository import Pageable, Slice
from mitglied.router.constants import ETAG, IF_NONE_MATCH, IF_NONE_MATCH_MIN_LEN
from mitglied.router.page import Page
from mitglied.security.role import Role
from mitglied.security.roles_required import RolesRequired
from mitglied.service import MitgliedService, MitgliedDTO
from mitglied.router.dependencies import get_service

router: Final = APIRouter(
    tags=["Mitglieder"],
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.MITGLIED]))],
)


@router.get("")
def get(
    request: Request,
    service: Annotated[MitgliedService, Depends(get_service)],
) -> JSONResponse:
    """Suche mit Query-Parameter.

    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit Query-Parameter
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit einer Seite mit Mitglieds-Daten
    :rtype: Response
    :raises NotFoundError: Falls keine Mitglieder gefunden wurden
    """
    query_params: Final = request.query_params
    log_str: Final = "{}"
    logger.debug(log_str, query_params)

    page: Final = query_params.get("page")
    size: Final = query_params.get("size")
    pageable: Final = Pageable.create(number=page, size=size)

    suchparameter = dict(query_params)
    if "page" in query_params:
        del suchparameter["page"]
    if "size" in query_params:
        del suchparameter["size"]

    mitglied_slice: Final = service.find(suchparameter=suchparameter, pageable=pageable)

    result: Final = _mitglied_slice_to_page(mitglied_slice, pageable)
    logger.debug(log_str, result)
    return JSONResponse(content=result)


@router.get("/{mitglied_id}")
def get_by_id(
    request: Request,
    mitglied_id: int,
    service: Annotated[MitgliedService, Depends(get_service)],
) -> Response:
    """Suche mit der Mitglied-ID."""
    logger.debug("mitglied_id={}", mitglied_id)
    mitglied = service.find_by_id(mitglied_id=mitglied_id)
    if_none_match: Final = request.headers.get(IF_NONE_MATCH)
    if (
        if_none_match is not None
        and len(if_none_match) >= IF_NONE_MATCH_MIN_LEN
        and if_none_match.startswith('"')
        and if_none_match.endswith('"')
    ):
        version = if_none_match[1:-1]
        logger.debug("version={}", version)
        if version is not None:
            try:
                if int(version) == mitglied.version:
                    return Response(status_code=status.HTTP_304_NOT_MODIFIED)
            except ValueError:
                logger.debug("invalid version={}", version)

    return JSONResponse(
        content=_mitglied_to_dict(mitglied),
        headers={ETAG: f'"{mitglied.version}"'},
    )


def _mitglied_slice_to_page(
    mitglied_slice: Slice[MitgliedDTO],
    pageable: Pageable,
) -> dict[str, Any]:
    mitglied_dict: Final = tuple(
        _mitglied_to_dict(mitglied) for mitglied in mitglied_slice.content
    )
    page: Final = Page.create(
        content=mitglied_dict,
        pageable=pageable,
        total_elements=mitglied_slice.total_elements,
    )
    return asdict(obj=page)


def _mitglied_to_dict(mitglied: MitgliedDTO) -> dict[str, Any]:
    mitglied_dict: Final = asdict(obj=mitglied)
    mitglied_dict.pop("version")
    mitglied_dict.update(
        {
            "geburtsdatum": mitglied.geburtsdatum.isoformat(),
            "beitrittsdatum": mitglied.beitrittsdatum.isoformat(),
        }
    )
    return mitglied_dict
