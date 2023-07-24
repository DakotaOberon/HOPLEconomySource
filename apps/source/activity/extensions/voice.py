import discord
from discord.ext import commands, tasks
from asgiref.sync import sync_to_async

from apps.source.activity.util import (
    get_activity_tracker_list,
    update_voice_activity_from_discord_member_voice_state,
    tick_member_activity_tracker,
    get_active_multiplier,
)
from apps.source.activity.models import ActivityMultiplier, ActivityController


class VoiceCog(commands.Cog):
    def __init__(self, bot: commands.Bot, activity_controller: ActivityController, active_multiplier: ActivityMultiplier):
        self.bot = bot
        self.activity_controller = activity_controller
        self.active_multiplier = active_multiplier
        self.on_tick.start()

    @tasks.loop(seconds=1)
    async def on_tick(self):
        self.active_multiplier = await sync_to_async(get_active_multiplier)(self.activity_controller)
        all_trackers = await sync_to_async(get_activity_tracker_list)()
        for tracker in all_trackers:
            await sync_to_async(tick_member_activity_tracker)(tracker, self.activity_controller, self.active_multiplier)

    @on_tick.before_loop
    async def before_on_tick(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.on_tick.cancel()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        await sync_to_async(update_voice_activity_from_discord_member_voice_state)(member, after, self.active_multiplier)

async def setup(bot: commands.Bot):
    activity_controller = await sync_to_async(ActivityController.objects.get)(client__id=bot.user.id)
    active_multiplier = await sync_to_async(get_active_multiplier)(activity_controller)
    await bot.add_cog(VoiceCog(bot, activity_controller, active_multiplier))
