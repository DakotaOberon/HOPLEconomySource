from django.db import models

class Citizen(models.Model):
    name = models.CharField(max_length=64, unique=True, null=True)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Citizen({self.name})"
