from django.contrib import admin
from .models import Account, Currency, AccountCurrencyBalance

admin.site.register([Account, Currency, AccountCurrencyBalance])
