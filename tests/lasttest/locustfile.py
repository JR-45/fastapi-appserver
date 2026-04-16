"""Lasttest mit Locust."""

import os
from typing import Final, Literal

import urllib3
from locust import HttpUser, constant_throughput, task

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GetUser(HttpUser):
    """Lasttest für GET-Requests."""

    wait_time = constant_throughput(0.1)

    def on_start(self) -> None:
        """Token holen."""
        self.client.verify = False
        response: Final = self.client.post(
            url="/auth/token",
            json={
                "username": os.getenv("LOCUST_USERNAME", "admin"),
                "password": os.getenv("LOCUST_PASSWORD"),
            },
        )
        body: Final[dict[Literal["token"], str]] = response.json()
        token: Final = body["token"]
        self.client.headers = {"Authorization": f"Bearer {token}"}

    @task(100)
    def get_by_id(self) -> None:
        """GET-Requests mit ID."""
        for mitglied_id in [1, 20, 30, 40, 50, 60]:
            self.client.get(f"/rest/{mitglied_id}")

    @task(200)
    def get_alle(self) -> None:
        """GET-Requests alle Mitglieder."""
        self.client.get("/rest")
