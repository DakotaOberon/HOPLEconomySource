from django.db import models
from django.core.validators import MinLengthValidator

class Guild(models.Model):
    name = models.CharField(max_length=64, unique=True, null=True)
    discord_id = models.CharField(
        max_length=18,
        validators=[MinLengthValidator(18)],
        unique=True, 
        null=True)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Guild({self.name})"

class Channel(models.Model):
    name = models.CharField(max_length=64, unique=True, null=True)
    discord_id = models.CharField(
        max_length=18,
        validators=[MinLengthValidator(18)],
        unique=True, 
        null=True)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True

class TextChannel(Channel):
    def __str__(self):
        return f'#{self.name}'

    def __repr__(self):
        return f"TextChannel({self.name})"

class VoiceChannel(Channel):
    def __str__(self):
        return f'<{self.name}'

    def __repr__(self):
        return f"VoiceChannel({self.name})"
