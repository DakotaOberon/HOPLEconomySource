from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers
from .views import AppDomainViewSet, DomainAppViewSet, AppViewSet, AppModelViewSet


router = routers.DefaultRouter()
router.register(r'apps', AppDomainViewSet, basename='app-domains')
router.register(r'apps/(?P<domain>[^/.]+)', DomainAppViewSet, basename='app')
router.register(r'apps/(?P<domain>[^/.]+)/(?P<app_label>[^/.]+)', AppViewSet, basename='app-module')
router.register(r'apps/(?P<domain>[^/.]+)/(?P<app_label>[^/.]+)/(?P<model_name>[^/.]+)', AppModelViewSet, basename='app-model')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
]
