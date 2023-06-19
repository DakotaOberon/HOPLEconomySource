import discord
from discord.ext import commands, tasks
from asgiref.sync import sync_to_async

from apps.source.activity.models import VoiceActivityTracker
from apps.source.activity.settings import VOICE_CONFIG
from apps.source.activity.util import (
    get_activity_tracker_list,
    update_voice_activity_from_discord_member_voice_state,
    tick_member_activity_tracker,
)


class VoiceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.on_tick.start()

    @tasks.loop(seconds=1)
    async def on_tick(self):
        # Loop voice activity trackers. For each tracker with a channel, update tracker.
        all_trackers = await sync_to_async(get_activity_tracker_list)()
        for tracker in all_trackers:
            await sync_to_async(tick_member_activity_tracker)(tracker)

    @on_tick.before_loop
    async def before_on_tick(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.on_tick.cancel()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        await sync_to_async(update_voice_activity_from_discord_member_voice_state)(member, after)

async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceCog(bot))
