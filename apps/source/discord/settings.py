from decouple import config


# Paths to extensions
COMMAND_EXTENSIONS = [
    # Example extension
    'apps.source.discord.extensions.example',

    # Source
    'apps.source.discord.extensions.develop',
    'apps.source.discord.extensions.discord_db',
    'apps.source.discord.extensions.events',
    'apps.source.activity.extensions.activity',
    'apps.source.activity.extensions.voice',
]

# Where slash commands will be locally synced to for testing
TEST_SERVER_ID = config("TEST_SERVER_ID")
