from threading import Thread
import os, asyncio
import time
import requests
from config import sleep_time
from Func.utils import download_file, upload_file_to_telegram
from Func.expg import ex_page
import globals
# Initialize the Flask application


# Task list to hold URL tasks
#task_list = []
running=0
s=0

def get_task_list():
    #global task_list
    return globals.task_list

# Function to add a task to the task list
def add_task_to_list(url, chat_id, thumbnail_url=None, type=None):
    #global task_list
    task = {
        'url': url,
        'chat_id': chat_id,
        'thumbnail_url': thumbnail_url,
        'type':type
    }
    globals.task_list.append(task)
    print("task add")
    return globals.task_list

# Function to process tasks from the task list
async def process_tasks(client):
    global s, running  # Declare global variables
    while True:
        try:
            s += 1
            if globals.task_list and running == 0:
                running = 1
                task = globals.task_list.pop(0)  # Get the first task in the list
                url = task.get('url')
                chat_id = task.get('chat_id')
                thumbnail_url = task.get('thumbnail_url')
                
                if task.get('type') and 'page' in task['type']:
                    try:
                        msg = await client.send_message(chat_id, "Starting page extract!")
                        exd = await ex_page(task)  # Extract page sources
                        await asyncio.sleep(1)
                        await msg.edit_text(f"Extracted: {len(exd)} sources from that page!")
                        
                        for url in exd:
                            filename = url.split("/")[-1]  # Extract the filename from the URL
                            if '?' in filename:
                                filename = filename.split("?")[0]
                            if "." not in filename:
                                filename = f"{time.time()}.mp4"
                            
                            file_path = await download_file(client, msg, url, filename, chat_id)
                            if file_path:
                                await upload_file_to_telegram(client, msg, task, file_path)
                                if os.path.exists(file_path):
                                    os.remove(file_path)

                        if len(exd) > 0:
                            await msg.delete()
                        running = 0

                    except Exception as e:
                        print(f"Error during page extraction: {e}")
                        await client.send_message(chat_id, f"Error during page extraction: {e}")
                        running = 0  # Ensure the running flag is reset

                else:
                    try:
                        msg = await client.send_message(chat_id, "Starting task!")
                        filename = url.split("/")[-1]  # Extract the filename from the URL
                        if '?' in filename:
                            filename = filename.split("?")[0]
                        if "." not in filename:
                            filename = f"{time.time()}.mp4"
                        
                        file_path = await download_file(client, msg, url, filename, chat_id)
                        if file_path:
                            await upload_file_to_telegram(client, msg, task, file_path)
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            await msg.delete()
                        running = 0

                    except Exception as e:
                        print(f"Error during file download or upload: {e}")
                        await client.send_message(chat_id, f"Error during task: {e}")
                        running = 0  # Ensure the running flag is reset

        except Exception as e:
            print(f"Unexpected error in main loop: {e}")
            await asyncio.sleep(1)  # Briefly wait before retrying to avoid a tight error loop
            running = 0
            
        await asyncio.sleep(sleep_time)  # Wait 2 seconds before checking again



# Start the task processing in a background thread
def start_task_processing(client):
    global s
    s = 1
    def run_asyncio():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_tasks(client))

    thread = Thread(target=run_asyncio)
    thread.daemon = True  # Set the thread as a daemon thread
    thread.start()
