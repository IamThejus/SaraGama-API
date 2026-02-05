import yt_dlp


def download_music(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,         
        "outtmpl": "audio.%(ext)s",
        "js_runtimes": {"node": {}}
    ,     # recommended
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return {
        "title":info["title"],
        "artist":info["uploader"]
    }
