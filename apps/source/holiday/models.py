from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone

from apps.source.holiday.util import int_to_dateutil_weekday


class Holiday(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="", blank=True)

    class Meta:
        abstract = True

class WeekdayHoliday(Holiday):
    month = models.PositiveSmallIntegerField(choices=(
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ))
    week = models.SmallIntegerField(default=1)
    day = models.PositiveSmallIntegerField(choices=(
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ))

    def get_date(self, year):
        if self.week >= 0:
            day = 1
        else:
            day = 31
        weekday = int_to_dateutil_weekday(self.day)
        return timezone.datetime.today() + relativedelta(year=year, month=self.month, day=day, weekday=weekday(+self.week), hour=0, minute=0, second=0, microsecond=0)

    def __str__(self):
        week_str = f'{self.week}th'
        if self.week == 1 or self.week == 0:
            week_str = 'First'
        elif self.week == -1:
            week_str = 'Last'
        elif abs(self.week) == 2:
            week_str = f'{abs(self.week)}nd'
        elif abs(self.week) == 3:
            week_str = f'{abs(self.week)}rd'

        if self.week < -1:
            week_str += ' to last'

        return f'{self.name}: {week_str} {self.get_day_display()} of {self.get_month_display()}'

    def __repr__(self):
        return f'<WeekdayHoliday: {self.name}>'

class FixedHoliday(Holiday):
    date = models.DateField(default=timezone.make_aware(timezone.datetime(2020, 1, 1)), help_text='Year is ignored')

    def get_date(self, year):
        return timezone.make_aware(timezone.datetime(year, self.date.month, self.date.day))

    def __str__(self):
        return f'{self.name}: {self.date.strftime("%B %d")}'

    def __repr__(self):
        return f'<FixedHoliday: {self.name}>'
