import os
import time
import threading
import requests
from pyrogram import Client
from mimetypes import guess_type
from app.utils import generate_thumbnail, download_file, upload_file_to_telegram
from app.config import API_ID, API_HASH, BOT_TOKEN

# Initialize the Pyrogram Client
bot_app = Client("url_uploader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Task list to hold URL tasks
task_list = []

# Function to add a task to the task list
def add_task_to_list(url, chat_id, thumbnail_url=None):
    task = {
        'url': url,
        'chat_id': chat_id,
        'thumbnail_url': thumbnail_url
    }
    task_list.append(task)
    print(f"Task added: {task}")

# Function to process tasks from the task list
def process_tasks():
    while True:
        if task_list:
            task = task_list.pop(0)  # Get the first task in the list
            url = task['url']
            chat_id = task['chat_id']
            thumbnail_url = task['thumbnail_url']
            
            # Download the file from the URL
            file_path = download_file(url, "downloaded_file", chat_id)
            # Upload the file to Telegram
            upload_file_to_telegram(task, file_path)
            
            # Clean up downloaded file after upload
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up: {file_path}")
        
        time.sleep(2)  # Wait 2 seconds before checking again

# Start the task processing thread
def start_task_processing():
    thread = threading.Thread(target=process_tasks)
    thread.daemon = True
    thread.start()
