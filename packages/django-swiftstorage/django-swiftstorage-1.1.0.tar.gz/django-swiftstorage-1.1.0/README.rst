django-swiftstorage
===================

Provides a custom storage system for Django to store and retrieve files
in OpenStack Swift.

Configuration
=============

::

    DEFAULT_FILE_STORAGE = "swiftstorage.storage.SwiftStorage"

    OS_USERNAME = "<openstack username>"
    OS_PASSWORD = "<openstack password>"
    OS_AUTH_URL = "<openstack keystone authenticator URL>"
    OS_REGION_NAME = "<openstack region name>"
    OS_TENANT_NAME = "<openstack tenant name>"

    SWIFT_CONTAINER_NAME = # Created if does not exist.

Testing
=======

Tests can be run with ``python setup.py test``. To make things easier,
use ``tox``.

``tox`` can be installed with ``pip`` or via the ``python-tox`` package
for Debian/Ubuntu.

Then simply call ``tox`` to run the tests in a virtual environment.
