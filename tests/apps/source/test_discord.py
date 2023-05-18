from django.test import TestCase

from apps.source.discord.models import Guild, TextChannel, VoiceChannel


class GuildModelTests(TestCase):
    def setUp(self):
        self.guild = Guild.objects.create(
            name="Test Guild",
            discord_id=123456789012345678
        )

    def test_str(self):
        self.assertEqual(str(self.guild), "Test Guild")

class TextChannelModelTests(TestCase):
    def setUp(self):
        self.guild = Guild.objects.create(
            name="Test Guild",
            discord_id=123456789012345678
        )
        self.channel = TextChannel.objects.create(
            name="Test Channel",
            discord_id=123456789012345678,
            guild=self.guild
        )

    def test_str(self):
        self.assertEqual(str(self.channel), "#Test Channel")

class VoiceChannelModelTests(TestCase):
    def setUp(self):
        self.guild = Guild.objects.create(
            name="Test Guild",
            discord_id=123456789012345678
        )
        self.channel = VoiceChannel.objects.create(
            name="Test Channel",
            discord_id=123456789012345678,
            guild=self.guild
        )

    def test_str(self):
        self.assertEqual(str(self.channel), "<Test Channel")
