import threading
import os, asyncio
import time
import requests
from utils import generate_thumbnail, download_file, upload_file_to_telegram

# Task list to hold URL tasks
task_list = []
running=0

# Function to add a task to the task list
def add_task_to_list(url, chat_id, thumbnail_url=None):
    task = {
        'url': url,
        'chat_id': chat_id,
        'thumbnail_url': thumbnail_url
    }
    task_list.append(task)

# Function to process tasks from the task list
async def process_tasks(client):
    while True:
        if task_list and running == 0:
            running=1
            task = task_list.pop(0)  # Get the first task in the list
            url = task['url']
            chat_id = task['chat_id']
            thumbnail_url = task['thumbnail_url']
            msg= await client.send_message(chat_id,"Starting Task!")
            # Download the file from the URL
            file_path = download_file(client, msg, url, "downloaded_file", chat_id)
            if file_path:  # Only upload if the file was successfully downloaded
                # Upload the file to Telegram
                upload_file_to_telegram(client, msg, task, file_path)
            
                # Clean up downloaded file after upload
                if os.path.exists(file_path):
                    os.remove(file_path)
                    await msg.delete()
                    running = 0 
    
        await asyncio.sleep(2)  # Wait 2 seconds before checking again

# Start the task processing in a background thread
def start_task_processing(client):
    thread = threading.Thread(target=process_tasks, args=(client,))
    thread.daemon = True
    thread.start()
