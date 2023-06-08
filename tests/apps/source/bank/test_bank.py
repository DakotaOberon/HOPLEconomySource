from django.test import TestCase

from apps.source.bank.models import Account, Currency, AccountCurrencyBalance
from apps.source.community.models import Citizen

class AccountModelTests(TestCase):
    def setUp(self):
        self.citizen = Citizen.objects.create(
            name="Test Citizen"
        )
        self.account = Account.objects.create(
            owner=self.citizen
        )
        self.currency_1 = Currency.objects.create(
            name="gold",
            plural="gold",
            symbol="g",
            symbol_as_prefix=False,
            value=1,
            decimal_places=0
        )
        self.currency_2 = Currency.objects.create(
            name="bill",
            plural="bills",
            symbol="$",
            symbol_as_prefix=True,
            value=100,
            decimal_places=2,
        )
    
    def test_no_currency_reference_in_account_on_creation(self):
        with self.assertRaises(AccountCurrencyBalance.DoesNotExist):
            AccountCurrencyBalance.objects.get(account=self.account, currency=self.currency_1)

    def test_withdraw_with_no_currency_reference(self):
        with self.assertRaises(AccountCurrencyBalance.DoesNotExist):
            self.account.withdraw(1, "gold")

    def test_currency_reference_created_on_deposit(self):
        self.account.deposit(1, "gold")
        account_currency = AccountCurrencyBalance.objects.get(account=self.account, currency=self.currency_1)
        self.assertEqual(account_currency.balance, 1)
    
    def test_currency_reference_created_on_check_balance(self):
        self.account.check_balance("bill")
        account_currency = AccountCurrencyBalance.objects.get(account=self.account, currency=self.currency_2)
        self.assertEqual(account_currency.balance, 0)

    def test_deposit(self):
        self.account.deposit(100, "gold")
        balance = self.account.check_balance("gold")
        self.assertEqual(balance, 100)

    def test_withdraw(self):
        self.account.deposit(100, "gold")
        self.account.withdraw(95, "gold")
        balance = self.account.check_balance("gold")
        self.assertEqual(balance, 5)

    def test_withdraw_too_much(self):
        self.account.deposit(100, "gold")
        with self.assertRaises(ValueError):
            self.account.withdraw(2000, "gold")

    def test_deposit_negative(self):
        with self.assertRaises(ValueError):
            self.account.deposit(-100, "gold")

    def test_withdraw_negative(self):
        self.account.deposit(100, "gold")
        with self.assertRaises(ValueError):
            self.account.withdraw(-100, "gold")

    def test_str(self):
        self.assertEqual(str(self.account), "Test Citizen's account")

    def test_repr(self):
        self.assertEqual(repr(self.account), "Account(Test Citizen)")

    def test_owner_set_to_null_on_owner_deletion(self):
        self.citizen.delete()
        self.account.refresh_from_db()
        self.assertIsNone(self.account.owner)

class CurrencyModelTest(TestCase):
    def setUp(self):
        self.currency_1 = Currency.objects.create(
            name="gold",
            plural="gold",
            symbol="g",
            symbol_as_prefix=False,
            value=1,
            decimal_places=0
        )
        self.currency_2 = Currency.objects.create(
            name="bill",
            plural="bills",
            symbol="$",
            symbol_as_prefix=True,
            value=100,
            decimal_places=2,
        )

    def test_convert(self):
        conversion_1 = self.currency_1.convert(1, "bill")
        conversion_2 = self.currency_2.convert(100, "gold")
        self.assertEqual(conversion_1, 100)
        self.assertEqual(conversion_2, 1)
    
    def test_convert_with_round(self):
        currency_3 = Currency.objects.create(
            name="silver",
            plural="silver",
            symbol="s",
            symbol_as_prefix=False,
            value=300,
            decimal_places=0
        )
        conversion_1 = self.currency_1.convert(1, "bill")
        conversion_2 = self.currency_2.convert(555.55, "gold")
        conversion_3 = currency_3.convert(1, "bill")
        self.assertEqual(conversion_1, 100)
        self.assertEqual(conversion_2, 6)
        self.assertEqual(conversion_3, 0.33)

    def test_conver_without_round(self):
        conversion = self.currency_2.convert(555.50, "gold", round_to_decimal_place=False)
        self.assertEqual(conversion, 5.555)

    def test_str_with_prefix(self):
        self.assertEqual(str(self.currency_1), "gold(g)")
        self.assertEqual(str(self.currency_2), "($)bill")

    def test_repr(self):
        self.assertEqual(repr(self.currency_1), "Currency(gold)")

class AccountCurrencyBalanceModelTest(TestCase):
    def setUp(self):
        self.citizen = Citizen.objects.create(
            name="Test Citizen"
        )
        self.account = Account.objects.create(
            owner=self.citizen
        )
        self.currency_1 = Currency.objects.create(
            name="gold",
            plural="gold",
            symbol="g",
            symbol_as_prefix=False,
            value=1,
            decimal_places=0
        )
        self.currency_2 = Currency.objects.create(
            name="bill",
            plural="bills",
            symbol="$",
            symbol_as_prefix=True,
            value=100,
            decimal_places=2,
        )
        self.account_currency_1 = AccountCurrencyBalance.objects.create(
            account=self.account,
            currency=self.currency_1,
            balance=100
        )
        self.account_currency_2 = AccountCurrencyBalance.objects.create(
            account=self.account,
            currency=self.currency_2,
            balance=100
        )

    def test_str(self):
        self.assertEqual(str(self.account_currency_1), "Test Citizen's account - gold(g): 100")
        self.assertEqual(str(self.account_currency_2), "Test Citizen's account - ($)bill: 100")

    def test_repr(self):
        self.assertEqual(repr(self.account_currency_1), "AccountCurrencyBalance(Test Citizen's account - gold(g))")
        self.assertEqual(repr(self.account_currency_2), "AccountCurrencyBalance(Test Citizen's account - ($)bill)")

    def test_deposit(self):
        self.account_currency_1.deposit(100)
        self.assertEqual(self.account_currency_1.balance, 200)

    def test_withdraw(self):
        self.account_currency_1.withdraw(50)
        self.assertEqual(self.account_currency_1.balance, 50)

    def test_withdraw_too_much(self):
        with self.assertRaises(ValueError):
            self.account_currency_1.withdraw(2000)

    def test_deposit_negative(self):
        with self.assertRaises(ValueError):
            self.account_currency_1.deposit(-100)

    def test_withdraw_negative(self):
        with self.assertRaises(ValueError):
            self.account_currency_1.withdraw(-100)
