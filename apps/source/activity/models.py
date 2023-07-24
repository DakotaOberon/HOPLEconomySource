from datetime import datetime

from django.db import models
from django.core.validators import MinLengthValidator
from django.db.models import JSONField
from django.utils import timezone

from apps.source.discord.models import Client, Member, VoiceChannel
from apps.source.holiday.models import WeekdayHoliday, FixedHoliday
from apps.source.bank.models import Currency


class ActivityMultiplier(models.Model):
    priority = models.PositiveSmallIntegerField(default=0, help_text='Priority of this multiplier. Lower priority multipliers will be used first.')
    currency = models.ForeignKey(Currency, related_name='activity_multipliers', on_delete=models.CASCADE, help_text='Currency to use for this multiplier.')
    rewards_per_day = models.IntegerField(default=100, help_text='How many rewards a user can earn per day.')
    base = models.FloatField(default=1.0, help_text='Starting multiplier for all activities')
    weekend = models.FloatField(default=0.5, help_text='Bonus points for being active on the weekend')
    birthday = models.FloatField(default=2.0, help_text='Bonus points for being active on your birthday')
    video = models.FloatField(default=0.04, help_text='Bonus points for having your video on in voice call')
    streaming = models.FloatField(default=0.06, help_text='Bonus points for streaming in voice call')
    muted = models.FloatField(default=-0.01, help_text='Bonus for being muted in voice call')
    deafened = models.FloatField(default=-0.12, help_text='Bonus for being deafened in voice call')
    group = models.FloatField(default=0.01, help_text='Bonus for each additional person in voice call')
    group_max = models.FloatField(default=0.1, help_text='Max bonus for additional people in voice call')

class ActivityController(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='activity_controller')
    is_holiday = models.BooleanField(default=False)
    is_weekend = models.BooleanField(default=False)
    base_multiplier = models.ForeignKey(ActivityMultiplier, on_delete=models.CASCADE, related_name='base_controllers')
    active_multiplier = models.ForeignKey(ActivityMultiplier, on_delete=models.CASCADE, related_name='active_controllers', null=True, blank=True)

    def set_is_weekend(self):
        self.is_weekend = datetime.now(timezone.get_current_timezone()).weekday() in [5, 6]
        self.save()

    def set_is_holiday(self):
        try:
            holidays_today: list[FixedHoliday | WeekdayHoliday] = self.holidays.get_holidays_today()
            self.is_holiday = len(holidays_today) > 0
            self.active_multiplier = max(holidays_today, key=lambda x: x.multiplier.multiplier.priority).multiplier.multiplier if self.is_holiday else None
        except ControllerHoliday.DoesNotExist:
            self.active_multiplier = None
            self.is_holiday = False
        self.save()

    def get_global_multiplier(self):
        if self.is_weekend == False:
            return 0
        if self.active_multiplier:
            return self.active_multiplier.weekend
        return self.base_multiplier.weekend

    def __str__(self):
        return f'ActivityController {self.id}'

    def __repr__(self):
        return f'<ActivityController({self.id})>'

class WeekdayHolidayMultiplier(models.Model):
    holiday = models.OneToOneField(WeekdayHoliday, on_delete=models.CASCADE, related_name='multiplier')
    multiplier = models.ForeignKey(ActivityMultiplier, on_delete=models.CASCADE, related_name='weekday_holidays')

    def __str__(self):
        return f'WeekdayHolidayMultiplier {self.holiday.name}'

    def __repr__(self):
        return f'WeekdayHolidayMultiplier({self.holiday.name})'

class FixedHolidayMultiplier(models.Model):
    holiday = models.OneToOneField(FixedHoliday, on_delete=models.CASCADE, related_name='multiplier')
    multiplier = models.ForeignKey(ActivityMultiplier, on_delete=models.CASCADE, related_name='fixed_holidays')

    def __str__(self):
        return f'FixedHolidayMultiplier {self.holiday.name}'

    def __repr__(self):
        return f'<FixedHolidayMultiplier({self.holiday.name})>'

class ControllerHoliday(models.Model):
    controller = models.OneToOneField(ActivityController, on_delete=models.CASCADE, related_name='holidays')
    weekday_holidays = models.ManyToManyField(WeekdayHoliday, blank=True)
    fixed_holidays = models.ManyToManyField(FixedHoliday, blank=True)

    def get_weekday_holidays_today(self):
        today = timezone.datetime.today()
        weekday_holidays = WeekdayHoliday.objects.filter(month=today.month, day=today.weekday())
        return [holiday for holiday in weekday_holidays if holiday.is_on(today)]

    def get_fixed_holidays_today(self):
        today = timezone.datetime.today()
        fixed_holidays = FixedHoliday.objects.filter(date__month=today.month, date__day=today.day)
        return [holiday for holiday in fixed_holidays if holiday.is_on(today)]

    def get_holidays_today(self):
        return self.get_weekday_holidays_today() + self.get_fixed_holidays_today()

    def __str__(self):
        return f'Controller Holidays {self.id}'

    def __repr__(self):
        return f'<ControllerHolidays({self.id})>'

class VoiceActivityTracker(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=18,
        validators=[MinLengthValidator(18)])
    member = models.OneToOneField(Member, on_delete=models.CASCADE, unique=True)
    controller = models.ForeignKey(ActivityController, blank=True, null=True, related_name='voice_activity_trackers', on_delete=models.SET_NULL)

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
    ticks_spent_video_on = models.IntegerField(default=0) # Time in ticks
    ticks_spent_streaming = models.IntegerField(default=0) # Time in ticks
    ticks_spent_deafened = models.IntegerField(default=0) # Time in ticks
    ticks_spent_muted = models.IntegerField(default=0) # Time in ticks
    points_earned = models.FloatField(default=0) # Points earned today

    multipliers_data = JSONField(default=dict, blank=True)

    def daily_reset(self):
        self.is_birthday = False
        self.rewards_left = 0
        self.ticks_spent_in_call = 0
        self.points_earned = 0
        self.multipliers_data = dict()

    def __str__(self):
        return f'Voice Activity Tracker - {self.member.name}'

    def __repr__(self):
        return f'<VoiceActivityTracker({self.member.name})>'

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
    points_earned = models.FloatField(default=0) # Total points earned
    highest_multiplier = models.FloatField(default=0) # Highest multiplier achieved
    highest_points_earned = models.IntegerField(default=0) # Highest points earned in a single day
    highest_time_spent_in_call = models.IntegerField(default=0) # Highest time spent in call in a single day

    multipliers_data = JSONField(default=dict)

    def __str__(self):
        return f'{self.member.name} Voice Activity Long Term Tracker'

    def __repr__(self):
        return f'<VoiceActivityLongTermTracker({self.member.name})>'
