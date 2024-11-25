from pyrogram import filters

# Handler for the /check command
async def check_handler(client, message):
    if message.text.startswith("/check"):
        # Check the number of tasks in the task list
        if task_list:
            task_count = len(task_list)
            await client.send_message(message.chat.id, f"There are {task_count} tasks in the queue.")
        else:
            await client.send_message(message.chat.id, "There are no tasks in the queue.")
