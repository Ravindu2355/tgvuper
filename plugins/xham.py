import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import json

def get_base_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name).strip()

def extract_thumbnail(html, soup):
    """Finds thumbnail from preload, og:image, or first <img>."""
    # Try preload <link> tag first
    preload_img = re.search(r'<link[^>]+rel="preload"[^>]+as="image"[^>]+href="([^"]+)"', html)
    if preload_img:
        return preload_img.group(1)

    # Try Open Graph meta tag
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        return og_image["content"]

    # Try <img> fallback
    img_tag = soup.find("img")
    if img_tag and img_tag.get("src"):
        return img_tag["src"]

    return None

def extract_inline_tpl(html):
    """Extracts qualities from inline structural _TPL_ URLs (contains 'multi=' section)."""
    match = re.search(r'href="(https://video-[^"]+_TPL_[^"]+\.m3u8)"', html)
    if not match:
        return None

    tpl_url = match.group(1)
    multi_match = re.search(r'multi=([^/]+):/_TPL_', tpl_url)
    if not multi_match:
        return None

    qualities_part = multi_match.group(1)
    # Example: 256x144:144p:,426x240:240p:,854x480:480p:
    qualities = re.findall(r'(\d+p):', qualities_part)

    streams = []
    for q in qualities:
        streams.append({
            "quality": q.replace('p', ''),
            "url": tpl_url.replace("_TPL_", q)
        })

    return streams

def extract_preload_m3u8(soup, headers):
    """Extracts qualities from preload .m3u8 link structure."""
    preload_tag = soup.find('link', rel='preload', href=re.compile(r'\.m3u8'))
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
    lines = m3u8.strip().splitlines()
    streams = []

    for i in range(len(lines)):
        if lines[i].startswith('#EXT-X-STREAM-INF'):
            match = re.search(r'RESOLUTION=\d+x(\d+)', lines[i])
            quality = match.group(1) + 'p' if match else 'unknown'
            if "/key" in lines[i + 1]:
                actual_url = "https:" + lines[i + 1] if lines[i + 1].startswith("//") else base_url + lines[i + 1]
            else:
                actual_url = preload_url.replace("_TPL_", quality)
            streams.append({
                "quality": quality.replace('p', ''),
                "url": actual_url
            })

    return streams

def get_video_stream_qualities(page_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'Referer': page_url,
        'Origin': 'https://xhamster2.com',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        html = requests.get(page_url, headers=headers, timeout=10).text
    except Exception as e:
        return {'error': f'Failed to load page: {e}'}

    soup = BeautifulSoup(html, 'html.parser')
    thumbnail = extract_thumbnail(html, soup)
    title_tag = soup.find('title')
    title = clean_filename(title_tag.text if title_tag else 'video')

    # Try inline structural _TPL_ first
    streams = extract_inline_tpl(html)
    if not streams:
        streams = extract_preload_m3u8(soup, headers)

    if not streams:
        return {'error': 'No valid video structure found on page.'}

    # ✅ Final structured result
    return {
        "type": "shorties",
        "videos": [
            {
                "title": title,
                "thumbnail": thumbnail,
                "streams": streams
            }
        ]
    }
