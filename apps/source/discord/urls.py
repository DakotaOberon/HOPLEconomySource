from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="discord_home"),
    path(r'guild/<int:guild_id>/', views.guild_home, name='discord_guild_home')
]
