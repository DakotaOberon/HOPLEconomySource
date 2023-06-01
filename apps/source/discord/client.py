import discord
from discord.ext import commands

from .models import Client
from .settings import COMMAND_EXTENSIONS, TEST_SERVER_ID


class DiscordClient(commands.Bot):
    def __init__(self, client_model: Client, *args, **kwargs):
        self.synced, self.global_synced = True, True
        self.client_model = client_model
        intents = discord.Intents.default()
        intents.presences = client_model.presence_intent
        intents.members = client_model.server_members_intent
        intents.message_content = client_model.message_content_intent
        super().__init__(intents=intents, command_prefix=self.client_model.command_prefix, *args, **kwargs)

    async def sync(self):
        local_guild = discord.Object(id=TEST_SERVER_ID)
        self.tree.copy_global_to(guild=local_guild)
        await self.tree.sync(guild=local_guild)

    async def sync_global(self):
        await self.tree.sync()

    async def setup_hook(self):
        await self.load_slash_commands()

        if not self.synced:
            await self.sync()
            self.synced = True
        if not self.global_synced:
            await self.sync_global()
            self.global_synced = True

    async def load_slash_commands(self):
        for extension_path in COMMAND_EXTENSIONS:
            print('Loading extension:', extension_path)
            await self.load_extension(extension_path)

    async def reload_slash_commands(self):
        for extension_path in COMMAND_EXTENSIONS:
            await self.reload_extension(extension_path)

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    def run(self, sync_on_start=False, sync_global_on_start=False, **kwargs):
        self.synced = not sync_on_start
        self.global_synced = not sync_global_on_start
        super().run(self.client_model.token, **kwargs)
