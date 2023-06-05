import discord
from discord.ext import commands

from economy.event import EVENT_MANAGER
from .events import ClientEvent

class DiscordEventClient(commands.Bot):
    # Gateway Events
    async def on_ready(self):
        EVENT_MANAGER.source.discord.trigger('on_client_ready', ClientEvent(self))

    # Guild Events
    async def on_guild_join(self, guild: discord.Guild):
        EVENT_MANAGER.source.discord.trigger('on_guild_join', ClientEvent(self, guild=guild))

    async def on_guild_remove(self, guild: discord.Guild):
        EVENT_MANAGER.source.discord.trigger('on_guild_remove', ClientEvent(self, guild=guild))

    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        EVENT_MANAGER.source.discord.trigger('on_guild_update', ClientEvent(self, before=before, after=after))

    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        EVENT_MANAGER.source.discord.trigger('on_channel_create', ClientEvent(self, guild=channel.guild, channel=channel))

    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        EVENT_MANAGER.source.discord.trigger('on_channel_delete', ClientEvent(self, guild=channel.guild, channel=channel))

    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        EVENT_MANAGER.source.discord.trigger('on_channel_update', ClientEvent(self, before=before, after=after))

    async def on_thread_create(self, thread: discord.Thread):
        EVENT_MANAGER.source.discord.trigger('on_thread_create', ClientEvent(self, thread=thread))

    async def on_thread_join(self, thread: discord.Thread):
        EVENT_MANAGER.source.discord.trigger('on_thread_join', ClientEvent(self, thread=thread))

    async def on_thread_update(self, before: discord.Thread, after: discord.Thread):
        EVENT_MANAGER.source.discord.trigger('on_thread_update', ClientEvent(self, before=before, after=after))

    async def on_thread_delete(self, thread: discord.Thread):
        EVENT_MANAGER.source.discord.trigger('on_thread_delete', ClientEvent(self, thread=thread))

    # Interaction Events
    async def on_interaction(self, interaction: discord.Interaction):
        EVENT_MANAGER.source.discord.trigger('on_interaction', ClientEvent(self, interaction=interaction))

    # Member Events
    async def on_member_join(self, member: discord.Member):
        EVENT_MANAGER.source.discord.trigger('on_member_join', ClientEvent(self, member=member))

    async def on_member_remove(self, member: discord.Member):
        EVENT_MANAGER.source.discord.trigger('on_member_remove', ClientEvent(self, member=member))

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        EVENT_MANAGER.source.discord.trigger('on_member_update', ClientEvent(self, before=before, after=after))

    async def on_user_update(self, before: discord.User, after: discord.User):
        EVENT_MANAGER.source.discord.trigger('on_user_update', ClientEvent(self, before=before, after=after))

    async def on_thread_member_join(self, member: discord.Member):
        EVENT_MANAGER.source.discord.trigger('on_thread_member_join', ClientEvent(self, member=member))

    async def on_thread_member_remove(self, member: discord.Member):
        EVENT_MANAGER.source.discord.trigger('on_thread_member_remove', ClientEvent(self, member=member))

    # Invite Events
    async def on_invite_created(self, invite: discord.Invite):
        EVENT_MANAGER.source.discord.trigger('on_invite_created', ClientEvent(self, invite=invite))

    async def on_invite_deleted(self, invite: discord.Invite):
        EVENT_MANAGER.source.discord.trigger('on_invite_deleted', ClientEvent(self, invite=invite))

    # Voice State Events
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        EVENT_MANAGER.source.discord.trigger('on_voice_state_update', ClientEvent(self, member=member, before=before, after=after))

    # Presence Events
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        EVENT_MANAGER.source.discord.trigger('on_presence_update', ClientEvent(self, before=before, after=after))

    # Message Events
    async def on_message(self, message: discord.Message):
        EVENT_MANAGER.source.discord.trigger('on_message', ClientEvent(self, message=message))
        await super().on_message(message)

    # Reaction Events
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        EVENT_MANAGER.source.discord.trigger('on_reaction_add', ClientEvent(self, reaction=reaction, user=user))

    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User):
        EVENT_MANAGER.source.discord.trigger('on_reaction_remove', ClientEvent(self, reaction=reaction, user=user))
