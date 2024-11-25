import os
import time
import threading
from pyrogram import Client, filters ,types
from plugins.url_add import url_add_handler
from plugins.check import check_handler
from config import API_ID, API_HASH, BOT_TOKEN
from task_manager import process_tasks, start_task_processing

# Initialize the Pyrogram Client
plugins = dict(root="plugins")
bot = Client(name="RVX_bot", bot_token=Config.BOT_TOKEN, api_id=Config.API_ID, api_hash=Config.API_HASH, plugins=plugins)

# Start task processing in the background
start_task_processing(bot)

@bot.on_message(filters.command("start"))
async def _ms(client, message:types.Message):
    await message.reply("okkk")
# Add handlers for the commands
#bot.add_handler(url_add_handler)
#bot.add_handler(check_handler)

# Run the bot
if __name__ == '__main__':
    bot_app.run()
