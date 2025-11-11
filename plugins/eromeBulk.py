import re
import requests
from pyrogram import Client, filters
from globals import task_list

# ----------------------------
# Helper Functions
# ----------------------------

def get_base_url(url):
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def transform_links(matches, base_url):
    transformed_links = []
    for url in matches:
        if url.startswith("/"):
            transformed_links.append(f"{base_url}{url}")
        else:
            transformed_links.append(url)
    return transformed_links

def is_valid_erome_url(url):
    """
    Check if URL is a valid Erome album
    Example: https://erome.com/album_id
    """
    return bool(re.match(r"https:\/\/(?:www\.)?erome\.com\/[\w\d]+", url))

# ----------------------------
# Extractor Function
# ----------------------------

def extract_erome_urls(page_url):
    """
    Extract all image/video URLs from an Erome album page
    """
    try:
        base_url = get_base_url(page_url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/117.0.0.0 Safari/537.36",
            "Referer": page_url
        }
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()
        html_content = response.text

        # Match image/video URLs inside <img src="..."> or <video src="..."> / <source src="...">
        url_pattern = r'<(?:img|video|source)[^>]+src=["\'](https?://[^"\']+)["\']'
        matches = re.findall(url_pattern, html_content)
        urls = transform_links(matches, base_url)

        # Remove duplicates
        urls = list(set(urls))
        return urls

    except requests.RequestException as e:
        print(f"Error fetching Erome page: {e}")
        return None

# ----------------------------
# Format Payload
# ----------------------------

def format_payload(video_urls, chat_id):
    return [{"url": url, "chat_id": chat_id, "type": "erome_album"} for url in video_urls]

# ----------------------------
# Pyrogram Command Handler
# ----------------------------

@Client.on_message(filters.command("eromeBulk"))
async def erome_bulk(client, message):
    global task_list
    try:
        args = message.text.split()
        if len(args) != 3:
            await message.reply("Usage: /eromeBulk `chat_id` `album_url`")
            return

        chat_id, page_url = args[1], args[2]

        if not is_valid_erome_url(page_url):
            await message.reply(f"Invalid Erome URL: {page_url}. Please provide a valid album URL.")
            return

        # Extract URLs
        media_urls = extract_erome_urls(page_url)
        if media_urls is None:
            await message.reply("Error extracting URLs. Please check the provided URL.")
            return
        if not media_urls:
            await message.reply("No media URLs found in this album.")
            return

        # Format payload and add to task list
        payload_array = format_payload(media_urls, chat_id)
        task_list.extend(payload_array)

        await message.reply(
            f"**Task list updated!\n\nAdd: {len(payload_array)} media.\n\nChat ID: {chat_id}\n\nTask List:\n{len(task_list)} media**\nFirst URL: {media_urls[0]}"
        )

    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
