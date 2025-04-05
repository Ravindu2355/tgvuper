import requests
from bs4 import BeautifulSoup
from res.ex_help import site_data
from res.cookie import parse_cookie_str
import asyncio
from playwright.sync_api import sync_playwright


s_h = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
s_c={}


def ex_vpg(url):
    try:
        with sync_playwright() as p:
            # Launch the browser
            browser = p.chromium.launch(headless=True)  # headless=True runs it in the background
            page = browser.new_page()
            
            # Navigate to the URL
            page.goto(url)
            
            # Wait for the JavaScript to load (adjust the selector as needed)
            page.wait_for_selector("video", timeout=10000)  # Wait for the video tag to load
            
            # Get all video elements
            video_sources = set()  # To store unique video sources
            
            video_tags = page.query_selector_all("video")
            for video in video_tags:
                # Get the 'src' attribute of the video tag
                src = video.get_attribute('src')
                if src:
                    video_sources.add(src)
                else:
                    # Check for <source> tags inside the <video>
                    source_tags = video.query_selector_all('source')
                    for source in source_tags:
                        src = source.get_attribute('src')
                        if src:
                            video_sources.add(src)
            
            browser.close()  # Close the browser
            return video_sources

    except Exception as e:
        print(f"Error fetching the webpage: {e}")
        return set()


def eex_vpg(url):
    try:
        # Send a GET request to the webpage
        response = requests.get(url,headers=s_h,cookies=s_c)
        response.raise_for_status()  # Raise an error if the request fails

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
        print(f"Error fetching the webpage: {e}")
        return set()

async def ex_page(task):
    global s_h, s_c
    for ob in site_data:
        v=site_data[ob]
        if ob in task['type']:
           if 'cookie' in v:
              s_c=parse_cookie_str(v['cookie']) 
           if 'headers' in v:
              s_h=v['headers']
    video_srcs = ex_vpg(task['url'])
    if video_srcs:
       print("Video sources found:")
       urls=[]
       for src in video_srcs:
          print(src)
          urls.append(src)
       return urls
    else:
       print("No video sources found.")
       return []
