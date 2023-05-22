from django.db import models
from django.contrib import admin
from economy.event import EVENT_MANAGER

class Citizen(models.Model):
    name = models.CharField(max_length=64, unique=True, null=True)

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        if created:
            EVENT_MANAGER.source.community.trigger('on_citizen_created', citizen=self)
            return
        EVENT_MANAGER.source.community.trigger('on_citizen_updated', citizen=self)

    def delete(self, *args, **kwargs):
        EVENT_MANAGER.source.community.trigger('on_citizen_deleted', citizen=self)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Citizen({self.name})"

class CitizenAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        created = not obj.pk
        if created:
            EVENT_MANAGER.source.community.trigger('on_citizen_created', citizen=obj)
            return
        EVENT_MANAGER.source.community.trigger('on_citizen_updated', citizen=obj)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        EVENT_MANAGER.source.community.trigger('on_citizen_deleted', citizen=obj)
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset) -> None:
        for obj in queryset:
            EVENT_MANAGER.source.community.trigger('on_citizen_deleted', citizen=obj)
        return super().delete_queryset(request, queryset)
