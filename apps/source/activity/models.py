from django.db import models
from django.core.validators import MinLengthValidator
from django.db.models import JSONField

from apps.source.discord.models import Member, VoiceChannel


class VoiceController(models.Model):
    is_holiday = models.BooleanField(default=False)
    is_weekend = models.BooleanField(default=False)

class VoiceActivityTracker(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=18,
        validators=[MinLengthValidator(18)])
    member = models.OneToOneField(Member, on_delete=models.CASCADE, unique=True)
    controller = models.ForeignKey(VoiceController, blank=True, null=True, related_name='voice_activity_trackers', on_delete=models.SET_NULL)

    # Multiplier trackers
    is_birthday = models.BooleanField(default=False)
    video_on = models.BooleanField(default=False)
    streaming = models.BooleanField(default=False)
    muted = models.BooleanField(default=False)
    deafened = models.BooleanField(default=False)

    current_channel = models.ForeignKey(VoiceChannel, null=True, blank=True, related_name='voice_activity_trackers', on_delete=models.SET_NULL)

    # Reward trackers
    ticks_till_reward = models.IntegerField(default=0) # Saved only when user leaves voice channel
    rewards_left = models.IntegerField(default=0) # Saved only when user leaves voice channel
    ticks_spent_in_call = models.IntegerField(default=0) # Time in ticks
    points_earned = models.IntegerField(default=0) # Points earned today

    multipliers_data = JSONField(default=dict, blank=True)

    def __str__(self):
        return f'Voice Activity Tracker - {self.member.name}'

    def __repr__(self):
        return f'VoiceActivityTracker({self.member.name})'

class VoiceActivityLongTermTracker(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=18,
        validators=[MinLengthValidator(18)])
    member = models.OneToOneField(Member, on_delete=models.CASCADE, unique=True)

    time_spent_in_call = models.IntegerField(default=0) # Time in seconds
    time_spent_video_on = models.IntegerField(default=0) # Time in seconds
    time_spent_streaming = models.IntegerField(default=0) # Time in seconds
    time_spent_deafened = models.IntegerField(default=0) # Time in seconds
    time_spent_muted = models.IntegerField(default=0) # Time in seconds
    points_earned = models.IntegerField(default=0) # Total points earned
    highest_multiplier = models.FloatField(default=0) # Highest multiplier achieved
    highest_points_earned = models.IntegerField(default=0) # Highest points earned in a single day
    highest_time_spent_in_call = models.IntegerField(default=0) # Highest time spent in call in a single day

    multiplier_data = JSONField(default=dict)

    def __str__(self):
        return f'{self.member.name} Voice Activity Long Term Tracker'

    def __repr__(self):
        return f'VoiceActivityLongTermTracker({self.member.name})'
