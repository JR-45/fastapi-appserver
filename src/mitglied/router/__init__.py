"""Modul für die REST-Schnittstelle."""

from mitglied.router.mitglied_router import router
from mitglied.router.page import Page

__all__ = ["router", "Page"]
