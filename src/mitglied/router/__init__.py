"""Modul für die REST-Schnittstelle."""

from collections.abc import Sequence

from mitglied.router.mitglied_router import get, get_by_id
from mitglied.router.mitglied_router import router as mitglied_router
from mitglied.router.mitglied_write_router import mitglied_write_router, post

__all__: Sequence[str] = [
    "get",
    "get_by_id",
    "mitglied_router",
    "mitglied_write_router",
    "post",
]
