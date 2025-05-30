================================
How to regenerate the ER diagram
================================

In the docs there is an autogenerated ER diagram showing the Django models as
SQL tables, relations and fields. Whenever tables, fields and relations are
added, changed or removed this diagram should be regenerated.

Get dependencies
================

You need to have installed the development dependencies to regenerate the diagram::

    pip install argus-server[dev]

This will install ``django_extensions`` which has the diagram generator we use.

Test by making a .dot-file
==========================

To test if everything is installed correctly, run::

    python manage.py graph_models argus_auth argus_incident argus_notificationprofile \
    --group-models -X Permission,AbstractUser,AbstractBaseUser,PermissionsMixin

This will dump a `.dot-file <https://graphviz.org/doc/info/lang.html>`_, the
textual representation of the graph, to standard out.

Generate PNG
============

In order to generate a PNG there are two methods:

1. Generate via the ``graph_models`` command and one more dependency
2. Use ``graphviz`` directly on a .dot-file

Generate via the ``graph_models`` command
-----------------------------------------

We need to have one more dependency installed: one of ``pygraphviz`` or
``pydotplus``. If one cannot be installed via pip, try the other.

To generate the final PNG in the correct location, run::

    python manage.py graph_models argus_auth argus_incident argus_notificationprofile \
    --group-models -X Permission,AbstractUser,AbstractBaseUser,PermissionsMixin \
    -o docs/reference/img/ER_model.png

Use ``graphviz`` directly on a .dot-file
----------------------------------------

1. Make sure you have graphviz installed, how is OS/distro dependent
2. Generate the dot-file with::

    python manage.py graph_models argus_auth argus_incident argus_notificationprofile \
    --group-models -X Permission,AbstractUser,AbstractBaseUser,PermissionsMixin \
    -o ER_model.dot
3. Generate the PNG with ``dot``::

    dot -T png -o docs/reference/img/ER_model.png ER_model.dot
4. You can now delete ``ER_model.dot``

Commit!
=======

Commit the new image with a message like "Sync the ER diagram to current
database schema".
