from pyrogram import filters
from task_manager import add_task_to_list

# Handler for the /url_add command
async def url_add_handler(client, message):
    if message.text.startswith("/url_add"):
        # Check if the message has the correct format
        parts = message.text.split(" ", 2)
        if len(parts) < 3:
            await client.send_message(message.chat.id, "Please provide a URL and optional thumbnail: /url_add <url> <thumbnail_url>")
            return
        
        url = parts[1]
        thumbnail_url = parts[2] if len(parts) > 2 else None
        
        # Add the task to the task list
        add_task_to_list(url, message.chat.id, thumbnail_url)
        await client.send_message(message.chat.id, f"Task added for URL: {url}")
