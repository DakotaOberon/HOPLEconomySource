import discord
from discord.ext import commands

from apps.source.discord.settings import TEST_SERVER_ID, ADMIN_ROLE_ID


class DevelopCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def confirm_user_is_admin(self, user: discord.Member):
        if (ADMIN_ROLE_ID is None) or (ADMIN_ROLE_ID == ''):
            return True
        return user.get_role(int(ADMIN_ROLE_ID)) is not None

    async def respond_no_permission(self, interaction):
        await interaction.response.send_message(f'You do not have permission to use this command.', ephemeral=True)

    @discord.app_commands.command(name='am_admin', description='Check if you have command admin permissions.')
    async def am_admin(self, interaction: discord.Interaction):
        if (not self.confirm_user_is_admin(interaction.user)):
            return await self.respond_no_permission(interaction)
        await interaction.response.send_message(f'You are an admin.', ephemeral=True)

    @discord.app_commands.command(name='sync', description='Sync slash commands to the test server.')
    async def sync(self, interaction: discord.Interaction):
        if (not self.confirm_user_is_admin(interaction.user)):
            return await self.respond_no_permission(interaction)
        locally_synced = await self.bot.tree.copy_global_to(guild=discord.Object(id=TEST_SERVER_ID))
        await interaction.response.send_message(f'`{len(locally_synced)}` slash commands synced `locally`.')

    @discord.app_commands.command(name='sync_global', description='Sync slash commands globally.')
    async def sync_global(self, interaction: discord.Interaction):
        if (not self.confirm_user_is_admin(interaction.user)):
            return await self.respond_no_permission(interaction)
        globally_synced = await self.bot.tree.sync()
        await interaction.response.send_message(f'`{len(globally_synced)}` slash commands synced `globally`.', ephemeral=True)

    @discord.app_commands.command(name='reload', description='Reload slash command cogs.')
    async def reload(self, interaction: discord.Interaction):
        if (not self.confirm_user_is_admin(interaction.user)):
            return self.respond_no_permission(interaction)
        self.bot.reload_slash_commands()
        await interaction.response.send_message(f'Slash commands reloaded.\nPlease re-sync if any new commands were added.', ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(DevelopCog(bot))
