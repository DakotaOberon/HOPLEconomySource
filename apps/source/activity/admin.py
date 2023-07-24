from django.contrib import admin
from .models import (
    ActivityMultiplier,
    ActivityController,
    WeekdayHolidayMultiplier,
    FixedHolidayMultiplier,
    ControllerHoliday,
    VoiceActivityTracker,
    VoiceActivityLongTermTracker,
)


admin.site.register([
    ActivityMultiplier,
    ActivityController,
    WeekdayHolidayMultiplier,
    FixedHolidayMultiplier,
    ControllerHoliday,
    VoiceActivityTracker,
    VoiceActivityLongTermTracker,
])
