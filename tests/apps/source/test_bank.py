from django.test import TestCase

from apps.source.bank.models import BankAccount
from apps.source.community.models import Citizen

class BankAccountModelTests(TestCase):
    def setUp(self):
        self.citizen = Citizen.objects.create(
            name="Test Citizen"
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
    
    def test_repr(self):
        self.assertEqual(repr(self.account), "BankAccount(Test Citizen)")

    def test_owner_set_to_null_on_owner_deletion(self):
        self.citizen.delete()
        self.account.refresh_from_db()
        self.assertIsNone(self.account.owner)
