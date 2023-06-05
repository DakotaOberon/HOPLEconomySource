import discord
from discord.ext import commands

from apps.source.discord.settings import TEST_SERVER_ID


class DevelopCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name='am_admin', description='Check if you have command admin permissions.')
    @discord.app_commands.default_permissions(administrator=True)
    async def am_admin(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'You are an admin.', ephemeral=True)

    @discord.app_commands.command(name='sync', description='Sync slash commands to the test server.')
    @discord.app_commands.default_permissions(administrator=True)
    async def sync(self, interaction: discord.Interaction):
        locally_synced = await self.bot.tree.copy_global_to(guild=discord.Object(id=TEST_SERVER_ID))
        await interaction.response.send_message(f'`{len(locally_synced)}` slash commands synced `locally`.')

    @discord.app_commands.command(name='sync_global', description='Sync slash commands globally.')
    @discord.app_commands.default_permissions(administrator=True)
    async def sync_global(self, interaction: discord.Interaction):
        globally_synced = await self.bot.tree.sync()
        await interaction.response.send_message(f'`{len(globally_synced)}` slash commands synced `globally`.', ephemeral=True)

    @discord.app_commands.command(name='reload', description='Reload slash command cogs.')
    @discord.app_commands.default_permissions(administrator=True)
    async def reload(self, interaction: discord.Interaction):
        self.bot.reload_slash_commands()
        await interaction.response.send_message(f'Slash commands reloaded.\nPlease re-sync if any new commands were added.', ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(DevelopCog(bot))
