from django.db import models
from django.core.validators import MinLengthValidator

class Citizen(models.Model):
    name = models.CharField(max_length=64, unique=True, null=True)
    discord_id = models.CharField(
        max_length=18,
        validators=[MinLengthValidator(18)],
        unique=True, 
        null=True)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Citizen({self.name})"
