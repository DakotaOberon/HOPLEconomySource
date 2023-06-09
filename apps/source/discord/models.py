from django.db import models
from django.core.validators import MinLengthValidator

from apps.source.community.models import Citizen


class Guild(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=18,
        validators=[MinLengthValidator(18)])
    name = models.CharField(max_length=64, default="Guild")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Guild({self.name})"

class Member(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=18,
        validators=[MinLengthValidator(18)])
    name = models.CharField(max_length=64, default="Member")
    guilds = models.ManyToManyField(Guild, related_name="members", blank=True)
    citizen = models.OneToOneField(Citizen, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Member({self.name})"

class Channel(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=18,
        validators=[MinLengthValidator(18)])
    name = models.CharField(max_length=64, default="Channel")
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class Category(Channel):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name="categories")

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f"Category({self.name})"

class TextChannel(Channel):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name="text_channels")

    def __str__(self):
        return f'#{self.name}'

    def __repr__(self):
        return f"TextChannel({self.name})"

class VoiceChannel(Channel):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name="voice_channels")

    def __str__(self):
        return f'#{self.name}'

    def __repr__(self):
        return f"VoiceChannel({self.name})"

class StageChannel(Channel):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name="stage_channels")

    def __str__(self):
        return f'#{self.name}'

    def __repr__(self):
        return f"StageChannel({self.name})"

class ForumChannel(Channel):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name="forum_channels")

    def __str__(self):
        return f'#{self.name}'

    def __repr__(self):
        return f"ForumChannel({self.name})"

class Client(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=18,
        validators=[MinLengthValidator(18)])
    name = models.CharField(max_length=64, default="Client")
    presence_intent = models.BooleanField(default=False)
    server_members_intent = models.BooleanField(default=False)
    message_content_intent = models.BooleanField(default=False)
    token = models.CharField(max_length=80, default="Token")
    command_prefix = models.CharField(max_length=8, default="!")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Client({self.name})"
