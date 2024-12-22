import os

# Configuration settings for your bot
API_ID = os.getenv('apiid')  # Get from https://my.telegram.org/auth
API_HASH = os.getenv('apihash')  # Get from https://my.telegram.org/auth
BOT_TOKEN = os.getenv('tk')  # Get from @BotFather
authU = os.getenv('auth')
TgSizeLimit = int(os.getenv('tglimit') or 2147483648)
sleep_time = int(os.getenv('sleep') or 30)
try:
    sleep_time = int(sleep_time)
except ValueError:
    sleep_time = 30

# Flask server settings
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 8000
