from django.apps import AppConfig


class BankConfig(AppConfig):
    dependencies = ['apps.source.community']
    name = 'apps.source.bank'
