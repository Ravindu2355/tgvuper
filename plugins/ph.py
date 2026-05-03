import re
import json
import requests
from bs4 import BeautifulSoup
import globals
from urllib.parse import urlparse

# --------------------------------------------------
# Extract flashvars streams
# --------------------------------------------------
def extract_flashvars(html):

    streams = []

    match = re.search(
        r'var\s+flashvars_\d+\s*=\s*(\{.*?\});',
        html, re.DOTALL
    )

    if not match:
        return []

    try:
        data = json.loads(match.group(1))
        media = data.get("mediaDefinitions", [])

        for m in media:
            if m.get("format") == "hls" and m.get("videoUrl"):
                streams.append({
                    "quality": m.get("quality", "unknown"),
                    "url": m.get("videoUrl"),
                    "type": "m3u8"
                })

            if m.get("format") == "mp4" and m.get("videoUrl"):
                streams.append({
                    "quality": m.get("quality", "unknown"),
                    "url": m.get("videoUrl"),
                    "type": "mp4"
                })

    except:
        pass

    return streams


# --------------------------------------------------
# Extract JSON_SHORTIES
# --------------------------------------------------
def extract_shorties(html):
    streams = []
    parts = html.split("JSON_SHORTIES")
    if len(parts) < 2:
        return []
    section = parts[-1]
    match = re.search(r'\[\s*{.*?}\s*\]', section, re.DOTALL)
    if not match:
        return []
    try:
        data = json.loads(match.group(0))
        for item in data:
            media = item.get("mediaDefinitions", [])
            for m in media:
                if m.get("format") == "hls" and m.get("videoUrl"):
                    streams.append({
                        "quality": m.get("quality", "unknown"),
                        "url": m.get("videoUrl"),
                        "type": "m3u8"
                    })

                if m.get("format") == "mp4" and m.get("videoUrl"):
                    streams.append({
                        "quality": m.get("quality", "unknown"),
                        "url": m.get("videoUrl"),
                        "type": "mp4"
                    })
    except:
        pass
    return streams


# --------------------------------------------------
# Extract og:video mp4
# --------------------------------------------------
def extract_og_mp4(html):

    streams = []

    og_videos = re.findall(
        r'<meta[^>]+property="og:video(?::secure_url)?"[^>]+content="([^"]+\.mp4[^"]*)"',
        html, re.I
    )

    for url in og_videos:
        q = re.search(r'(\d{3,4})P', url, re.I)

        streams.append({
            "quality": q.group(1) if q else "unknown",
            "url": url,
            "type": "mp4"
        })

    return streams


# --------------------------------------------------
# Extract JSON-LD mp4
# --------------------------------------------------
def extract_json_ld(html):

    streams = []

    match = re.search(
        r'"contentUrl"\s*:\s*"([^"]+\.mp4[^"]*)"',
        html, re.I
    )

    if match:

        url = match.group(1)
        q = re.search(r'(\d{3,4})P', url, re.I)

        streams.append({
            "quality": q.group(1) if q else "unknown",
            "url": url,
            "type": "mp4"
        })

    return streams


# --------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------
def get_pornhub_streams(page_url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/124.0.0.0 Mobile Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:

        proxy_url = globals.proxy.get("url")

        if proxy_url and proxy_url != "off":

            payload = {
                "url": page_url,
                "headers": {
                    "User-Agent": headers["User-Agent"]
                }
            }

            html = requests.post(proxy_url, json=payload, timeout=10).text

        else:

            html = requests.get(page_url, headers=headers, timeout=10).text

    except Exception as e:
        return {"error": f"Failed to load page: {e}"}


    soup = BeautifulSoup(html, 'html.parser')


    # --------------------------------------------------
    # Title
    # --------------------------------------------------

    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else "video"


    # --------------------------------------------------
    # Thumbnail
    # --------------------------------------------------

    thumbnail = None

    og_img = soup.find("meta", property="og:image")
    if og_img:
        thumbnail = og_img.get("content")


    # --------------------------------------------------
    # Streams
    # --------------------------------------------------

    streams = []

    streams.extend(extract_flashvars(html))
    streams.extend(extract_shorties(html))
    streams.extend(extract_og_mp4(html))
    streams.extend(extract_json_ld(html))


    if not streams:
        return {"error": "No valid video structure found on page."}


    # --------------------------------------------------
    # Deduplicate
    # --------------------------------------------------

    seen = set()

    streams = [
        s for s in streams
        if not (s["url"] in seen or seen.add(s["url"]))
    ]


    return {
        "type": "video",
        "videos": [{
            "title": title,
            "thumbnail": thumbnail,
            "streams": streams
        }]
    }
