from django.apps import apps
from django.db.models import Model
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import permissions


def get_installed_app_serializers():
    installed_app_serializers = {}

    app_models = apps.get_models()
    for app_model in app_models:
        if not issubclass(app_model, Model):
            continue

        class_name = app_model.__name__ + 'Serializer'
        class Meta:
            model = app_model
            fields = '__all__'
        serializer_class = type(class_name, (serializers.ModelSerializer,), {'Meta': Meta})

        installed_app_serializers[app_model.__name__] = serializer_class

    return installed_app_serializers

def get_installed_app_viewsets(serializer_classes: dict[serializers.ModelSerializer]):
    skippable_models = ['LogEntry', 'ContentType', 'Session', 'Permission', 'Group', 'User']
    installed_app_viewsets = {}

    models = apps.get_models()
    for model in models:
        if not issubclass(model, Model):
            continue

        if model.__name__ not in serializer_classes:
            continue

        if model.__name__ in skippable_models:
            continue

        # Create viewset class
        class_name = model.__name__ + 'ViewSet'
        queryset = model.objects.all().order_by('id')
        serializer_class = serializer_classes[model.__name__]
        permission_classes = [permissions.IsAuthenticated]
        viewset_class = type(class_name, (viewsets.ModelViewSet,), {'queryset': queryset, 'serializer_class': serializer_class, 'permission_classes': permission_classes})

        # Add viewset to installed_app_viewsets
        installed_app_viewsets[model.__name__] = viewset_class
    return installed_app_viewsets
