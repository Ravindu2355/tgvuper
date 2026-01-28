from pyrogram import Client, filters, types
import globals
from config import authU

@Client.on_message(filters.command("change_proxy") & filters.private)
async def view_regex(client, message):
    global globals
    parts = message.text.split(" ")
     #if str(message.chat.id) in authU:
      if len(parts) < 2:
          await client.send_message(message.chat.id, "Please provide a URL and optional /change_proxy <url>")
          return
      url = parts[1]
      globals.proxyurl = url
      await message.reply(f"Setuped : {globals.proxyurl}")
