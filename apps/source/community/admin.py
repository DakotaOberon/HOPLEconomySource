from django.contrib import admin
from .models import Citizen, CitizenAdmin

admin.site.register(Citizen, CitizenAdmin)
