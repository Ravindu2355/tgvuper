import os, time
import requests
from mimetypes import guess_type
from moviepy.editor import VideoFileClip
from Func.up_progress import progress_for_pyrogram, humanbytes
from res.header import get_h
from res.cookie import r_cookies
from PIL import Image
from config import TgSizeLimit
from Func.tomp4 import convert_video_to_mp4

def is_file_within_size_limit_from_url(url, size_limit=2 * 1024 * 1024 * 1024):  # 2GB in bytes
    try:
        # Send a HEAD request to fetch headers only
        response = requests.head(url, allow_redirects=True)

        if response.status_code != 200:
            print(f"Error: Unable to access the URL. Status code: {response.status_code}")
            return f"Error: Unable to access the URL. Status code: {response.status_code}"

        # Get the 'Content-Length' header, which gives the file size in bytes
        content_length = response.headers.get('Content-Length')
        if content_length is None:
            print("Error: 'Content-Length' header is missing. Cannot determine file size.")
            return "Error: 'Content-Length' header is missing. Cannot determine file size."

        file_size = int(content_length)
        if file_size <= size_limit:
            print(f"The file at '{url}' is within the size limit ({file_size} bytes).")
            return True
        else:
            print(f"The file at '{url}' exceeds the size limit ({file_size} bytes).")
            return f"Error: The file at '{url}' exceeds the size limit ({file_size} bytes)."

    except requests.RequestException as e:
        print(f"Error: Failed to check file size from URL. Exception: {e}")
        return f"Error: Failed to check file size from URL. Exception: {e}"


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
    content_disposition = response.headers.get('Content-Disposition')
    if content_disposition:
        try:
            filename_part = content_disposition.split('filename=')[-1]
            filename = filename_part.strip(' "')
            if filename:
                return filename
        except Exception as e:
            print(f"Error extracting filename from Content-Disposition: {e}")
    
    url_path = response.url.split("/")[-1]
    if url_path:
        if '?' in url_path:
            url_path = url_path.split("?")[0]
        return url_path
    
    return f"video_{str(int(time.time()))}.mp4"


# Function to download file from the URL with progress
async def download_file(client, msg, url, download_path, chat_id):
    try:
        headers = get_h(url)
        cookies = r_cookies()
        response = requests.get(url, headers=headers, cookies=cookies, stream=True)
        
        if response.status_code != 200:
            await client.send_message(chat_id, f"Failed to fetch URL: {url}\nStatus code: {response.status_code}")
            return None

        ndl = get_file_name_from_response(response)
        if not ndl:
            ndl = f"video_{str(int(time.time()))}.mp4"
        download_path = ndl

        total_size = int(response.headers.get('content-length', 0))
        if total_size == 0:
            await client.send_message(chat_id, "Failed to detect size it detected as 0-bytes.\n\n**But trying to download...**")
        if total_size >= TgSizeLimit:
            await client.send_message(chat_id, f"**Sorry...**\n\nI can not upload Files larger than {humanbytes(TgSizeLimit)}")
            return None
        downloaded = 0
        start_t = time.time()
        old_pm = ""

        await msg.edit_text(f"Starting download\nSize: {humanbytes(total_size)}\nName: {download_path}")
        
        # Only show progress if file is >50MB (50 * 1024 * 1024 bytes)
        with open(download_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 50 * 1024 * 1024:
                        progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                        progress_message = f"Downloading... {progress:.2f}%"
                        now = time.time()
                        diff = now - start_t
                        pm = progress_message
                        # Update progress only every 10 seconds
                        if round(diff % 10.00) == 0 or downloaded == total_size:
                            if old_pm != pm:
                                old_pm = pm
                                await msg.edit_text(pm)

        if download_path.endswith(".mp4"):
            return download_path
        else:
            await msg.edit_text(f"😰Not a mp4.trying to convert!")
            newdl_path = await convert_video_to_mp4(msg,download_path)
            return newdl_path
    except Exception as e:
        await client.send_message(chat_id, f"Error on URL: {url}\nDownload error: {e}")
        return None

# Function to upload file to Telegram (with optional thumbnail) with progress
async def upload_file_to_telegram(client, msg, task, file_path, cap=""):
    chat_id = task['chat_id']
    try:
        sz = get_file_size(file_path)
        await msg.edit_text(f"Upload Starting!... {sz}")
        if file_path:
            file_type = guess_type(file_path)[0]
            thumbnail_path = f"file_{int(time.time())}_thumb.jpg"
            duration = 0

            # Generate a thumbnail if no thumbnail URL is provided and the file is a video
            if not task.get('thumbnail_url'):
                if not thumbnail_path:
                    thumbnail_path = f"{time.time()}_thumb.jpg"
                try:
                    with VideoFileClip(file_path) as video:
                        duration = int(video.duration)
                        frame = video.get_frame(3.0)  # Get a frame at 3 seconds
                        img = Image.fromarray(frame)
                        img.save(thumbnail_path, "JPEG")
                except Exception as e:
                    thumbnail_path=""
                    await msg.reply(f"Error generating thumbnail: {e}")
                    pass
            start_time = time.time()
            total_size = os.path.getsize(file_path)
            uploaded = 0
            old_pm = ""

            # Default caption to task's URL if not provided
            if not cap:
                cap = task['url']

            # Progress callback function
            async def progress_callback(current, total, message):
                nonlocal old_pm
                progress = (current / total) * 100
                progress_message = f"Uploading... {progress:.2f}%"
                now = time.time()
                diff = now - start_time
                # Update progress only every 10 seconds
                if round(diff % 10.00) == 0 or current == total:
                    if old_pm != progress_message:
                        old_pm = progress_message
                        await message.edit_text(progress_message)

            # Check if the file is a video or document
            if file_type and "video" in file_type:
                # Only show progress if file is >50MB
                if total_size > 50 * 1024 * 1024:
                    await client.send_video(
                        chat_id=chat_id,
                        video=file_path,
                        duration=duration,
                        caption=f"Video: {cap}",
                        thumb=thumbnail_path if not task.get('thumbnail_url') else task['thumbnail_url'],
                        supports_streaming=True,
                        progress=progress_callback,
                        progress_args=(msg,)
                    )
                else:
                    await client.send_video(
                        chat_id=chat_id,
                        video=file_path,
                        duration=duration,
                        caption=f"Video: {cap}",
                        thumb= thumbnail_path if not task.get('thumbnail_url') else task['thumbnail_url'],
                    )
            else:
                # Upload file as a document
                if total_size > 50 * 1024 * 1024:
                    await client.send_document(
                       chat_id=chat_id,
                       document=file_path,
                       caption=f"File: {cap}",
                       thumb= thumbnail_path if not task.get('thumbnail_url') else task['thumbnail_url'],
                       progress=progress_callback,
                       progress_args=(msg,)
                    )
                else:
                    await client.send_document(
                       chat_id=chat_id,
                       document=file_path,
                       caption=f"File: {cap}",
                       thumb= thumbnail_path if not task.get('thumbnail_url') else task['thumbnail_url'],
                    )

            # Clean up the thumbnail file
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)

    except Exception as e:
        await client.send_message(chat_id, f"Error on upload: {e}")
