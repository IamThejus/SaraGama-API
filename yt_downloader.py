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
        "user_agent": "Mozilla/5.0",
        "extractor_retries": 5,
        "fragment_retries": 5,
        "sleep_interval": 1,
        "max_sleep_interval": 5,
        "js_runtimes": {"node": {}},
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    return {
        "title": info.get("title"),
        "artist": info.get("uploader"),
    }
