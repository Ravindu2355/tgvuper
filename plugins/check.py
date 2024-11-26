from pyrogram import Client, filters, types
from task_manager import  s
from globals

# Handler for the /check command
@Client.on_message(filters.command("check"))
async def check_handler(client, message):
   if globals.task_list:
         task_count = len(globals.task_list)
         await client.send_message(message.chat.id, f"There are {task_count} tasks in the queue.And process fun runed {s} times")
   else:
         await client.send_message(message.chat.id, "There are no tasks in the queue.")
