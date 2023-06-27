from django.test import TestCase
from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU

from apps.source.holiday.util import (
    int_to_dateutil_weekday
)


class IntToDateutilWeekdayTestCase(TestCase):
    def test_int_to_dateutil_weekday(self):
        self.assertEqual(int_to_dateutil_weekday(0), MO)
        self.assertEqual(int_to_dateutil_weekday(1), TU)
        self.assertEqual(int_to_dateutil_weekday(2), WE)
        self.assertEqual(int_to_dateutil_weekday(3), TH)
        self.assertEqual(int_to_dateutil_weekday(4), FR)
        self.assertEqual(int_to_dateutil_weekday(5), SA)
        self.assertEqual(int_to_dateutil_weekday(6), SU)
