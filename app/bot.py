import os
import time
import threading
from pyrogram import Client, filters
from app.plugins.url_add import url_add_handler
from app.plugins.check import check_handler
from app.config import API_ID, API_HASH, BOT_TOKEN
from app.task_manager import process_tasks, start_task_processing

# Initialize the Pyrogram Client
bot_app = Client("url_uploader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start task processing in the background
start_task_processing()

# Add handlers for the commands
bot_app.add_handler(url_add_handler)
bot_app.add_handler(check_handler)

# Run the bot
if __name__ == '__main__':
    bot_app.run()
