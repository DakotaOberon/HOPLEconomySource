from django.test import TestCase

from apps.source.community.models import Citizen

class CitizenModelTests(TestCase):
    def setUp(self):
        self.citizen = Citizen.objects.create(
            name="Test Citizen"
        )

    def test_str(self):
        self.assertEqual(str(self.citizen), "Test Citizen")
