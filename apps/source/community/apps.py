from django.apps import AppConfig
from economy.util import AppEventManager
from .events import register_events, register_functions


class CommunityConfig(AppConfig):
    dependencies = []
    name = 'apps.source.community'
    event_manager = AppEventManager()

    def ready(self):
        register_events(self.event_manager)
        register_functions(self.event_manager)
