from pyrogram import Client, filters, types
from task_manager import  s
import globals
from config import authU

# Command to change the regex
@app.on_message(filters.command("change_regex") & filters.private)
async def change_regex(client, message):
    # Check if the user provided a new regex
    global globals
    if str(message.chat.id) not in authU:
       await message.reply("**Not authed!...**")
       return
    if len(message.command) < 2:
        await message.reply("Usage: /change_regex <new_regex>")
        return
    
    # Get the new regex from the command arguments
    new_regex = " ".join(message.command[1:])
    
    # Update the patterns dictionary
    globals.patterns["bunkr_video"] = new_regex
    
    # Confirm the change to the user
    await message.reply(f"Regex for 'bunkr_video' has been updated to: `{new_regex}`", parse_mode="markdown")

# Command to view the current regex
@app.on_message(filters.command("view_regex") & filters.private)
async def view_regex(client, message):
    current_regex = globals.patterns.get("bunkr_video", "Not set")
    await message.reply(f"Current regex for 'bunkr_video': `{current_regex}`", parse_mode="markdown")


# Handler for the /check command
@Client.on_message(filters.command("check"))
async def check_handler(client, message):
   if globals.task_list:
         task_count = len(globals.task_list)
         await client.send_message(message.chat.id, f"There are {task_count} tasks in the queue.And process fun runed {s} times")
   else:
         await client.send_message(message.chat.id, "There are no tasks in the queue.")
