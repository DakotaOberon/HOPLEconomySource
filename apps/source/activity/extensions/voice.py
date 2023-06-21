from datetime import time

import discord
from discord.ext import commands, tasks
from django.utils import timezone
from asgiref.sync import sync_to_async

from apps.source.activity.settings import VOICE_CONFIG
from apps.source.activity.util import (
    get_activity_tracker_list,
    update_voice_activity_from_discord_member_voice_state,
    tick_member_activity_tracker,
    daily_activity_tracker_reset,
)
from apps.source.activity.models import VoiceController


RESET_TIME = timezone.make_aware(time(hour=VOICE_CONFIG['REWARD_RESET_HOUR'], minute=12), timezone.get_current_timezone())

class VoiceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.on_tick.start()
        self.reset_voice_activity.start()

    @tasks.loop(seconds=1)
    async def on_tick(self):
        all_trackers = await sync_to_async(get_activity_tracker_list)()
        for tracker in all_trackers:
            await sync_to_async(tick_member_activity_tracker)(tracker)

    @on_tick.before_loop
    async def before_on_tick(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.on_tick.cancel()
        self.reset_voice_activity.cancel()

    @tasks.loop(time=RESET_TIME)
    async def reset_voice_activity(self):
        all_trackers = await sync_to_async(get_activity_tracker_list)()
        for tracker in all_trackers:
            await sync_to_async(daily_activity_tracker_reset)(tracker)

        voice_controller = await sync_to_async(VoiceController.objects.first)()
        await sync_to_async(voice_controller.set_is_weekend)()
        await sync_to_async(voice_controller.set_is_holiday)()
        return

    @reset_voice_activity.before_loop
    async def before_reset_voice_activity(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        await sync_to_async(update_voice_activity_from_discord_member_voice_state)(member, after)

async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceCog(bot))
