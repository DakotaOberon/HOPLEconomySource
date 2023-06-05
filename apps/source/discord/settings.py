from decouple import config


# Paths to extensions
COMMAND_EXTENSIONS = [
    'apps.source.discord.extensions.develop',
    'apps.source.discord.extensions.example',
    'apps.source.discord.extensions.discord_db'
]

# Where slash commands will be locally synced to for testing
TEST_SERVER_ID = config("TEST_SERVER_ID")
