import os, time
import requests
from mimetypes import guess_type
from moviepy.editor import VideoFileClip
from Func.up_progress import progress_for_pyrogram, humanbytes
from res.header import get_h
from res.cookie import r_cookies
from PIL import Image

def get_file_size(file_path):
    try:
        size_bytes = os.path.getsize(file_path)
        for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
    except FileNotFoundError:
        return "Error: File not found"



def get_file_name_from_response(response):
    # Check if Content-Disposition header is present
    content_disposition = response.headers.get('Content-Disposition')
    if content_disposition:
        # Extract the filename from the Content-Disposition header
        filename_part = content_disposition.split('filename=')[-1]
        filename = filename_part.strip(' "')
        return filename
    
    # Fallback to extracting the file name from the URL
    return f"video_{str(time.time())}.mp4"
    
# Function to generate a thumbnail from the video if no thumbnail is provided

# Function to download file from the URL with progress
async def download_file(client, msg, url, download_path, chat_id):
    try:
        #msg = await client.send_message(chat_id,"starting download...")
        headers=get_h(url)
        cookies=r_cookies()
        response = requests.get(url, headers=headers, cookies=cookies, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        ndl=get_file_name_from_response(response)
        download_path= ndl
        downloaded = 0
        start_t=time.time()
        old_pm=""
        await msg.edit_text(f"starting download \nsize: {humanbytes(total_size)}\nname: {download_path}")
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
                    if round(diff % 10.00) == 0 or downloaded == total_size:
                       if old_pm != pm:
                           old_pm = pm
                           #await msg.edit_text(pm)  # Send progress message to user
        #await msg.edit_text("downloaded!...")
        return download_path
    except Exception as e:
        await client.send_message(chat_id,f"Err on url:{url}\ndl Err: {e}")
        return None

# Function to upload file to Telegram (with optional thumbnail) with progress
async def upload_file_to_telegram(client, msg, task, file_path, cap=""):
    chat_id=task['chat_id']
    try:
        sz = get_file_size(file_path)
        await msg.edit_text(f"Upload Starting!...{sz}")
        if file_path:
            file_type = guess_type(file_path)[0]
            thumbnail_path = None
            duration= 0
            if not task['thumbnail_url']:
                if "video" in file_type:
                    thumbnail_path = f'{time.time()}_thumb.jpg'
                    with VideoFileClip(file_path) as video:
                        duration = int(video.duration)
                        frame = video.get_frame(3.0)
                        img = Image.fromarray(frame)
                        img.save(thumbnail_path, "JPEG")         
            start_time=time.time()
            if cap == "":
                cap == task['url']
            if file_type and "video" in file_type:
                await client.send_video(
                    chat_id=task['chat_id'],
                    video=file_path,
                    duration=duration,
                    caption=f"Video: {cap}",
                    thumb=thumbnail_path if thumbnail_path else task['thumbnail_url'],
                    supports_streaming=True,  # Ensure the video is streamable
                    #progress=progress_for_pyrogram,
                    #progress_args=("🔰**Uploading!...**🔰\n\n",msg,start_time)
                )
            else:
                await client.send_document(
                    chat_id=task['chat_id'],
                    document=file_path,
                    caption=f"File: {cap}",
                    thumb=thumbnail_path if thumbnail_path else task['thumbnail_url'],
                    supports_streaming=True,  # Ensure the video is streamable
                    #progress=progress_for_pyrogram,
                    #progress_args=("🔰**Uploading!...**🔰\n\n",msg,start_time)
                
                )
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
    except Exception as e:
        await client.send_message(chat_id,f"Err on upload : {e}")
        pass
