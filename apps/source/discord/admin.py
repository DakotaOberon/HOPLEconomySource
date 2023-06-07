from django.contrib import admin
from .models import (
    Guild,
    Member,
    Category,
    TextChannel,
    VoiceChannel,
    StageChannel,
    ForumChannel,
    Client,
)

admin.site.register([Guild, Category, TextChannel, VoiceChannel, StageChannel, ForumChannel, Member, Client])
