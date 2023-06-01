from decouple import config


# Paths to extensions
COMMAND_EXTENSIONS = [
    'apps.source.discord.extensions.develop',
    'apps.source.discord.extensions.example',
]

# Where slash commands will be locally synced to for testing
TEST_SERVER_ID = config("TEST_SERVER_ID")

# ID of role that can run admin commands
ADMIN_ROLE_ID = config("ADMIN_ROLE_ID")
