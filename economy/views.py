from django.apps import apps
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.response import Response


def get_installed_apps_by_domain() -> dict:
    app_configs = apps.get_app_configs()
    app_domains = {}
    for app_config in app_configs:
        if not (app_config.name.startswith('apps')):
            continue
        domain = app_config.name.split('.')[1]
        app_label = app_config.name.split('.')[2]
        if domain not in app_domains:
            app_domains[domain] = []
        app_domains[domain].append(app_label)
    
    return app_domains

# ViewSet for /apps endpoint
class DomainViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    apps = get_installed_apps_by_domain()

    def list(self, request):
        response = {}
        for domain in self.apps:
            domain_url = f'{request.scheme}://{request.get_host()}/apps/{domain}'
            response[domain] = domain_url

        return Response(response)

# ViewSet for /apps/{domain} endpoint
class AppViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    apps = get_installed_apps_by_domain()

    def list(self, request, domain=None):
        response = {}
        for app_label in self.apps.get(domain, []):
            base_url = request.build_absolute_uri('/')
            app_url = f'{base_url}apps/{domain}/{app_label}'
            response[app_label] = app_url

        return Response(response)

# ViewSet for /apps/{domain}/{app_label} endpoint
class ModelViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, domain=None, app_label=None):
        response = {}
        app_config = apps.get_app_config(app_label)
        for model in app_config.get_models():
            model_name_lower = model.__name__.lower()
            base_url = request.build_absolute_uri('/')
            model_url = f'{base_url}apps/{domain}/{app_label}/{model_name_lower}'
            response[model_name_lower] = model_url

        return Response(response)

# ViewSet for /apps/{domain}/{app_label}/{model_name} endpoint
class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        app_label = self.kwargs['app_label']
        model_name = self.kwargs['model_name']
        app_config = apps.get_app_config(app_label)
        model = app_config.get_model(model_name)
        return model.objects.all().order_by('id')

    def get_serializer_class(self):
        app_label = self.kwargs['app_label']
        model_name = self.kwargs['model_name']
        app_config = apps.get_app_config(app_label)
        app_model = app_config.get_model(model_name)
        class_name = app_model.__name__ + 'Serializer'
        class Meta:
            model = app_model
            fields = '__all__'
        serializer_class = type(class_name, (serializers.ModelSerializer,), {'Meta': Meta})
        return serializer_class
