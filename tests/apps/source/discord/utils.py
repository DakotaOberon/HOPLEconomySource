from unittest.mock import MagicMock

import discord


class MockDiscordClass():
    def __init__(self, spec):
        self.mock = MagicMock(spec=spec)

    def get_mock(self):
        return self.mock

class MockDiscordGuild(MockDiscordClass):
    def __init__(self, guild_id, name):
        super().__init__(discord.Guild)
        self.mock.id = guild_id
        self.mock.name = name

class MockDiscordMember(MockDiscordClass):
    def __init__(self, member_id, name, guild, display_name=None, bot=False):
        super().__init__(discord.Member)
        self.mock.id = member_id
        self.mock.name = name
        self.mock.display_name = display_name if display_name else name
        self.mock.bot = bot
        self.mock.guild = guild

class MockDiscordCategory(MockDiscordClass):
    def __init__(self, channel_id, name, guild):
        super().__init__(spec=discord.CategoryChannel)
        self.mock.id = channel_id
        self.mock.name = name
        self.mock.guild = guild

class MockDiscordTextChannel(MockDiscordClass):
    def __init__(self, channel_id, name, guild, category=None):
        super().__init__(spec=discord.TextChannel)
        self.mock.id = channel_id
        self.mock.name = name
        self.mock.guild = guild
        self.mock.category = category

class MockDiscordVoiceChannel(MockDiscordClass):
    def __init__(self, channel_id, name, guild, category=None):
        super().__init__(spec=discord.VoiceChannel)
        self.mock.id = channel_id
        self.mock.name = name
        self.mock.guild = guild
        self.mock.category = category

class MockDiscordStageChannel(MockDiscordClass):
    def __init__(self, channel_id, name, guild, category=None):
        super().__init__(spec=discord.StageChannel)
        self.mock.id = channel_id
        self.mock.name = name
        self.mock.guild = guild
        self.mock.category = category

class MockDiscordForumChannel(MockDiscordClass):
    def __init__(self, channel_id, name, guild, category=None):
        super().__init__(spec=discord.ForumChannel)
        self.mock.id = channel_id
        self.mock.name = name
        self.mock.guild = guild
        self.mock.category = category
