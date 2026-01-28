import aiohttp
from urllib.parse import urljoin

MAX_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
PREFERRED_QUALITY = 720


async def get_best_quality_under_2gb(obj):
    streams = [
        {**s, "quality": int(s.get("quality", 0))}
        for s in obj["videos"][0]["streams"]
    ]

    # 🔹 Sort: 720p first, then highest → lowest
    streams.sort(
        key=lambda s: (
            s["quality"] != PREFERRED_QUALITY,
            -s["quality"]
        )
    )

    async with aiohttp.ClientSession() as session:
        for stream in streams:
            url = stream["url"]

            try:
                # ================= MP4 =================
                if ".mp4" in url and not url.endswith(".m3u8"):
                    async with session.head(url, allow_redirects=True) as resp:
                        size = int(resp.headers.get("Content-Length", 0))

                        if 0 < size <= MAX_SIZE:
                            return {
                                "quality": stream["quality"],
                                "url": url,
                                "type": "mp4",
                                "sizeBytes": size,
                                "sizeGB": round(size / 1024 / 1024 / 1024, 2)
                            }

                # ================= M3U8 =================
                if ".m3u8" in url:
                    async with session.get(url) as resp:
                        playlist = await resp.text()

                    base_url = url.rsplit("/", 1)[0] + "/"
                    segments = [
                        urljoin(base_url, line.strip())
                        for line in playlist.splitlines()
                        if line and not line.startswith("#")
                    ]

                    total_size = 0

                    for seg in segments:
                        async with session.head(seg, allow_redirects=True) as resp:
                            seg_size = int(resp.headers.get("Content-Length", 0))
                            total_size += seg_size

                            if total_size > MAX_SIZE:
                                break

                    if 0 < total_size <= MAX_SIZE:
                        return {
                            "quality": stream["quality"],
                            "url": url,
                            "type": "m3u8",
                            "sizeBytes": total_size,
                            "sizeGB": round(total_size / 1024 / 1024 / 1024, 2)
                        }

            except Exception:
                continue  # try next quality

    return None

def get_video_title(obj):
    try:
        return obj["videos"][0]["title"]
    except (KeyError, IndexError, TypeError):
        return "UnknownTitle_yy"


def get_video_thumbnail(obj):
    try:
        return obj["videos"][0]["thumbnail"]
    except (KeyError, IndexError, TypeError):
        return None

def getExDXham(obj):
    return {
        title:get_video_title(obj),
        thumb:get_video_thumbnail(obj),
        video:get_best_quality_under_2gb(obj)
    }
        

