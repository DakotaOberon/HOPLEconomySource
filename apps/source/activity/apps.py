from django.apps import AppConfig


class BankConfig(AppConfig):
    dependencies = ['apps.source.community', 'apps.source.bank', 'apps.source.discord']
    name = 'apps.source.activity'
