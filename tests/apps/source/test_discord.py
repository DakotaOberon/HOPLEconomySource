from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from apps.source.discord.models import Guild, Member, Channel, TextChannel, VoiceChannel
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
        self.assertEqual(str(self.channel), "<Test Channel")

    def test_repr(self):
        self.assertEqual(repr(self.channel), "VoiceChannel(Test Channel)")
    
    def test_guild_deletion_cascade(self):
        self.assertEqual(VoiceChannel.objects.count(), 1)
        self.guild.delete()
        self.assertEqual(VoiceChannel.objects.count(), 0)
