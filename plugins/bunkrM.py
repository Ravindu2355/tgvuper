import re
import requests
from pyrogram import Client, filters
from globals import task_list, patterns
from urllib.parse import urlparse

def transform_links(matches, base_url):
    transformed_links = []
    for url in matches:
        if url.startswith("/"):  # Check if it's a relative URL
            transformed_links.append(f"{base_url}{url}")  # Prepend base URL
        else:
            transformed_links.append(url)  # Leave absolute URLs unchanged
    return transformed_links

def get_base_url(url):
    parsed_url = urlparse(url)
    # Combine the scheme (http/https) and netloc (domain)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


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
        baseu = get_base_url(page_url)
        response = requests.get(page_url)
        response.raise_for_status()
        html_content = response.text
        #mts = list(set(re.findall(video_url_pattern, html_content)))  # Remove duplicates
        #mts = list(set(match[0] for match in re.findall(video_url_pattern, html_content)))  # Extract only full matches
        matches = re.findall(video_url_pattern, html_content)
        mts=[match[0] + match[2] for match in matches if match[2]]
        print(mts)
        video_urls = transform_links(mts, baseu)
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
        baseu = get_base_url(page_url)
        
        if video_urls is None:
            await message.reply(f"Error extracting URLs. Please check the provided URL.\nbase URL :{baseu}")
            return
        
        if not video_urls:
            await message.reply("No video URLs found.")
            return
        
        # Step 2: Format the URLs into JSON payload
        payload_array = format_payload(video_urls, chat_id)
        
        # Step 3: Add to global task list
        task_list.extend(payload_array)
        
        # Show the updated task list
        await message.reply(f"**Task list updated!\n\nAdd: {len(payload_array)} videos.\n\nChat ID: {chat_id}\n\nTask List:\n{len(task_list)} videos**\nbase URL :{baseu}\n 1st:{video_urls[0]}")
        
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

