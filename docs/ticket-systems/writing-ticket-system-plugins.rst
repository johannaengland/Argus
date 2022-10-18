.. _writing-ticket-system-plugins:

Writing your own ticket system plugin
=====================================

To write your own ticket system plugin it is easiest to use a Python library
that accesses the API offered by the desired ticket system.

The plugin class inherits from the class ``TicketPlugin`` and needs to implement
the following methods:

.. autoclass:: argus.incident.ticket.base.TicketPlugin
   :members:

The function ``create_ticket`` calls the two previous functions and creates
the desired ticket and returns its url. This function is called within Argus
when a user wants to create a ticket.
