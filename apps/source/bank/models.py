from django.db import models

from apps.source.community.models import Citizen

class BankAccount(models.Model):
    owner = models.OneToOneField(Citizen, on_delete=models.SET_NULL, null=True)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.owner.name}'s bank account"
    
    def __repr__(self):
        return f"BankAccount({self.owner.name})"

    def deposit(self, amount: int):
        if (amount < 0):
            raise ValueError("Please use positive integers only for deposits")
        self.balance += amount
        self.save()

    def withdraw(self, amount: int):
        if (amount < 0):
            raise ValueError("Please use positive integers only for withdrawals")
        if (amount > self.balance):
            raise ValueError("You cannot withdraw more than the balance")
        self.balance -= amount
        self.save()
