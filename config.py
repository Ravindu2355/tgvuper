import os

# Configuration settings for your bot
API_ID = os.getenv('apiid')  # Get from https://my.telegram.org/auth
API_HASH = os.getenv('apihash')  # Get from https://my.telegram.org/auth
BOT_TOKEN = os.getenv('tk')  # Get from @BotFather
authU =os.getenv('auth')
sl_time =os.getenv('sleep')
# Flask server settings
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 8000
