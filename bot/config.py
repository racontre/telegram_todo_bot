"""
Sets the bot token from an environment variable.
"""

import os
BOT_TOKEN = ""
OWNER_ID = 123455673


BOT_TOKEN = os.environ.get('BOT_TOKEN', BOT_TOKEN)
