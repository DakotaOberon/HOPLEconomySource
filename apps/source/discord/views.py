from django.shortcuts import render
from .models import Guild


def home(request):
    guilds_list = Guild.objects.order_by("name")
    return render(request, "discord_home.html", {"guilds_list": guilds_list})
