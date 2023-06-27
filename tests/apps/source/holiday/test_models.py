from django.test import TestCase
from datetime import date

from apps.source.holiday.models import (
    Holiday,
    WeekdayHoliday,
    FixedHoliday
)


class HolidayTestCase(TestCase):
    def test_abstract(self):
        self.assertTrue(Holiday._meta.abstract)

class WeekdayHolidayTestCase(TestCase):
    def setUp(self):
        self.weekday_holiday = WeekdayHoliday.objects.create(
            name='Test Weekday Holiday',
            week=1,
            month=1,
            day=0
        )

    def test_get_date(self):
        self.assertEqual(self.weekday_holiday.get_date(2020).date(), date(2020, 1, 6))

    def test_get_date_last(self):
        self.weekday_holiday.week = -1
        self.assertEqual(self.weekday_holiday.get_date(2020).date(), date(2020, 1, 27))

    def test_str(self):
        self.assertEqual(str(self.weekday_holiday), 'Test Weekday Holiday: First Monday of January')
        self.weekday_holiday.week = 2
        self.assertEqual(str(self.weekday_holiday), 'Test Weekday Holiday: 2nd Monday of January')
        self.weekday_holiday.week = -1
        self.assertEqual(str(self.weekday_holiday), 'Test Weekday Holiday: Last Monday of January')
        self.weekday_holiday.week = -2
        self.assertEqual(str(self.weekday_holiday), 'Test Weekday Holiday: 2nd to last Monday of January')

    def test_repr(self):
        self.assertEqual(repr(self.weekday_holiday), '<WeekdayHoliday: Test Weekday Holiday>')

class FixedHolidayTestCase(TestCase):
    def setUp(self):
        self.fixed_holiday = FixedHoliday.objects.create(
            name='Test Fixed Holiday',
            date=date(2000, 1, 1)
        )

    def test_get_date(self):
        self.assertEqual(self.fixed_holiday.get_date(2020).date(), date(2020, 1, 1))

    def test_str(self):
        self.assertEqual(str(self.fixed_holiday), 'Test Fixed Holiday: January 01')

    def test_repr(self):
        self.assertEqual(repr(self.fixed_holiday), '<FixedHoliday: Test Fixed Holiday>')
