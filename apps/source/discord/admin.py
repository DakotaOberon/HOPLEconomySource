from django.contrib import admin
from .models import Guild, TextChannel, VoiceChannel

admin.site.register([Guild, TextChannel, VoiceChannel])
