from django.apps import AppConfig


class DiscordConfig(AppConfig):
    name = 'apps.source.discord'

    def ready(self):
        from . import urls
        self.urlpatterns = urls.urlpatterns
