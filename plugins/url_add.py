from pyrogram import Client, filters, types
from task_manager import add_task_to_list, start_task_processing
from config import authU

@Client.on_message(filters.regex("yt"))
async def url_add_handler_yt(client, message):
     parts = message.text.split(" ")
     if str(message.chat.id) in authU:
        if len(parts) < 2:
            await client.send_message(message.chat.id, "Please provide a URL and optional thumbnail: /yt <url> <thumbnail_url>")
            return
        url = parts[1]
        type="yt_direct"
        add_task_to_list(url, message.chat.id, thumbnail_url = None,type=type)
        await client.send_message(message.chat.id, f"Task added for URL: {url}")
     else:
        await client.send_message(message.chat.id,"Sorry You are not user😄")
          
# Handler for the /url_add command
@Client.on_message(filters.regex("url_add"))
async def url_add_handler(client, message):
     parts = message.text.split(" ")
     if str(message.chat.id) in authU:
        if len(parts) < 2:
            await client.send_message(message.chat.id, "Please provide a URL and optional thumbnail: /url_add <url> <thumbnail_url>")
            return
        url = parts[1]
        thumbnail_url = None #parts[2] if len(parts) > 2 else None
        # Add the task to the task list
        add_task_to_list(url, message.chat.id, thumbnail_url)
        await client.send_message(message.chat.id, f"Task added for URL: {url}")
     else:
        await client.send_message(message.chat.id,"Sorry You are not user😄")

#@Client.on_message(filters.regex("http"))
async def old_p_url(client,message):
        id = str(message.chat.id)
        if id in authU:
            url= message.text
            type=None
            if '.html' in url:
                 type="desi_page"
            add_task_to_list(url, message.chat.id, thumbnail_url=None,type=type)
            await message.reply(f"Task added for URL: {url}")
        else:
            await message.reply("Sorry You are not user😄")
from pyrogram import Client, filters
from urllib.parse import urlparse
import os

@Client.on_message(filters.regex(r"https?://"))
async def p_url(client, message):
    id = str(message.chat.id)

    if id not in authU:
        await message.reply("Sorry You are not user😄")
        return

    url = message.text.strip()
    type = None

    # ✅ Extract file extension from URL path
    path = urlparse(url).path
    ext = os.path.splitext(path)[1].lower()

    # ✅ DIRECT FILE TYPES
    direct_exts = [
        ".mp4", ".mkv", ".avi", ".mov", ".webm",
        ".mp3", ".wav", ".flac",
        ".zip", ".rar", ".7z",
        ".pdf", ".apk", ".exe"
    ]

    if ext in direct_exts:
        type = "direct_file"

    # ✅ PAGE TYPES
    elif ext in [".html", ".php", ".asp", ".aspx", ""]:
        type = "page_url"

    else:
        type = "unknown"

    # ✅ Add task
    add_task_to_list(
        url,
        message.chat.id,
        thumbnail_url=None,
        type=type
    )

    await message.reply(f"✅ Task added as: `{type}`\n🔗 URL: {url}")
     
