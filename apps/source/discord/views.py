from django.shortcuts import render
from .models import Guild, Client


def home(request):
    guilds_list = Guild.objects.order_by("name")
    clients_list = Client.objects.order_by("name")
    return render(request, "discord_home.html", {"guilds_list": guilds_list, "clients_list": clients_list})

def guild_home(request, guild_id):
    try:
        guild = Guild.objects.get(id=guild_id)
    except Guild.DoesNotExist:
        guild = None
    
    guild_info = {}
    if (guild):
        guild_info = {
            "id": guild.id,
            "name": guild.name,
            "total_members": len(guild.members.all()),
        }

    return render(request, "discord_guild_home.html", guild_info)
