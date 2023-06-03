from django.core.management.base import BaseCommand, CommandParser
from apps.source.discord.models import Client
from apps.source.discord.client import DiscordClient


class Command(BaseCommand):
    help = "Starts the discord bot"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('client_id', type=int)
        parser.add_argument('--sync', action='store_true', help='Syncs slash commands')
        parser.add_argument('--sync-global', action='store_true', help='Syncs slash commands globally')
    
    def handle(self, *args, **options):
        client_model = Client.objects.get(id=options['client_id'])
        client = DiscordClient(client_model)
        sync_on_start, sync_global_on_start = False, False
        if options['sync']:
            sync_on_start = True
        if options['sync_global']:
            sync_global_on_start = True
        self.stdout.write(self.style.SUCCESS('Discord bot starting'))
        client.run(sync_on_start=sync_on_start, sync_global_on_start=sync_global_on_start)

if __name__ == "__main__":
    Command().handle()
