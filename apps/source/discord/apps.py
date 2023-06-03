from django.apps import AppConfig
from economy.util import AppEventManager
from .events import register_events, register_functions


class DiscordConfig(AppConfig):
    dependencies = ['apps.source.community', 'apps.source.bank']
    name = 'apps.source.discord'
    event_manager = AppEventManager()

    def ready(self):
        from . import urls
        self.urlpatterns = urls.urlpatterns

        register_events(self.event_manager)
        register_functions(self.event_manager)
