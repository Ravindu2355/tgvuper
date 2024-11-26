import requests
from bs4 import BeautifulSoup
from res.ex_help import site_data
from res.cookie import parse_cookie_str

s_h = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
s_c={}
def ex_vpg:
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

async def ex_pg(task):
    global s_h, s_c
    for ob in site_data:
        v=site_data[ob]
        if ob in task['type']:
           if v['cookie']:
              s_c=parse_cookie_str(v['cookie']) 
           if v['headers']:
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
