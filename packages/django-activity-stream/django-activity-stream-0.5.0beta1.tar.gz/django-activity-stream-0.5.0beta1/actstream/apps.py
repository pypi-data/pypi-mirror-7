from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_text

try:
    from django.apps import AppConfig
except ImportError:
    AppConfig = object

try:
    from django.db.backends.mysql.base import DatabaseOperations
except (ImportError, ImproperlyConfigured):
    DatabaseOperations = None


from actstream import settings


def fixed_last_executed_query(self, cursor, sql, params):
    """
    Patches error with MySQL + Django<=1.5: https://code.djangoproject.com/ticket/19954
    """
    return force_text(cursor._last_executed, errors='replace')


class ActstreamConfig(AppConfig):
    name = 'actstream'

    def ready(self):
        from actstream.signals import action
        from actstream.actions import action_handler

        action.connect(action_handler, dispatch_uid='actstream.models')

        if hasattr(self, 'get_model'):
            action_class = self.get_model('action')
        else:
            from actstream.models import Action as action_class

        if settings.USE_JSONFIELD:
            try:
                from jsonfield.fields import JSONField
            except ImportError:
                raise ImproperlyConfigured('You must have django-jsonfield installed '
                                           'if you wish to use a JSONField on your actions')
            JSONField(blank=True, null=True).contribute_to_class(action_class, 'data')

        if DatabaseOperations:
            DatabaseOperations.last_executed_query = fixed_last_executed_query
