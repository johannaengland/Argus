from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .base import TicketPlugin

if TYPE_CHECKING:
    from argus.incident.models import Incident

LOG = logging.getLogger(__name__)

__all__ = [
    "DummyPlugin",
]

created_tickets = []


def empty_created_tickets():
    global created_tickets
    created_tickets = []


class TicketTestClient:
    def __init__(self, endpoint, authentication):
        self.authentication = authentication
        self.endpoint = endpoint

    def create(self, *args, **kwargs):
        global created_tickets
        created_tickets.append((*args, kwargs))

        return self.endpoint


class DummyPlugin(TicketPlugin):
    """This plugin is exclusively for testing

    Instead of creating tickets it writes the information to a local object
    """

    @classmethod
    def import_settings(cls):
        return "www.example.com", None, None

    @staticmethod
    def create_client(endpoint, authentication):
        return TicketTestClient(endpoint, authentication)

    @classmethod
    def create_ticket(cls, incident: Incident):
        """Instead of writing a ticket saves information to an object and
        returns a dummy url
        """
        endpoint, authentication, ticket_information = cls.import_settings()

        client = cls.create_client(endpoint=endpoint, authentication=authentication)
        ticket_url = client.create(
            {
                "title": str(incident),
                "description": incident.description,
            }
        )

        return ticket_url
