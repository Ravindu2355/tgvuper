import requests, re
from bs4 import BeautifulSoup
from res.ex_help import site_data
from res.cookie import parse_cookie_str
from log import logger as lg
from urllib.parse import urlparse


s_h = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
s_c={}

def eproner_ex(page_url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(page_url, headers=s_h, timeout=20)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    download_div = soup.find("div", id="downloaddiv")
    if not download_div:
        return None

    # ✅ Auto-detect base URL
    parsed = urlparse(page_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    videos = []

    for a in download_div.find_all("a"):
        text = a.get_text(strip=True)
        href = a.get("href")

        # Match: (720p, h264, 1272.91 MB)
        match = re.search(r"\((\d+)p.*?h264.*?,\s*([\d.]+)\s*MB\)", text, re.I)
        if not match:
            continue

        quality = int(match.group(1))
        size_mb = float(match.group(2))

        full_url = href if href.startswith("http") else base_url.rstrip("/") + "/" + href.lstrip("/")

        videos.append({
            "quality": quality,
            "size": size_mb,
            "url": full_url
        })

    # ✅ Sort by HIGHEST quality first
    videos.sort(key=lambda x: x["quality"], reverse=True)

    # ✅ Pick best under 1.9GB (1900MB)
    for video in videos:
        if video["size"] <= 1900:
            return video["url"]

    return None

def exn_b(html):
    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')

    # Extract the og:image content, with error handling for missing tag
    og_image = soup.find('meta', property='og:image')
    if og_image:
        og_image = og_image.get('content', '')
    else:
        og_image = ''

    # Extract the og:title content
    og_title = soup.find('meta', property='og:title')
    if og_title:
        og_title = og_title.get('content', '')
    else:
        og_title = ''

    if og_image and og_title:
        # Extract the base URL of the image
        base_url = urlparse(og_image)._replace(path='').geturl()

        # Extract the file extension from og:title (e.g., mp4 from the filename)
        file_extension = re.search(r'\.([a-zA-Z0-9]+)$', og_title).group(1)

        # Output the results
        print("OG Image URL:", og_image)
        print("Base URL:", base_url)
        print("File Extension from OG Title:", file_extension)
        nurl = og_image.replace("i-", "").replace("thumbs/", "")
        nset = nurl.split(".")
        nset.pop()
        nset.append(file_extension)
        nuu = ".".join(nset)
        lg.info(nuu)
        return [nuu]
    else:
        lg.info("OG tags not found in the HTML")
        return []

def eexn_b(html):
        # Parse the HTML content
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract the og:image content
        og_image = soup.find('meta', property='og:image')['content']

        # Extract the base URL of the image
        base_url = urlparse(og_image)._replace(path='').geturl()

        # Extract the og:title content
        og_title = soup.find('meta', property='og:title')['content']

        # Extract the file extension from og:title (e.g., mp4 from the filename)
        file_extension = re.search(r'\.([a-zA-Z0-9]+)$', og_title).group(1)

        # Output the results
        print("OG Image URL:", og_image)
        print("Base URL:", base_url)
        print("File Extension from OG Title:", file_extension)
        nurl = og_image.replace("i-","").replace("thumbs/","")
        nset = nurl.split(".")
        nset.pop()
        nset.append(file_extension)
        nuu = ".".join(nset)
        lg.info(nuu)
        return [nuu]


def ex_vpgolff(url):
    try:
        # Send a GET request to the webpage
        response = requests.get(url,headers=s_h,cookies=s_c)
        response.raise_for_status()  # Raise an error if the request fails

        if "bunk" in url:
           nuv = exn_b(response.text)
           if nuv:
              return nuv
            
        # Parse the webpage content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all video elements
        video_tags = soup.find_all('video')
        # Use a set to store unique video sources
        video_sources = set()  # Set automatically handles duplicates
        
        for video in video_tags:
            # Get the src from the video tag or nested source tag
            if video.get('src'):
                video_sources.add(video['src'])
            else:
                # Check for <source> tags inside the <video>
                sources = video.find_all('source')
                for source in sources:
                    if source.get('src'):
                        video_sources.add(source['src'])

        return video_sources

    except requests.exceptions.RequestException as e:
        lg.info(f"Error fetching the webpage: {e}")
        return set()


def ex_vpg(url):
    def extract_sources(html):
        soup = BeautifulSoup(html, 'html.parser')
        video_tags = soup.find_all('video')
        video_sources = set()
        for video in video_tags:
            if video.get('src'):
                video_sources.add(video['src'])
            else:
                for source in video.find_all('source'):
                    if source.get('src'):
                        video_sources.add(source['src'])
        return video_sources

    def fetch_with_proxy(target_url):
        proxy_url = "https://script.google.com/macros/s/AKfycbz1gq2kaB3JydJICPrOai4Klx7qO-L91KSIrrT6GhPougbL48NRS96FT83K1_x2Ucm6lg/exec"
        try:
            r = requests.get(proxy_url, params={"url": target_url}, timeout=15)
            if r.status_code == 200:
                return r.text
        except Exception:
            return None
        return None

    try:
        r = requests.get(url, headers=s_h, cookies=s_c, timeout=15)
        if r.status_code == 200:
            if "bunk" in url:
                nuv = exn_b(r.text)
                if nuv:
                    return nuv
            sources = extract_sources(r.text)
            if sources:
                return sources
            # if 200 but no <video>, try proxy
            proxy_html = fetch_with_proxy(url)
            if proxy_html:
                sources = extract_sources(proxy_html)
                if sources:
                    return sources
        else:
            # try proxy if non-200
            proxy_html = fetch_with_proxy(url)
            if proxy_html:
                sources = extract_sources(proxy_html)
                if sources:
                    return sources
        # if all failed
        r.raise_for_status()
    except Exception as e:
        # last attempt with proxy if request itself failed
        proxy_html = fetch_with_proxy(url)
        if proxy_html:
            sources = extract_sources(proxy_html)
            if sources:
                return sources
        raise e

async def ex_page(task):
    global s_h, s_c
    if "eporn" in task['url']:
        vdx=eproner_ex(task['url'])
        if vdx:
            return [vdx]
        else:
            return []
    for ob in site_data:
        v=site_data[ob]
        if ob in task['type']:
           if 'cookie' in v:
              s_c=parse_cookie_str(v['cookie']) 
           if 'headers' in v:
              s_h=v['headers']
    video_srcs = ex_vpg(task['url'])
    if video_srcs:
       lg.info("Video sources found:")
       urls=[]
       for src in video_srcs:
          lg.info(src)
          urls.append(src)
       return urls
    else:
       lg.info("No video sources found.")
       return []
