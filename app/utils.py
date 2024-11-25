import os, time
import requests
from mimetypes import guess_type
from moviepy.editor import VideoFileClip
from up_progress import progress_for_pyrogram

# Function to generate a thumbnail from the video if no thumbnail is provided
def generate_thumbnail(video_path, thumbnail_path="thumbnail.jpg"):
    try:
        clip = VideoFileClip(video_path)
        frame = clip.get_frame(1)  # Gets the frame at 1 second
        frame.save_frame(thumbnail_path)  # Save the frame as an image
        clip.close()
        return thumbnail_path
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None

# Function to download file from the URL with progress
async def download_file(url, download_path, chat_id):
    try:
        msg = await client.send_message(chat_id,"starting download...")
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        start_t=time.time()
        old_pm=""
        with open(download_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                    progress_message = f"Downloading... {progress:.2f}%"
                    now=time.time()
                    diff = now - start_t
                    pm=progress_message
                    if round(diffr % 10.00) == 0 or downloaded_size == total_size:
                       if old_pm != pm:
                           await msg.edit_text(pm)  # Send progress message to user
        return download_path
        await msg.delete()
    except Exception as e:
        await client.send_message(chat_id,f"Err on url:{url}\ndl Err: {e}")
        return None

# Function to upload file to Telegram (with optional thumbnail) with progress
def upload_file_to_telegram(task, file_path):
    def progress_callback(current, total):
        progress = (current / total) * 100
        progress_message = f"Uploading... {progress:.2f}%"
        client.send_message(task['chat_id'], progress_message)  # Send progress message to user

    try:
        msg = await client.send_message(chat_id,"Starting Upload...")
        if file_path:
            file_type = guess_type(file_path)[0]
            thumbnail_path = None
            if not task['thumbnail_url']:
                if "video" in file_type:
                    thumbnail_path = generate_thumbnail(file_path)
            
            if file_type and "video" in file_type:
                client.send_video(
                    chat_id=task['chat_id'],
                    video=file_path,
                    caption=f"Video: {task['url']}",
                    thumb=thumbnail_path if thumbnail_path else task['thumbnail_url'],
                    progress=progress_callback
                )
            else:
                client.send_document(
                    chat_id=task['chat_id'],
                    document=file_path,
                    caption=f"File: {task['url']}",
                    thumb=thumbnail_path if thumbnail_path else task['thumbnail_url'],
                    progress=progress_callback
                )
    except Exception as e:
        pass
