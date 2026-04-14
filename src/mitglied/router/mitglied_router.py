"""MitgliedRouter."""

from dataclasses import asdict
from typing import Annotated, Any, Final

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from loguru import logger

from mitglied.repository import Pageable, Slice
from mitglied.router.dependencies import get_service
from mitglied.router.page import Page
from mitglied.security.role import Role
from mitglied.security.roles_required import RolesRequired
from mitglied.service import MitgliedDTO, MitgliedService

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
    mitglied_id: int,
    service: Annotated[MitgliedService, Depends(get_service)],
) -> dict:
    """Suche mit der Mitglied-ID."""
    logger.debug("mitglied_id={}", mitglied_id)
    mitglied = service.find_by_id(mitglied_id=mitglied_id)
    return {"mitglied": mitglied}


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
    mitglied_dict.update({
        "geburtsdatum": mitglied.geburtsdatum.isoformat(),
        "beitrittsdatum": mitglied.beitrittsdatum.isoformat(),
    })
    return mitglied_dict
