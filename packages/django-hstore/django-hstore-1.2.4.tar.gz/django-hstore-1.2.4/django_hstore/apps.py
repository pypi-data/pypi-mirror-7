import sys

import django
from django.conf import settings
from django.db.backends.signals import connection_created

try:
    from django.apps import AppConfig
except ImportError:
    AppConfig = object

from .utils import register_hstore


class ConnectionCreateHandler(object):
    """
    Generic connection handlers manager.
    Executes attached functions when connection is created.
    With possibility of attaching single execution methods.
    """

    generic_handlers = []
    unique_handlers = []

    def __call__(self, sender, connection, **kwargs):
        handlers = set()

        if len(self.unique_handlers) > 0:
            handlers.update(self.unique_handlers)
            self.unique_handlers = []

        handlers.update(self.generic_handlers)

        # List comprehension is used instead of for statement
        # only for performance.
        [x(connection) for x in handlers]

    def attach_handler(self, func, vendor=None, unique=False):
        if unique:
            self.unique_handlers.append(func)
        else:
            self.generic_handlers.append(func)

connection_handler = ConnectionCreateHandler()


def register_hstore_handler(connection, **kwargs):
    # do not register hstore if DB is not postgres
    # do not register if HAS_HSTORE flag is set to false

    if connection.vendor != 'postgresql' or \
       connection.settings_dict.get('HAS_HSTORE', True) is False:
        return

    # if the ``NAME`` of the database in the connection settings is ``None``
    # defer hstore registration by setting up a new unique handler
    if connection.settings_dict['NAME'] is None:
        connection_handler.attach_handler(register_hstore_handler,
                                          vendor="postgresql", unique=True)
        return

    if sys.version_info[0] < 3:
        register_hstore(connection.connection, globally=True, unicode=True)
    else:
        register_hstore(connection.connection, globally=True)


# This allows users that introduce hstore to an existing
# production environment to set global registry to false for avoid
# strange behaviors when having hstore installed individually
# on each database instead of on template1.
HSTORE_GLOBAL_REGISTER = getattr(settings, "DJANGO_HSTORE_GLOBAL_REGISTER", True)

connection_handler.attach_handler(register_hstore_handler,
                                  vendor="postgresql", unique=HSTORE_GLOBAL_REGISTER)


class HStoreConfig(AppConfig):
    name = 'django_hstore'
    verbose = 'Django HStore'

    def ready(self):
        connection_created.connect(connection_handler,
                                   dispatch_uid="_connection_create_handler")

if django.get_version() < '1.7':
    HStoreConfig().ready()
