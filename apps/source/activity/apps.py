from django.apps import AppConfig


class BankConfig(AppConfig):
    dependencies = ['apps.source.community', 'apps.source.bank', 'apps.source.discord', 'apps.source.holiday']
    name = 'apps.source.activity'
