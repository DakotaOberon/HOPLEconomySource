from django.contrib import admin
from .models import (
    WeekdayHoliday,
    FixedHoliday
)


admin.site.register([WeekdayHoliday, FixedHoliday])
