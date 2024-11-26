import os
import time
from threading import Thread
from pyrogram import Client, filters ,types
from plugins.url_add import url_add_handler
from plugins.check import check_handler
from config import API_ID, API_HASH, BOT_TOKEN
from task_manager import process_tasks, start_task_processing
from flask_server import start_fls

# Initialize the Pyrogram Client
plugins = dict(root="plugins")
bot = Client(name="RVX_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH, plugins=plugins)

# Start task processing in the background
start_task_processing(bot)



@bot.on_message(filters.command("start"))
async def _ms(client, message:types.Message):
    await message.reply("okkk")
# Add handlers for the commands
#bot.add_handler(url_add_handler)
#bot.add_handler(check_handler)

flask_t= Thread(target=start_fls)
flask_t.start()
# Run the bot
if __name__ == '__main__':
    bot.run()
