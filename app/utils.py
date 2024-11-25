import os
import requests
from mimetypes import guess_type
from moviepy.editor import VideoFileClip

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
            else:  # For other file types
                bot_app.send_document(
                    chat_id=task['chat_id'],
                    document=file_path,
                    caption=f"File: {task['url']}",
                    thumb=thumbnail_path if thumbnail_path else task['thumbnail_url'],
                    progress=progress_callback
                )
    except Exception as e:
        print(f"Error uploading file to Telegram: {e}")
