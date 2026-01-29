import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import json
import globals


def get_base_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name).strip()


# --------------------------------------------------
# THUMBNAIL EXTRACTION
# --------------------------------------------------
def extract_thumbnail(html, soup):
    preload_img = re.search(
        r'<link[^>]+rel="preload"[^>]+as="image"[^>]+href="([^"]+)"',
        html, re.I
    )
    if preload_img:
        return preload_img.group(1)

    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        return og_image["content"]

    img_tag = soup.find("img")
    if img_tag and img_tag.get("src"):
        return img_tag["src"]

    return None


# --------------------------------------------------
# INLINE _TPL_ HLS
# --------------------------------------------------
def extract_inline_tpl(html):
    match = re.search(
        r'href="(https://video-[^"]+_TPL_[^"]+\.m3u8)"',
        html, re.I
    )
    if not match:
        return None

    tpl_url = match.group(1)
    multi_match = re.search(r'multi=([^/]+):/_TPL_', tpl_url)
    if not multi_match:
        return None

    qualities = re.findall(r'(\d+p):', multi_match.group(1))
    streams = []

    for q in qualities:
        streams.append({
            "quality": q.replace("p", ""),
            "url": tpl_url.replace("_TPL_", q),
            "type": "hls"
        })

    return streams


# --------------------------------------------------
# PRELOAD M3U8
# --------------------------------------------------
def extract_preload_m3u8(soup, headers):
    preload_tag = soup.find(
        'link', rel='preload', href=re.compile(r'\.m3u8')
    )
    if not preload_tag:
        return None

    preload_url = preload_tag['href']
    if '_TPL_' not in preload_url:
        return None

    try:
        m3u8 = requests.get(preload_url, headers=headers, timeout=10).text
    except Exception:
        return None

    base_url = get_base_url(preload_url)
    lines = m3u8.splitlines()
    streams = []

    for i in range(len(lines)):
        if lines[i].startswith('#EXT-X-STREAM-INF'):
            res = re.search(r'RESOLUTION=\d+x(\d+)', lines[i])
            quality = res.group(1) if res else "unknown"

            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if next_line.startswith("//"):
                url = "https:" + next_line
            elif next_line.startswith("http"):
                url = next_line
            else:
                url = preload_url.replace("_TPL_", quality + "p")

            streams.append({
                "quality": quality,
                "url": url,
                "type": "hls"
            })

    return streams


# --------------------------------------------------
# MP4 EXTRACTION (og:video + JSON-LD)
# --------------------------------------------------
def extract_content_urls(html):
    streams = []

    og_videos = re.findall(
        r'<meta[^>]+property="og:video(?::secure_url)?"[^>]+content="([^"]+\.mp4[^"]*)"',
        html, re.I
    )

    for url in og_videos:
        q = re.search(r'(\d{3,4})p', url, re.I)
        streams.append({
            "quality": q.group(1) if q else "unknown",
            "url": url,
            "type": "mp4"
        })

    json_ld = re.search(
        r'"contentUrl"\s*:\s*"([^"]+\.mp4[^"]*)"',
        html, re.I
    )
    if json_ld:
        url = json_ld.group(1)
        q = re.search(r'(\d{3,4})p', url, re.I)
        streams.append({
            "quality": q.group(1) if q else "unknown",
            "url": url,
            "type": "mp4"
        })

    return streams or None


# --------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------
def get_video_stream_qualities(page_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/124.0.0.0 Mobile Safari/537.36',
        'Origin': 'https://xhamster2.com',
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

    title_tag = soup.find('title')
    title = clean_filename(title_tag.text if title_tag else "video")
    thumbnail = extract_thumbnail(html, soup)

    streams = []

    tpl = extract_inline_tpl(html)
    if tpl:
        streams.extend(tpl)

    preload = extract_preload_m3u8(soup, headers)
    if preload:
        streams.extend(preload)

    mp4s = extract_content_urls(html)
    if mp4s:
        streams.extend(mp4s)

    if not streams:
        return {"error": "No valid video structure found on page."}

    # Deduplicate
    seen = set()
    streams = [
        s for s in streams
        if not (s["url"] in seen or seen.add(s["url"]))
    ]

    return {
        "type": "shorties",
        "videos": [{
            "title": title,
            "thumbnail": thumbnail,
            "streams": streams
        }]
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------
#if __name__ == "__main__":
#    url = input("Enter xHamster video URL: ").strip()
#    data = get_video_stream_qualities(url)
#    print(json.dumps(data, indent=2))
