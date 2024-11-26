from threading import Thread
import os, asyncio
import time
import requests
from Func.utils import generate_thumbnail, download_file, upload_file_to_telegram
from Func.expg import ex_page
from flask import Flask, request, jsonify
from flask_cors import CORS
# Initialize the Flask application
app = Flask(__name__)
CORS(app)


@app.route('/')
def f_home():
    return 'hellow RVX task dl bot',200


# Task list to hold URL tasks
task_list = []
running=0
s=0

def get_task_list():
    global task_list
    return task_list

# Function to add a task to the task list
def add_task_to_list(url, chat_id, thumbnail_url=None, type=None):
    global task_list
    task = {
        'url': url,
        'chat_id': chat_id,
        'thumbnail_url': thumbnail_url,
        'type':type
    }
    task_list.append(task)
    print("task add")
    return task_list

# Function to process tasks from the task list
async def process_tasks(client):
    global s, running, task_list
    while True:
        s+=1
        if task_list and running == 0:
            running=1
            task = task_list.pop(0)  # Get the first task in the list
            url = task['url']
            chat_id = task['chat_id']
            thumbnail_url = task['thumbnail_url']
            if task['type']:
                if 'page' in task['type']:
                    msg= await client.send_message(chat_id,"Starting page Extract!")
                    exd = ex_page(task)
                    await msg.edit_text(f"Extracted: {len(exd)} sources from that page!...")
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
                    running=0
            else:
               msg= await client.send_message(chat_id,"Starting Task!")
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
                    running=0
        await asyncio.sleep(2)  # Wait 2 seconds before checking again

@app.route('/tasks')
def f_tasks():
    return f"Currently {len(get_task_list())} tasks running!..",200


@app.route('/add_task', methods=['POST'])
def add_task():
    global task_list
    data = request.json
    url = data.get('url')
    chat_id = data.get('chat_id')
    thumbnail_url = data.get('thumbnail_url', None)
    type = data.get('type',None)
    if url and chat_id:
        task = {'url': url, 'chat_id': chat_id, 'thumbnail_url': thumbnail_url, 'type': type}
        task_list.append(task)  # Adding task to the global task list
        return jsonify({"status": "success", "message": f"Task added for URL: {url}"}), 200
    else:
        return jsonify({"status": "error", "message": "Missing url or chat_id"}), 400


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
