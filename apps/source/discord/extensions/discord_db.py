import discord
from discord.ext import commands
from asgiref.sync import sync_to_async

from apps.source.community.models import Citizen
from apps.source.discord.models import (
    Guild,
    Member,
    Category,
    TextChannel,
    VoiceChannel,
    StageChannel,
    ForumChannel,
)


# Guilds
def sync_guilds_with_db(bot: commands.Bot):
    guild_ids_in_db = set(Guild.objects.values_list('id', flat=True))
    guilds_in_db = Guild.objects.all()
    guilds_synced = 0

    for guild in bot.guilds:
        if str(guild.id) in guild_ids_in_db:
            db_guild = Guild.objects.get(id=guild.id)
            db_guild.name = guild.name
            db_guild.save()
            continue
        Guild.objects.create(id=guild.id, name=guild.name)
        guilds_synced += 1

    guilds_in_db.exclude(id__in=[str(guild.id) for guild in bot.guilds]).update(active=False)
    return guilds_synced

def remove_inactive_guilds():
    return Guild.objects.filter(active=False).delete()[0]

# Members
def sync_members_with_db(bot: commands.Bot):
    members_synced = 0
    for member in bot.get_all_members():
        if member.bot:
            continue

        member_in_db = Member.objects.filter(id=member.id).first()
        if member_in_db:
            member_in_db.citizen.name = member.display_name
            member_in_db.citizen.save()
            member_in_db.name = member.name
            member_in_db.save()
            continue

        members_citizen = Citizen.objects.create(name=member.display_name)
        Member.objects.create(id=member.id, name=member.name, citizen=members_citizen)
        members_synced += 1
    return members_synced

def sync_member_guilds_with_db(bot: commands.Bot):
    member_objects_in_db = Member.objects.all()
    members_updated = 0

    for db_member in member_objects_in_db:
        user = bot.get_user(int(db_member.id))
        guild_ids_in_member = set(db_member.guilds.values_list('id', flat=True))
        guilds_changed = False

        for guild in user.mutual_guilds:
            if str(guild.id) in guild_ids_in_member:
                continue
            guild_in_db_filter = Guild.objects.filter(id=guild.id).first()
            if guild_in_db_filter is None:
                guild_in_db_filter = Guild.objects.create(id=guild.id, name=guild.name, active=True)
            db_member.guilds.add(guild_in_db_filter)
            guilds_changed = True
        
        user_mutual_guild_ids = set([guild.id for guild in user.mutual_guilds])
        guilds_to_remove = [guild for guild in guild_ids_in_member if int(guild) not in user_mutual_guild_ids]
        for guild_to_remove in guilds_to_remove:
            db_member.guilds.remove(guild_to_remove)
            guilds_changed = True

        if (guilds_changed):
            db_member.save()
            members_updated += 1
    return members_updated

# Channels
def sync_channels_with_db(bot: commands.Bot):
    channels_synced = 0
    for guild in bot.guilds:
        guild_in_db = Guild.objects.get(id=guild.id)

        for channel in guild.channels:
            if not channel.permissions_for(guild.me).view_channel:
                continue

            channel_model = None
            if isinstance(channel, discord.TextChannel):
                channel_model = TextChannel
            elif isinstance(channel, discord.VoiceChannel):
                channel_model = VoiceChannel
            elif isinstance(channel, discord.CategoryChannel):
                channel_model = Category
            elif isinstance(channel, discord.StageChannel):
                channel_model = StageChannel
            elif isinstance(channel, discord.ForumChannel):
                channel_model = ForumChannel
            else:
                continue

            if channel_model.objects.filter(id=channel.id).exists():
                channel_in_db = channel_model.objects.get(id=channel.id)
                channel_in_db.name = channel.name
                channel_in_db.save()
                continue
            channel_model.objects.create(id=channel.id, name=channel.name, guild=guild_in_db)
            channels_synced += 1
    return channels_synced

class DiscordDBCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name='db_sync', description='Syncs discord related information with the database.')
    @discord.app_commands.default_permissions(administrator=True)
    async def db_sync(self, interaction: discord.Interaction):
        await interaction.response.send_message('Syncing discord information with the database...')
        guilds_synced = await sync_to_async(sync_guilds_with_db)(self.bot)
        members_synced = await sync_to_async(sync_members_with_db)(self.bot)
        members_updated = await sync_to_async(sync_member_guilds_with_db)(self.bot)
        channels_synced = await sync_to_async(sync_channels_with_db)(self.bot)

        message = 'Done!\n' \
            f'`{guilds_synced}` guild{"" if guilds_synced == 1 else "s"} synced to database.\n' \
            f'`{members_synced}` member{"" if members_synced == 1 else "s"} synced to database.\n' \
            f'`{members_updated}` member{"" if members_updated == 1 else "s"} updated with guilds.\n' \
            f'`{channels_synced}` channel{"" if channels_synced == 1 else "s"} synced to database.'
        await interaction.followup.send(message)

    @discord.app_commands.command(name='db_remove_inactive_guilds', description='Removes inactive guilds from the database.')
    @discord.app_commands.default_permissions(administrator=True)
    async def db_remove_inactive_guilds(self, interaction: discord.Interaction):
        await interaction.response.send_message('Removing inactive guilds from the database...')
        guilds_removed = await sync_to_async(remove_inactive_guilds)()
        await interaction.followup.send(f'Done! `{guilds_removed}` guild{"" if guilds_removed == 1 else "s"} removed.')

async def setup(bot: commands.Bot):
    await bot.add_cog(DiscordDBCog(bot))
