import re
import requests
from pyrogram import Client, filters
from globals import task_list, patterns

def is_valid_bunkr_url(url):
    return bool(re.match(r"https:\/\/bunkr+\.([\w.]+)\/a\/[\w\d]+", url))

def iis_valid_bunkr_url(url):
    return bool(re.match(r"https:\/\/bunkr{1,2}\.[\w.]+\/a\/[\w\d]+", url))

# Extract video URLs from a Bunkrr page
def extract_video_urls(page_url):
    #video_url_pattern = r"https?:\/\/.*?\/v\/[\w\d]+"
    #video_url_pattern = r"https?:\/\/.*?\/v\/[\w\d\-]+"
    #video_url_pattern = r"https?:\/\/.*?\/v\/[^\"]+"
    video_url_pattern = patterns["bunkr_video"]
    try:
        response = requests.get(page_url)
        response.raise_for_status()
        html_content = response.text
        video_urls = list(set(re.findall(video_url_pattern, html_content)))  # Remove duplicates
        return video_urls
    except requests.RequestException as e:
        return None  # Return None in case of error

# Format video URLs into payloads
def format_payload(video_urls, chat_id):
    return [{"url": url, "chat_id": chat_id, "type": "bunkr_page"} for url in video_urls]

# The command handler for /bunkrBulk <chat_id> <main_url>
@Client.on_message(filters.command("bunkrBulk"))
async def bunkr_bulk(client, message):
    global task_list
    try:
        # Get chat_id and URL from message
        args = message.text.split()
        if len(args) != 3:
            await message.reply("Usage: /bunkrBulk `chat_id` `main_url`")
            return
        
        chat_id, page_url = args[1], args[2]
        
        # Validate the Bunkrr URL
        if not is_valid_bunkr_url(page_url):
            await message.reply(f"Invalid Bunkrr URL: {page_url}. Please provide a valid URL with /a/ path.")
            return
        
        # Step 1: Extract video URLs
        video_urls = extract_video_urls(page_url)
        
        if video_urls is None:
            await message.reply("Error extracting URLs. Please check the provided URL.")
            return
        
        if not video_urls:
            await message.reply("No video URLs found.")
            return
        
        # Step 2: Format the URLs into JSON payload
        payload_array = format_payload(video_urls, chat_id)
        
        # Step 3: Add to global task list
        task_list.extend(payload_array)
        
        # Show the updated task list
        await message.reply(f"**Task list updated!\n\nAdd: {len(payload_array)} videos.\n\nChat ID: {chat_id}\n\nTask List:\n{len(task_list)} videos**")
        
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

