from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .base import created_tickets, TicketPlugin

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

    @staticmethod
    def create_client(endpoint, authentication):
        return None

    @classmethod
    def create_ticket(cls, incident: Incident):
        """Instead of writing a ticket saves information to an object and
        returns a dummy url
        """
        created_tickets.append(
            {
                "title": str(incident),
                "description": incident.description,
            }
        )

        return "www.example.com"
