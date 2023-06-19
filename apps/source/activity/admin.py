from django.contrib import admin
from .models import (
    VoiceController,
    VoiceActivityTracker,
    VoiceActivityLongTermTracker,
)


admin.site.register([VoiceController, VoiceActivityTracker, VoiceActivityLongTermTracker])
