from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="discord_home"),
    path(r'guild/<int:guild_id>/', views.guild_item, name='discord_guild_home'),
    path(r'client/<int:client_id>/', views.client_item, name='discord_client_home'),
]
