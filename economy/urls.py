"""
URL configuration for economy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from .util import get_installed_app_serializers, get_installed_app_viewsets


installed_module_serializers = get_installed_app_serializers()
installed_module_viewsets = get_installed_app_viewsets(installed_module_serializers)
print(installed_module_viewsets)

router = routers.DefaultRouter()

for view in installed_module_viewsets:
    router.register(r'{}'.format(view.lower()), installed_module_viewsets[view], basename=view.lower())

print(router.get_api_root_view())

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
]
