from django.test import TestCase

from apps.source.bank.models import BankAccount
from apps.source.community.models import Citizen

class BankAccountModelTests(TestCase):
    def setUp(self):
        self.citizen = Citizen.objects.create(
            name="Test Citizen",
            discord_id=1234567890
        )
        self.account = BankAccount.objects.create(
            owner=self.citizen,
            balance=1000
        )

    def test_deposit(self):
        self.account.deposit(100)
        self.assertEqual(self.account.balance, 1100)

    def test_withdraw(self):
        self.account.withdraw(100)
        self.assertEqual(self.account.balance, 900)

    def test_withdraw_too_much(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(2000)

    def test_deposit_negative(self):
        with self.assertRaises(ValueError):
            self.account.deposit(-100)

    def test_withdraw_negative(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(-100)

    def test_str(self):
        self.assertEqual(str(self.account), "Test Citizen's bank account")
