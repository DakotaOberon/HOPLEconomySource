from django.db import models

from apps.source.community.models import Citizen


class Currency(models.Model):
    name = models.CharField(max_length=64, unique=True, help_text="The name of the currency (gold coin)")
    plural = models.CharField(max_length=64, null=True, blank=True, default=None, help_text="The plural form of the currency (gold coins)")
    symbol = models.CharField(max_length=128, null=True, blank=True, default='$', help_text="The symbol of the currency ($) or (<:Name:discord_id>)")
    symbol_as_prefix = models.BooleanField(default=True, help_text="Whether the symbol should be a prefix ($10) or a suffix (10$)")
    value = models.IntegerField(default=1, help_text="The value of the currency in reference to every other currency. Used for conversions. (1 gold coin = 10 silver coin = 100 copper coin)")
    decimal_places = models.IntegerField(default=2, help_text="The number of decimal places the currency can break down into (10.00 gold coins)")

    def save(self, *args, **kwargs):
        if self.plural == None:
            self.plural = f"{self.name}s"
        super().save(*args, **kwargs)

    def convert(self, amount: int, currency: str, round_to_decimal_place: bool = True):
        if (amount < 0):
            raise ValueError("Please use positive integers only for conversions")
        if (self.name == currency):
            return amount
        if (self.value == 0):
            raise ValueError("Cannot convert to a currency with a value of 0")
        currency_obj = Currency.objects.get(name=currency)
        converted_value = (amount / self.value) * currency_obj.value
        if (round_to_decimal_place):
            converted_value = round(converted_value, currency_obj.decimal_places)
        return converted_value

    def __str__(self):
        return f"({self.symbol}){self.name}" if self.symbol_as_prefix else f"{self.name}({self.symbol})"

    def __repr__(self):
        return f"Currency({self.name})"

class Account(models.Model):
    owner = models.OneToOneField(Citizen, on_delete=models.SET_NULL, null=True)

    def deposit(self, amount: int, currency: str|Currency):
        if (amount < 0):
            raise ValueError("Please use positive integers only for deposits")
        currency_object = Currency.objects.get(name=currency) if isinstance(currency, str) else currency
        account_currency, created = AccountCurrencyBalance.objects.get_or_create(
            account=self,
            currency=currency_object
        )
        account_currency.deposit(amount)

    def withdraw(self, amount: int, currency: str|Currency):
        if (amount < 0):
            raise ValueError("Please use positive integers only for withdrawals")
        currency_object = Currency.objects.get(name=currency) if isinstance(currency, str) else currency
        account_currency = AccountCurrencyBalance.objects.get(
            account=self,
            currency=currency_object
        )
        account_currency.withdraw(amount)

    def check_balance(self, currency: str|Currency):
        currency_object = Currency.objects.get(name=currency) if isinstance(currency, str) else currency
        account_currency, created = AccountCurrencyBalance.objects.get_or_create(
            account=self,
            currency=currency_object
        )
        return account_currency.balance

    def __str__(self):
        return f"{self.owner.name}'s account"

    def __repr__(self):
        return f"Account({self.owner.name})"

class AccountCurrencyBalance(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)

    def deposit(self, amount: int):
        if (amount < 0):
            raise ValueError("Please use positive integers only for deposits")
        self.balance = round(self.balance + amount, self.currency.decimal_places)
        self.save()

    def withdraw(self, amount: int):
        if (amount < 0):
            raise ValueError("Please use positive integers only for withdrawals")
        if (amount > self.balance):
            raise ValueError("You cannot withdraw more than the balance")
        self.balance = round(self.balance - amount, self.currency.decimal_places)
        self.save()

    def __str__(self):
        return f"{self.account} - {self.currency}: {self.balance}"

    def __repr__(self):
        return f"AccountCurrencyBalance({self.account} - {self.currency})"
