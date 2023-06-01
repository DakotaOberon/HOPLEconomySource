from django.apps import AppConfig


class DiscordConfig(AppConfig):
    dependencies = ['apps.source.community', 'apps.source.bank']
    name = 'apps.source.discord'

    def ready(self):
        from . import urls
        self.urlpatterns = urls.urlpatterns
