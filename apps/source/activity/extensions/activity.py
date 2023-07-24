from datetime import time

from discord.ext import commands, tasks
from django.utils import timezone
from asgiref.sync import sync_to_async

from apps.source.activity.settings import VOICE_CONFIG
from apps.source.activity.util import (
    get_activity_tracker_list,
    daily_activity_tracker_reset,
    get_active_multiplier,
)
from apps.source.activity.models import ActivityMultiplier, ActivityController


RESET_TIME = timezone.make_aware(time(hour=VOICE_CONFIG['REWARD_RESET_HOUR'], minute=0), timezone.get_current_timezone())

class ActivityCog(commands.Cog):
    def __init__(self, bot: commands.Bot, activity_controller: ActivityController, active_multiplier: ActivityMultiplier):
        self.bot = bot
        self.activity_controller = activity_controller
        self.active_multiplier = active_multiplier
        self.reset_activity.start()

    def cog_unload(self):
        self.reset_activity.cancel()

    @tasks.loop(time=RESET_TIME)
    async def reset_activity(self):
        all_trackers = await sync_to_async(get_activity_tracker_list)()
        for tracker in all_trackers:
            await sync_to_async(daily_activity_tracker_reset)(tracker, self.active_multiplier)

        await sync_to_async(self.activity_controller.set_is_weekend)()
        await sync_to_async(self.activity_controller.set_is_holiday)()
        self.active_multiplier = sync_to_async(get_active_multiplier)(self.activity_controller)
        return

    @reset_activity.before_loop
    async def before_reset_voice_activity(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    activity_controller = await sync_to_async(ActivityController.objects.get)(client__id=bot.user.id)
    active_multiplier = await sync_to_async(get_active_multiplier)(activity_controller)
    await sync_to_async(activity_controller.set_is_weekend)()
    await sync_to_async(activity_controller.set_is_holiday)()
    await bot.add_cog(ActivityCog(bot, activity_controller, active_multiplier))
