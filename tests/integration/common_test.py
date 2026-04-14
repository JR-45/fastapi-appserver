# ruff: noqa: S101, D103
# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Allgemeine Daten für die Tests."""

from http import HTTPStatus
from pathlib import Path
from ssl import create_default_context
from typing import Final

from httpx import post

__all__ = [
    "base_url",
    "ctx",
    "db_populate",
    "login",
    "rest_path",
    "rest_url",
    "timeout",
    "token_path",
    "username_admin",
]

schema: Final = "https"
port: Final = 8000
host: Final = "127.0.0.1"
base_url: Final = f"{schema}://{host}:{port}"
rest_path: Final = "/rest"
rest_url: Final = f"{base_url}{rest_path}"
token_path: Final = "/auth/token"  # noqa: S105
username_admin: Final = "admin"
password_admin: Final = "p"  # noqa: S105  # NOSONAR
timeout: Final = 2
certificate: Final = str(Path("tests") / "integration" / "certificate.crt")
ctx = create_default_context(cafile=certificate)


def login(
    username: str = username_admin,
    password: str = password_admin,  # NOSONAR
) -> str:
    login_data: Final = {"username": username, "password": password}
    response: Final = post(
        f"{base_url}{token_path}",
        json=login_data,
        verify=ctx,
        timeout=timeout,
    )
    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(f"login() mit Statuscode {response.status_code}")
    response_body: Final = response.json()
    token: Final = response_body.get("token")
    if token is None or not isinstance(token, str):
        raise RuntimeError(f"login() mit ungueltigem Token: type={type(token)}")
    return token


def db_populate() -> None:
    # In fastapi-appserver wird die DB beim Starten in lifespan() neu geladen
    # Wenn es einen dedizierten Endpunkt gibt, kann er hier aufgerufen werden.
    # Da lifespan es bereits tut, lassen wir es vorerst leer oder rufen den Service direkt auf falls moeglich.
    pass
