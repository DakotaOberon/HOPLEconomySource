from unittest.mock import patch, PropertyMock, MagicMock

import discord
from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from discord.ext import commands

from apps.source.discord.client import DiscordClient
from apps.source.discord.models import (
    Guild,
    Member,
    Channel,
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


class GuildModelTests(TestCase):
    def setUp(self):
        self.guild = Guild.objects.create(
            id=123456789012345678,
            name="Test Guild"
        )

    def test_id_too_short(self):
        with self.assertRaises(ValidationError):
            guild = Guild.objects.create(
                id=123456789,
                name="Test Guild 2"
            )
            guild.full_clean()

    def test_id_too_long(self):
        with self.assertRaises(ValidationError):
            guild = Guild.objects.create(
                id=12345678901234567890,
                name="Test Guild 2"
            )
            guild.full_clean()

    def test_default_name(self):
        guild = Guild.objects.create(
            id=123456789012345670
        )
        self.assertEqual(guild.name, "Guild")

    def test_str(self):
        self.assertEqual(str(self.guild), "Test Guild")

    def test_repr(self):
        self.assertEqual(repr(self.guild), "Guild(Test Guild)")

class MemberModelTests(TestCase):
    def setUp(self):
        self.guild = Guild.objects.create(
            id=123456789012345678,
            name="Test Guild"
        )
        self.citizen = Citizen.objects.create(
            name="Test Citizen"
        )
        self.citizen2 = Citizen.objects.create(
            name="Test Citizen 2"
        )
        self.member = Member.objects.create(
            id=123456789012345678,
            name="Test Member",
            citizen=self.citizen,
        )
        self.member.guilds.add(self.guild)

    def test_id_too_short(self):
        with self.assertRaises(ValidationError):
            member = Member.objects.create(
                id=123456789,
                name="Test Member 2",
                citizen=self.citizen2
            )
            member.full_clean()

    def test_id_too_long(self):
        with self.assertRaises(ValidationError):
            member = Member.objects.create(
                id=12345678901234567890,
                name="Test Member 2",
                citizen=self.citizen2
            )
            member.full_clean()

    def test_default_name(self):
        member = Member.objects.create(
            id=123456789012345670,
            citizen=self.citizen2
        )
        self.assertEqual(member.name, "Member")

    def test_unique_citizen(self):
        with self.assertRaises(IntegrityError):
            member = Member.objects.create(
                id=123456789012345671,
                name="Test Member 3",
                citizen=self.citizen
            )
            member.full_clean()

    def test_str(self):
        self.assertEqual(str(self.member), "Test Member")

    def test_repr(self):
        self.assertEqual(repr(self.member), "Member(Test Member)")

    def test_citizen_deletion_cascade(self):
        self.assertEqual(Member.objects.count(), 1)
        self.citizen.delete()
        self.assertEqual(Member.objects.count(), 0)

class ChannelModelTests(TestCase):
    def test_abstract(self):
        with self.assertRaises(AttributeError):
            Channel.objects.create(
                id=123456789012345678,
                name="Test Channel"
            )

class TextChannelModelTests(TestCase):
    def setUp(self):
        self.guild = Guild.objects.create(
            id=123456789012345678,
            name="Test Guild"
        )
        self.channel = TextChannel.objects.create(
            id=123456789012345678,
            name="Test Channel",
            guild=self.guild
        )

    def test_id_too_short(self):
        with self.assertRaises(ValidationError):
            channel = TextChannel.objects.create(
                id=123456789,
                name="Test Channel 2",
                guild=self.guild
            )
            channel.full_clean()

    def test_id_too_long(self):
        with self.assertRaises(ValidationError):
            channel = TextChannel.objects.create(
                id=12345678901234567890,
                name="Test Channel 2",
                guild=self.guild
            )
            channel.full_clean()

    def test_default_name(self):
        channel = TextChannel.objects.create(
            id=123456789012345670,
            guild=self.guild
        )
        self.assertEqual(channel.name, "Channel")

    def test_access_text_channel_from_guild(self):
        self.assertEqual(self.guild.text_channels.first().id, str(self.channel.id))

    def test_str(self):
        self.assertEqual(str(self.channel), "#Test Channel")

    def test_repr(self):
        self.assertEqual(repr(self.channel), "TextChannel(Test Channel)")

    def test_guild_deletion_cascade(self):
        self.assertEqual(TextChannel.objects.count(), 1)
        self.guild.delete()
        self.assertEqual(TextChannel.objects.count(), 0)

class VoiceChannelModelTests(TestCase):
    def setUp(self):
        self.guild = Guild.objects.create(
            id=123456789012345678,
            name="Test Guild"
        )
        self.channel = VoiceChannel.objects.create(
            id=123456789012345678,
            name="Test Channel",
            guild=self.guild
        )

    def test_id_too_short(self):
        with self.assertRaises(ValidationError):
            channel = VoiceChannel.objects.create(
                id=123456789,
                name="Test Channel 2",
                guild=self.guild
            )
            channel.full_clean()

    def test_id_too_long(self):
        with self.assertRaises(ValidationError):
            channel = VoiceChannel.objects.create(
                id=12345678901234567890,
                name="Test Channel 2",
                guild=self.guild
            )
            channel.full_clean()

    def test_default_name(self):
        channel = VoiceChannel.objects.create(
            id=123456789012345670,
            guild=self.guild
        )
        self.assertEqual(channel.name, "Channel")

    def test_access_voice_channel_from_guild(self):
        self.assertEqual(self.guild.voice_channels.first().id, str(self.channel.id))

    def test_str(self):
        self.assertEqual(str(self.channel), "#Test Channel")

    def test_repr(self):
        self.assertEqual(repr(self.channel), "VoiceChannel(Test Channel)")

    def test_guild_deletion_cascade(self):
        self.assertEqual(VoiceChannel.objects.count(), 1)
        self.guild.delete()
        self.assertEqual(VoiceChannel.objects.count(), 0)

class DiscordDBExtensionTest(TestCase):
    def setUp(self):
        self.client_model = Client.objects.create(
            id=123456789012345678,
            name="Test Client"
        )
        self.mock_client = DiscordClient(client_model=self.client_model)

        self.mock_guild_1 = MagicMock(spec=discord.Guild)
        self.mock_guild_1.id = 123456789012345678
        self.mock_guild_1.name = "Test Guild 1"

        self.mock_guild_2 = MagicMock(spec=discord.Guild)
        self.mock_guild_2.id = 123456789012345679
        self.mock_guild_2.name = "Test Guild 2"

        self.mock_member_1 = MagicMock(spec=discord.Member)
        self.mock_member_1.id = 123456789012345671
        self.mock_member_1.name = "Test Member 1"
        self.mock_member_1.display_name = "Display Name 1"
        self.mock_member_1.guild = self.mock_guild_1
        self.mock_member_1.bot = False

        self.mock_member_2 = MagicMock(spec=discord.Member)
        self.mock_member_2.id = 123456789012345672
        self.mock_member_2.name = "Test Member 2"
        self.mock_member_2.display_name = "Test Member 2"
        self.mock_member_2.guild = self.mock_guild_1
        self.mock_member_2.bot = False
        self.mock_member_3 = MagicMock(spec=discord.Member)
        self.mock_member_3.id = 123456789012345672
        self.mock_member_3.name = "Test Member 2"
        self.mock_member_3.display_name = "Test Member 2"
        self.mock_member_3.guild = self.mock_guild_2
        self.mock_member_3.bot = False

        self.guild_1 = Guild.objects.create(
            id=123456789012345678,
            name="Test Guild 0"
        )
        self.guild_2 = Guild.objects.create(
            id=123456789012345679,
            name="Test Guild 2"
        )
        self.citizen_1 = Citizen.objects.create(
            id=123456789012345671,
            name="Test Member 1",
        )
        self.member_1 = Member.objects.create(
            id=123456789012345671,
            name='Test Member 0',
            citizen=self.citizen_1
        )

    def test_create_or_update_guild(self):
        mock_guild_3 = MagicMock(spec=discord.Guild)
        mock_guild_3.id = 123456789012345680
        mock_guild_3.name = "Test Guild 3"

        self.assertEqual(Guild.objects.count(), 2)
        create_or_update_guild(mock_guild_3)
        self.assertEqual(Guild.objects.count(), 3)
        self.assertEqual(Guild.objects.get(id=mock_guild_3.id).name, mock_guild_3.name)

        create_or_update_guild(self.mock_guild_1)
        self.assertEqual(Guild.objects.get(id=self.mock_guild_1.id).name, self.mock_guild_1.name)
        self.assertEqual(Guild.objects.get(id=self.mock_guild_1.id).active, True)

        create_or_update_guild(self.mock_guild_1, active=False)
        self.assertEqual(Guild.objects.get(id=self.mock_guild_1.id).active, False)

    def test_create_or_update_member(self):
        self.assertEqual(Member.objects.count(), 1)
        create_or_update_member(self.mock_member_1)
        self.assertEqual(Member.objects.count(), 1)
        self.assertEqual(Member.objects.get(id=self.mock_member_1.id).name, self.mock_member_1.name)

        create_or_update_member(self.mock_member_2)
        self.assertEqual(Member.objects.count(), 2)
        self.assertEqual(Member.objects.get(id=self.mock_member_2.id).name, self.mock_member_2.name)
        self.assertListEqual(list(Member.objects.get(id=self.mock_member_2.id).guilds.values_list('id', flat=True)), [str(self.mock_guild_1.id)])

        create_or_update_member(self.mock_member_3)
        self.assertEqual(Member.objects.count(), 2)
        self.assertEqual(Member.objects.get(id=self.mock_member_3.id).name, self.mock_member_3.name)
        self.assertListEqual(list(Member.objects.get(id=self.mock_member_3.id).guilds.values_list('id', flat=True)), [str(self.mock_guild_1.id), str(self.mock_guild_2.id)])

        create_or_update_member(self.mock_member_3, leaving_guild=True)
        self.assertEqual(Member.objects.count(), 2)
        self.assertListEqual(list(Member.objects.get(id=self.mock_member_3.id).guilds.values_list('id', flat=True)), [str(self.mock_guild_1.id)])

    def test_sync_guilds_with_db_active_switch(self):
        with patch.object(commands.Bot, 'get_guild') as mock_get_guild:
            mock_get_guild.side_effect = lambda guild_id: guild_id == self.mock_guild_1.id
            self.assertEqual(self.guild_2.active, True)
            sync_guilds_with_db(self.mock_client)
            self.assertEqual(Guild.objects.get(id=self.guild_2.id).active, False)

    def test_sync_guilds_with_db_add_and_update_guilds_in_db(self):
        with patch.object(commands.Bot, 'guilds', new_callable=PropertyMock) as mock_guilds:
            mock_guild_3 = MagicMock(spec=discord.Guild)
            mock_guild_3.id = 123456789012345680
            mock_guild_3.name = "Test Guild 3"
            mock_guilds.return_value = [self.mock_guild_1, self.mock_guild_2, mock_guild_3]
            self.assertEqual(Guild.objects.count(), 2)
            self.assertEqual(Guild.objects.get(id=self.mock_guild_1.id).name, "Test Guild 0")
            guilds_synced = sync_guilds_with_db(self.mock_client)
            self.assertEqual(guilds_synced, 1)
            self.assertEqual(Guild.objects.count(), 3)
            self.assertEqual(Guild.objects.get(id=self.mock_guild_1.id).name, "Test Guild 1")

    def test_remove_inactive_guilds(self):
        self.assertEqual(Guild.objects.count(), 2)
        self.guild_1.active = False
        self.guild_1.save()
        remove_inactive_guilds()
        self.assertEqual(Guild.objects.count(), 1)
        self.assertRaises(Guild.DoesNotExist, Guild.objects.get, id=self.guild_1.id)

    def test_sync_members_with_db(self):
        member_as_bot = MagicMock(spec=discord.Member)
        member_as_bot.id = 123456789012345670
        member_as_bot.name = "Test Member Bot"
        member_as_bot.display_name = "Test Member Bot"
        member_as_bot.guild = self.mock_guild_1
        member_as_bot.bot = True
        with patch.object(commands.Bot, 'get_all_members') as mock_get_all_members:
            mock_get_all_members.return_value = [self.mock_member_1, self.mock_member_2, self.mock_member_3, member_as_bot]
            self.assertEqual(Member.objects.count(), 1)
            self.assertEqual(Citizen.objects.count(), 1)
            members_synced = sync_members_with_db(self.mock_client)
            self.assertEqual(members_synced, 1)
            self.assertEqual(Member.objects.count(), 2)
            self.assertEqual(Member.objects.get(id=self.member_1.id).name, "Test Member 1")
            self.assertRaises(Member.DoesNotExist, Member.objects.get, id=member_as_bot.id)

    def test_sync_channels_with_db_and_create_or_update_channel(self):
        mock_category = MagicMock(spec=discord.CategoryChannel)
        mock_category.id = 223456789012345670
        mock_category.name = "Test Category"
        mock_text_channel_1 = MagicMock(spec=discord.TextChannel)
        mock_text_channel_1.id = 123456789012345671
        mock_text_channel_1.name = "Test Text Channel 1"
        mock_text_channel_1.permissions_for.return_value.view_channel = True
        mock_text_channel_1.guild = self.mock_guild_1
        mock_text_channel_2 = MagicMock(spec=discord.TextChannel)
        mock_text_channel_2.id = 123456789012345672
        mock_text_channel_2.name = "Test Text Channel 2"
        mock_text_channel_2.permissions_for.return_value.view_channel = False
        mock_text_channel_2.guild = self.mock_guild_1
        mock_voice_channel_1 = MagicMock(spec=discord.VoiceChannel)
        mock_voice_channel_1.id = 123456789012345674
        mock_voice_channel_1.name = "Test Voice Channel 1"
        mock_voice_channel_1.permissions_for.return_value.view_channel = True
        mock_voice_channel_1.guild = self.mock_guild_1
        mock_stage_channel_1 = MagicMock(spec=discord.StageChannel)
        mock_stage_channel_1.id = 123456789012345675
        mock_stage_channel_1.name = "Test Stage Channel 1"
        mock_stage_channel_1.permissions_for.return_value.view_channel = True
        mock_stage_channel_1.guild = self.mock_guild_1
        mock_forum_channel_1 = MagicMock(spec=discord.ForumChannel)
        mock_forum_channel_1.id = 123456789012345676
        mock_forum_channel_1.name = "Test Forum Channel 1"
        mock_forum_channel_1.permissions_for.return_value.view_channel = True
        mock_forum_channel_1.guild = self.mock_guild_1
        self.mock_guild_1.channels = [mock_category, mock_text_channel_1, mock_text_channel_2, mock_voice_channel_1, mock_stage_channel_1, mock_forum_channel_1]

        # Test sync_channels_with_db
        with patch.object(commands.Bot, 'guilds', new_callable=PropertyMock) as mock_guilds:
            mock_guilds.return_value = [self.mock_guild_1]
            self.assertEqual(Category.objects.count(), 0)
            self.assertEqual(TextChannel.objects.count(), 0)
            self.assertEqual(VoiceChannel.objects.count(), 0)
            self.assertEqual(StageChannel.objects.count(), 0)
            self.assertEqual(ForumChannel.objects.count(), 0)
            channels_synced = sync_channels_with_db(self.mock_client)
            self.assertEqual(channels_synced, 5)
            self.assertEqual(Category.objects.count(), 1)
            self.assertEqual(TextChannel.objects.count(), 1)
            self.assertEqual(VoiceChannel.objects.count(), 1)
            self.assertEqual(StageChannel.objects.count(), 1)
            self.assertEqual(ForumChannel.objects.count(), 1)
            channels_synced_2 = sync_channels_with_db(self.mock_client)
            self.assertEqual(channels_synced_2, 0)

        # Test create_or_update_channel
        create_or_update_channel(mock_category, self.mock_guild_1.id, remove=True)
        self.assertEqual(Category.objects.count(), 0)
        create_or_update_channel(mock_category, self.mock_guild_1.id)
        self.assertEqual(Category.objects.count(), 1)