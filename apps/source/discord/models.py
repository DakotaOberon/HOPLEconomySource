from django.db import models
from django.core.validators import MinLengthValidator

from apps.source.community.models import Citizen

class Guild(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=18,
        validators=[MinLengthValidator(18)])
    name = models.CharField(max_length=64, default="Guild")

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

class TextChannel(Channel):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name="text_channels")

    def __str__(self):
        return f'#{self.name}'

    def __repr__(self):
        return f"TextChannel({self.name})"

class VoiceChannel(Channel):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name="voice_channels")

    def __str__(self):
        return f'<{self.name}'

    def __repr__(self):
        return f"VoiceChannel({self.name})"

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

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Client({self.name})"
