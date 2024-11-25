from flask import Flask, request, jsonify
import threading
import requests
from pyrogram import Client
import time
import os
from mimetypes import guess_type
from moviepy.editor import VideoFileClip

# Initialize the Flask application
app = Flask(__name__)

# Define your Telegram bot credentials (API ID, API Hash, and Bot Token)
API_ID = 'YOUR_API_ID'  # Get from https://my.telegram.org/auth
API_HASH = 'YOUR_API_HASH'  # Get from https://my.telegram.org/auth
BOT_TOKEN = 'YOUR_BOT_TOKEN'  # Get from @BotFather

# Create the Pyrogram Client
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

# Function to generate a thumbnail from the video if no thumbnail is provided
def generate_thumbnail(video_path, thumbnail_path="thumbnail.jpg"):
    try:
        clip = VideoFileClip(video_path)
        frame = clip.get_frame(1)  # Gets the frame at 1 second
        frame.save_frame(thumbnail_path)  # Save the frame as an image
        clip.close()
        print(f"Thumbnail saved to {thumbnail_path}")
        return thumbnail_path
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None

# Function to download file from the URL with progress
def download_file(url, download_path, chat_id):
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(download_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                    progress_message = f"Downloading... {progress:.2f}%"
                    bot_app.send_message(chat_id, progress_message)  # Send progress message to user
                    print(f"Download progress: {progress:.2f}%")
        print(f"File downloaded to {download_path}")
        return download_path
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

# Function to upload file to Telegram (with optional thumbnail) with progress
def upload_file_to_telegram(task, file_path):
    def progress_callback(current, total):
        progress = (current / total) * 100
        progress_message = f"Uploading... {progress:.2f}%"
        bot_app.send_message(task['chat_id'], progress_message)  # Send progress message to user
        print(f"Upload progress: {progress:.2f}%")

    try:
        if file_path:
            file_type = guess_type(file_path)[0]  # Get MIME type (e.g., video/mp4, image/jpg)
            thumbnail_path = None
            if not task['thumbnail_url']:  # If no thumbnail is provided, generate one
                if "video" in file_type:
                    thumbnail_path = generate_thumbnail(file_path)  # Generate thumbnail from video
            
            if file_type and "video" in file_type:  # Check if it's a video file
                bot_app.send_video(
                    chat_id=task['chat_id'],
                    video=file_path,
                    caption=f"Video: {task['url']}",
                    thumb=thumbnail_path if thumbnail_path else task['thumbnail_url'],
                    progress=progress_callback
                )
                print(f"Video uploaded to {task['chat_id']}: {file_path}")
            else:  # For other file types
                bot_app.send_document(
                    chat_id=task['chat_id'],
                    document=file_path,
                    caption=f"File: {task['url']}",
                    thumb=thumbnail_path if thumbnail_path else task['thumbnail_url'],
                    progress=progress_callback
                )
                print(f"File uploaded to {task['chat_id']}: {file_path}")
        else:
            print("No file to upload.")
    except Exception as e:
        print(f"Error uploading file to Telegram: {e}")

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

# Background thread to process tasks
thread = threading.Thread(target=process_tasks)
thread.daemon = True
thread.start()

# Flask route to handle adding tasks via POST request
@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    url = data.get('url')
    chat_id = data.get('chat_id')
    thumbnail_url = data.get('thumbnail_url', None)
    
    if url and chat_id:
        # Add the task to the bot's task list
        add_task_to_list(url, chat_id, thumbnail_url)
        return jsonify({"status": "success", "message": f"Task added for URL: {url}"}), 200
    else:
        return jsonify({"status": "error", "message": "Missing url or chat_id"}), 400

# Run the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
