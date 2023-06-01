from django.shortcuts import render
from .models import Guild, Client


def home(request):
    guilds_list = Guild.objects.order_by("name")
    clients_list = Client.objects.order_by("name")
    return render(request, "discord_home.html", {"guilds_list": guilds_list, "clients_list": clients_list})

def guild_item(request, guild_id):
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

    return render(request, "discord_guild_item.html", guild_info)

def client_item(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        client = None

    client_info = {}
    if (client):
        client_info = {
            "id": client.id,
            "name": client.name,
            "presence_intent": client.presence_intent,
            "server_members_intent": client.server_members_intent,
            "message_content_intent": client.message_content_intent,
        }

    return render(request, "discord_client_item.html", client_info)
