VOICE_CONFIG = {
    'TICK_RATE': 1,             # Time in seconds between each tick. Times will be off if you don't use a whole number or a number that fits smoothly into 1 such as 0.25. Default: 1 tick per second
    'TICKS_PER_REWARD': 60,     # Ticks until user gets points. Default: 60 ticks (1 minute) until user gets a point
    'BASE_POINT_REWARD': 1,     # Value of reward. Default: 1 base point per reward
    'REWARDS_PER_DAY': 100,     # How many rewards a user can earn per day. Default: 100
    'REWARD_RESET_TIME': 0,     # Time in hours when rewards reset. Default: Midnight local time

    'MULTIPLIERS_ENABLED': True, # Whether or not to enable multipliers. Default: True
    'MULTIPLIERS': {
        # Multipliers are added together and then multiplied by the base point reward
        'BASE': 1,              # Base multiplier. Default: 1
        'WEEKEND': 0.5,         # Multiplier for weekends. Default: 0.5 (50%)
        'HOLIDAY': 1,           # Multiplier for holidays. Default: 1 (100%)
        'BIRTHDAY': 2,          # Multiplier for birthdays. Default: 2 (200%)
        'VIDEO': 0.04,          # Multiplier for having camera on. Default 0.04 (4%)
        'STREAMING': 0.06,      # Multiplier for streaming. Default 0.06 (6%)
        'DEAF': -0.12,          # Multiplier for being deafened. Default -0.12 (-12%)
        'MUTE': -0.01,          # Multiplier for being muted. Default -0.01 (-1%)
        'GROUP': 0.01,          # Multiplier for being in a group. Default 0.01 (1%)
        'GROUP_MAX': 0.1,       # Max multiplier for being in a group. Default 0.1 (10%)
    },

    'DECIMAL_PLACES': 2,        # How many decimal places to round to. This helps avoid floating point errors. Default: 2
}
