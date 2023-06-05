import discord
from discord.ext import commands
from asgiref.sync import sync_to_async

from apps.source.discord.models import Guild


def sync_bot_guilds_with_db(bot: commands.Bot):
    guild_objects_in_db = Guild.objects.all()
    for db_guild in guild_objects_in_db:
        if bot.get_guild(int(db_guild.id)):
            continue
        db_guild.active=False
        db_guild.save()

    guilds_synced = 0
    for guild in bot.guilds:
        guild_in_db_filter = guild_objects_in_db.filter(id=guild.id)
        if len(guild_in_db_filter) > 0:
            guild_in_db_filter = guild_in_db_filter[0]
            guild_in_db_filter.name = guild.name
            guild_in_db_filter.active = True
            guild_in_db_filter.save()
            continue
        Guild.objects.create(id=guild.id, name=guild.name, active=True)
        guilds_synced += 1

    return guilds_synced

def remove_inactive_guilds():
    guild_objects_in_db = Guild.objects.all()
    guilds_removed = 0
    for db_guild in guild_objects_in_db:
        if db_guild.active == False:
            db_guild.delete()
            guilds_removed += 1
    return guilds_removed

class DiscordDBCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name='db_sync', description='Syncs discord related information with the database.')
    @discord.app_commands.default_permissions(administrator=True)
    async def db_sync(self, interaction: discord.Interaction):
        await interaction.response.send_message('Syncing discord information with the database...')
        guilds_synced = await sync_to_async(sync_bot_guilds_with_db)(self.bot)
        await interaction.followup.send(f'Done! `{guilds_synced}` guild{"" if guilds_synced == 1 else "s"} synced.')

    @discord.app_commands.command(name='db_remove_inactive_guilds', description='Removes inactive guilds from the database.')
    @discord.app_commands.default_permissions(administrator=True)
    async def db_remove_inactive_guilds(self, interaction: discord.Interaction):
        await interaction.response.send_message('Removing inactive guilds from the database...')
        guilds_removed = await sync_to_async(remove_inactive_guilds)()
        await interaction.followup.send(f'Done! `{guilds_removed}` guild{"" if guilds_removed == 1 else "s"} removed.')

async def setup(bot: commands.Bot):
    await bot.add_cog(DiscordDBCog(bot))
