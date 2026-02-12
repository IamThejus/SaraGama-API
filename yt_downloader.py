import os
import tempfile
import yt_dlp

def download_music(url):
    cookies = os.getenv("YT_COOKIES")
    print("YT_COOKIES exists:", bool(cookies))
    print("YT_COOKIES length:", len(cookies) if cookies else 0)
    if not cookies:
        raise Exception("YT_COOKIES environment variable not set")

    # Write cookies to temp file
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        f.write(cookies)
        cookie_path = f.name

    ydl_opts = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "outtmpl": "audio.%(ext)s",
    "cookies": cookie_path,

    # 🔥 MUST look like a real Chrome browser
    "user_agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),

    # 🔥 Extra headers matter on cloud IPs
    "http_headers": {
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.youtube.com/",
        "DNT": "1",
    },

    # Stability
    "extractor_retries": 10,
    "fragment_retries": 10,
    "sleep_interval": 2,
    "max_sleep_interval": 6,

    # JS challenge support
    "js_runtimes": {"node": {}},
    "geo_bypass": True,

    # Noise reduction
    "quiet": True,
    "no_warnings": True,
}


    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    return {
        "title": info.get("title"),
        "artist": info.get("uploader"),
    }
