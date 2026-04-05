"""Modul für die GraphQL-Schnittstelle."""

from mitglied.graphql_api.schema import Query, graphql_router

__all__ = [
    "Query",
    "graphql_router",
]
