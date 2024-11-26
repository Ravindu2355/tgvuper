import requests
from bs4 import BeautifulSoup

def extract_video_src(url):
    try:
        # Send a GET request to the webpage
        response = requests.get(url)
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


video_srcs = ex_pg(url)
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
