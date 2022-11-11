from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .base import created_tickets, TicketPlugin, TicketTestClient

if TYPE_CHECKING:
    from argus.incident.models import Incident

LOG = logging.getLogger(__name__)

__all__ = [
    "DummyPlugin",
]


class DummyPlugin(TicketPlugin):
    """This plugin is exclusively for testing

    Instead of creating tickets it writes the information to a local object
    """

    @classmethod
    def import_settings(cls):
        return None, None, None

    @staticmethod
    def create_client(endpoint, authentication):
        return TicketTestClient()

    @classmethod
    def create_ticket(cls, incident: Incident):
        """Instead of writing a ticket saves information to an object and
        returns a dummy url
        """
        endpoint, authentication, ticket_information = cls.import_settings()

        client = cls.create_client(endpoint=endpoint, authentication=authentication)
        ticket_url = client.create_ticket(
            {
                "title": str(incident),
                "description": incident.description,
            }
        )

        return ticket_url
