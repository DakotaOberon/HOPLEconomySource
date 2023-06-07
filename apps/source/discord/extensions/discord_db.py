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
def create_or_update_guild(guild: discord.Guild, active=True):
    db_guild, created = Guild.objects.get_or_create(id=str(guild.id))
    db_guild.name = guild.name
    db_guild.active = active
    db_guild.save()
    return created

def sync_guilds_with_db(bot: commands.Bot):
    guilds_in_db = Guild.objects.all()
    guilds_synced = 0

    for guild in bot.guilds:
        if create_or_update_guild(guild):
            guilds_synced += 1

    guilds_in_db.exclude(id__in=[str(guild.id) for guild in bot.guilds]).update(active=False)
    return guilds_synced

def remove_inactive_guilds():
    return Guild.objects.filter(active=False).delete()[0]

# Members
def create_or_update_member(member: discord.Member, leaving_guild=False):
    if member.bot:
        return None

    db_guild = Guild.objects.get(id=str(member.guild.id))
    db_member = Member.objects.filter(id=str(member.id)).first()
    if not db_member:
        db_citizen = Citizen.objects.create(name=member.display_name)
        db_member = Member.objects.create(id=str(member.id), name=member.name, citizen=db_citizen)

        if not (leaving_guild):
            db_member.guilds.add(db_guild)
        return True

    db_member.citizen.name = member.display_name
    db_member.citizen.save()
    db_member.name = member.name

    if not (leaving_guild):
        db_member.guilds.add(db_guild)
    else:
        db_member.guilds.remove(db_guild)

    db_member.save()
    return False

def sync_members_with_db(bot: commands.Bot):
    members_synced = 0
    for member in bot.get_all_members():
        created = create_or_update_member(member)
        if created:
            members_synced += 1
    return members_synced

# Channels
def create_or_update_channel(channel: discord.abc.GuildChannel, guild_id: int, remove=False):
    if not channel.permissions_for(channel.guild.me).view_channel:
        return None

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
        return None
    
    db_guild = Guild.objects.get(id=str(guild_id))
    try:
        db_channel = channel_model.objects.get(id=str(channel.id))
    except channel_model.DoesNotExist:
        if remove:
            return False
        db_channel = channel_model.objects.create(id=channel.id, name=channel.name, guild=db_guild)
        return True

    if remove:
        db_channel.delete()
        return False

    db_channel.name = channel.name
    db_channel.save()
    return False

def sync_channels_with_db(bot: commands.Bot):
    channels_synced = 0
    for guild in bot.guilds:
        for channel in guild.channels:
            if create_or_update_channel(channel, guild.id):
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
        channels_synced = await sync_to_async(sync_channels_with_db)(self.bot)

        message = 'Done!\n' \
            f'`{guilds_synced}` guild{"" if guilds_synced == 1 else "s"} synced to database.\n' \
            f'`{channels_synced}` channel{"" if channels_synced == 1 else "s"} synced to database.\n' \
            f'`{members_synced}` member{"" if members_synced == 1 else "s"} synced to database.'

        await interaction.followup.send(message)

    @discord.app_commands.command(name='db_remove_inactive_guilds', description='Removes inactive guilds from the database.')
    @discord.app_commands.default_permissions(administrator=True)
    async def db_remove_inactive_guilds(self, interaction: discord.Interaction):
        await interaction.response.send_message('Removing inactive guilds from the database...')
        guilds_removed = await sync_to_async(remove_inactive_guilds)()
        await interaction.followup.send(f'Done! `{guilds_removed}` guild{"" if guilds_removed == 1 else "s"} removed.')

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await sync_to_async(create_or_update_guild)(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        create_or_update_guild(guild, active=False)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        await sync_to_async(create_or_update_guild)(after)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await sync_to_async(create_or_update_member)(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await sync_to_async(create_or_update_member)(member, leaving_guild=True)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        await sync_to_async(create_or_update_member)(after)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        await sync_to_async(create_or_update_channel)(channel, channel.guild.id)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        await sync_to_async(create_or_update_channel)(channel, channel.guild.id, remove=True)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        await sync_to_async(create_or_update_channel)(after, after.guild.id)

async def setup(bot: commands.Bot):
    await bot.add_cog(DiscordDBCog(bot))
