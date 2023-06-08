from unittest.mock import patch, PropertyMock

from django.test import TestCase
from discord.ext import commands

from apps.source.discord.client import DiscordClient
from apps.source.discord.models import (
    Guild,
    Member,
    Category,
    TextChannel,
    VoiceChannel,
    StageChannel,
    ForumChannel,
    Client,
)
from apps.source.discord.extensions.discord_db import (
    create_or_update_guild,
    sync_guilds_with_db,
    remove_inactive_guilds,
    create_or_update_member,
    sync_members_with_db,
    create_or_update_channel,
    sync_channels_with_db,
)
from apps.source.community.models import Citizen
from tests.apps.source.discord.utils import (
    MockDiscordGuild,
    MockDiscordMember,
    MockDiscordCategory,
    MockDiscordTextChannel,
    MockDiscordVoiceChannel,
    MockDiscordStageChannel,
    MockDiscordForumChannel,
)


class DiscordDBGuildFunctionTests(TestCase):
    def setUp(self):
        self.client_model = Client.objects.create(
            id=102030405060708090,
            name="Client 1",
        )
        self.mock_discord_client = DiscordClient(self.client_model)
        self.mock_discord_guild_1 = MockDiscordGuild(123456789012345678, "Guild 1").get_mock()
        self.mock_discord_guild_2 = MockDiscordGuild(234567890123456789, "Guild 2").get_mock()
        self.guild_model_1 = Guild.objects.create(
            id=self.mock_discord_guild_1.id,
            name="Guild 0",
        )
        self.guild_model_2 = Guild.objects.create(
            id=self.mock_discord_guild_2.id,
            name=self.mock_discord_guild_2.name,
        )

    def test_create_or_update_guild(self):
        mock_discord_guild_3 = MockDiscordGuild(345678901234567890, "Guild 3").get_mock()

        self.assertEqual(Guild.objects.count(), 2)
        create_or_update_guild(mock_discord_guild_3)
        self.assertEqual(Guild.objects.count(), 3)
        self.assertEqual(Guild.objects.get(id=mock_discord_guild_3.id).name, mock_discord_guild_3.name)

        create_or_update_guild(self.mock_discord_guild_1)
        self.assertEqual(Guild.objects.get(id=self.mock_discord_guild_1.id).name, self.mock_discord_guild_1.name)

        self.assertEqual(Guild.objects.get(id=self.mock_discord_guild_1.id).active, True)
        create_or_update_guild(self.mock_discord_guild_1, active=False)
        self.assertEqual(Guild.objects.get(id=self.mock_discord_guild_1.id).active, False)

    def test_sync_guilds_with_db(self):
        with patch.object(commands.Bot, 'get_guild') as mock_get_guild:
            mock_get_guild.side_effect = lambda guild_id: guild_id == self.mock_discord_guild_1.id
            self.assertEqual(self.guild_model_2.active, True)
            sync_guilds_with_db(self.mock_discord_client)
            self.assertEqual(Guild.objects.get(id=self.guild_model_2.id).active, False)

    def test_remove_inactive_guilds(self):
        self.assertEqual(Guild.objects.count(), 2)
        self.guild_model_1.active = False
        self.guild_model_1.save()
        remove_inactive_guilds()
        self.assertEqual(Guild.objects.count(), 1)
        self.assertRaises(Guild.DoesNotExist, Guild.objects.get, id=self.guild_model_1.id)

class DiscordDBMemberFunctionTests(TestCase):
    def setUp(self):
        self.client_model = Client.objects.create(
            id=102030405060708090,
            name="Client 1",
        )
        self.mock_discord_client = DiscordClient(self.client_model)
        self.mock_discord_guild_1 = MockDiscordGuild(123456789012345678, "Guild 1").get_mock()
        self.mock_discord_guild_2 = MockDiscordGuild(234567890123456789, "Guild 2").get_mock()
        self.mock_discord_member_1 = MockDiscordMember(123456789012345678, "Member 1", self.mock_discord_guild_1, display_name='Nickname 1').get_mock()
        self.mock_discord_member_2 = MockDiscordMember(123456789012345679, "Member 2", self.mock_discord_guild_1).get_mock()
        self.mock_discord_member_3 = MockDiscordMember(123456789012345679, "Member 2", self.mock_discord_guild_2).get_mock()
        self.mock_discord_member_bot = MockDiscordMember(123456789012345670, "Member Bot", self.mock_discord_guild_1, bot=True).get_mock()

        self.guild_model_1 = Guild.objects.create(
            id=self.mock_discord_guild_1.id,
            name=self.mock_discord_guild_1.name,
        )
        self.guild_model_2 = Guild.objects.create(
            id=self.mock_discord_guild_2.id,
            name=self.mock_discord_guild_2.name,
        )
        self.citizen_model_1 = Citizen.objects.create(
            name=self.mock_discord_member_1.name
        )
        self.member_model_1 = Member.objects.create(
            id=self.mock_discord_member_1.id,
            name=self.mock_discord_member_1.name,
            citizen=self.citizen_model_1,
        )

    def test_create_or_update_member(self):
        self.assertEqual(Member.objects.count(), 1)
        create_or_update_member(self.mock_discord_member_1)
        self.assertEqual(Member.objects.count(), 1)
        self.assertEqual(Member.objects.get(id=self.mock_discord_member_1.id).name, self.mock_discord_member_1.name)
        self.assertEqual(Citizen.objects.get(id=self.citizen_model_1.id).name, self.mock_discord_member_1.display_name)

        create_or_update_member(self.mock_discord_member_2)
        self.assertEqual(Member.objects.count(), 2)
        self.assertEqual(Member.objects.get(id=self.mock_discord_member_2.id).name, self.mock_discord_member_2.name)
        self.assertListEqual(list(Member.objects.get(id=self.mock_discord_member_2.id).guilds.values_list('id', flat=True)), [str(self.mock_discord_guild_1.id)])

        create_or_update_member(self.mock_discord_member_3)
        self.assertEqual(Member.objects.count(), 2)
        self.assertEqual(Member.objects.get(id=self.mock_discord_member_3.id).name, self.mock_discord_member_3.name)
        self.assertListEqual(list(Member.objects.get(id=self.mock_discord_member_3.id).guilds.values_list('id', flat=True)), [str(self.mock_discord_guild_1.id), str(self.mock_discord_guild_2.id)])

        create_or_update_member(self.mock_discord_member_3, leaving_guild=True)
        self.assertEqual(Member.objects.count(), 2)
        self.assertListEqual(list(Member.objects.get(id=self.mock_discord_member_3.id).guilds.values_list('id', flat=True)), [str(self.mock_discord_guild_1.id)])

    def test_sync_members_with_db(self):
        with patch.object(commands.Bot, 'get_all_members') as mock_get_all_members:
            mock_get_all_members.return_value = [self.mock_discord_member_1, self.mock_discord_member_2, self.mock_discord_member_3, self.mock_discord_member_bot]
            self.assertEqual(Member.objects.count(), 1)
            self.assertEqual(Citizen.objects.count(), 1)
            members_synced = sync_members_with_db(self.mock_discord_client)
            self.assertEqual(members_synced, 1)
            self.assertEqual(Member.objects.count(), 2)
            self.assertEqual(Member.objects.get(id=self.member_model_1.id).name, "Member 1")
            self.assertRaises(Member.DoesNotExist, Member.objects.get, id=self.mock_discord_member_bot.id)

class DiscordDBChannelFunctionTests(TestCase):
    def setUp(self):
        self.client_model = Client.objects.create(
            id=102030405060708090,
            name="Client 1",
        )
        self.mock_discord_client = DiscordClient(self.client_model)
        self.mock_discord_guild = MockDiscordGuild(123456789012345670, "Guild 1").get_mock()
        self.guild_model = Guild.objects.create(
            id=self.mock_discord_guild.id,
            name=self.mock_discord_guild.name,
        )
        self.mock_discord_category = MockDiscordCategory(123456789012345672, "Category Channel 1", self.mock_discord_guild).get_mock()
        self.mock_discord_text_channel = MockDiscordTextChannel(123456789012345674, "Text Channel 1", self.mock_discord_guild).get_mock()
        self.mock_discord_voice_channel = MockDiscordVoiceChannel(123456789012345676, "Voice Channel 1", self.mock_discord_guild).get_mock()
        self.mock_discord_stage_channel = MockDiscordStageChannel(123456789012345678, "Stage Channel 1", self.mock_discord_guild).get_mock()
        self.mock_discord_forum_channel = MockDiscordForumChannel(123456789012345680, "Forum Channel 1", self.mock_discord_guild).get_mock()
        self.mock_discord_guild.channels = [
            self.mock_discord_category,
            self.mock_discord_text_channel,
            self.mock_discord_voice_channel,
            self.mock_discord_stage_channel,
            self.mock_discord_forum_channel,
        ]

    def test_create_or_update_channel(self):
        create_or_update_channel(self.mock_discord_category, self.mock_discord_guild.id)
        self.assertEqual(Category.objects.count(), 1)
        create_or_update_channel(self.mock_discord_category, self.mock_discord_guild.id, remove=True)
        self.assertEqual(Category.objects.count(), 0)

    def test_sync_channels_with_db(self):
        with patch.object(commands.Bot, 'guilds', new_callable=PropertyMock) as mock_guilds:
            mock_guilds.return_value = [self.mock_discord_guild]
            self.assertEqual(Category.objects.count(), 0)
            self.assertEqual(TextChannel.objects.count(), 0)
            self.assertEqual(VoiceChannel.objects.count(), 0)
            self.assertEqual(StageChannel.objects.count(), 0)
            self.assertEqual(ForumChannel.objects.count(), 0)
            channels_synced = sync_channels_with_db(self.mock_discord_client)
            self.assertEqual(channels_synced, 5)
            self.assertEqual(Category.objects.count(), 1)
            self.assertEqual(TextChannel.objects.count(), 1)
            self.assertEqual(VoiceChannel.objects.count(), 1)
            self.assertEqual(StageChannel.objects.count(), 1)
            self.assertEqual(ForumChannel.objects.count(), 1)
            channels_synced_2 = sync_channels_with_db(self.mock_discord_client)
            self.assertEqual(channels_synced_2, 0)
