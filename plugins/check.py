from pyrogram import Client, filters, types
from task_manager import task_list

# Handler for the /check command
@Client.on_message(filters.command("check"))
async def check_handler(client, message):
   if task_list:
         task_count = len(task_list)
         await client.send_message(message.chat.id, f"There are {task_count} tasks in the queue.")
   else:
         await client.send_message(message.chat.id, "There are no tasks in the queue.")
