from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from .views import DomainViewSet, AppViewSet, ModelViewSet, ItemViewSet


router = routers.DefaultRouter()
router.register(r'apps', DomainViewSet, basename='domains')
router.register(r'apps/(?P<domain>[^/.]+)', AppViewSet, basename='domain-apps')
router.register(r'apps/(?P<domain>[^/.]+)/(?P<app_label>[^/.]+)', ModelViewSet, basename='app-models')
router.register(r'apps/(?P<domain>[^/.]+)/(?P<app_label>[^/.]+)/(?P<model_name>[^/.]+)', ItemViewSet, basename='model-items')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
]
