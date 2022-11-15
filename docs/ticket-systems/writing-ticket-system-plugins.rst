.. _writing-ticket-system-plugins:

Writing your own ticket system plugin
=====================================

To write your own ticket system plugin it is easiest to use a Python library
that accesses the API offered by the desired ticket system.

The plugin class inherits from the class ``TicketPlugin`` and needs to implement
the following methods:

.. autoclass:: argus.incident.ticket.base.TicketPlugin
   :members:

The method ``create_ticket`` calls ``import_settings`` and ``create_client``
and using the library creates a ticket within the desired ticket system and
returns its url. This method is called within Argus when a user wants to create
a ticket.
