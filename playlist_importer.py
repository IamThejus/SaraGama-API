import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from ytmusicapi import YTMusic
yt = YTMusic()

def get_song_metadata(song_name):
    results = yt.search(song_name, filter="songs",limit=1)

    if not results:
        return None

    song = results[0]

    return {
        "title": song.get("title"),
        "video_url": song.get("videoId"),
        "artist": [
            artist["name"]
            for artist in song.get("artists", [])
        ],
        "thumbnail": (
            song["thumbnails"][-1]["url"]
            if song.get("thumbnails")
            else None
        ),
        "duration": song.get("duration")
    }




def get_apple_playlist(url):
    html = requests.get(url).text

    songs = []

    for match in re.finditer(r'"id":"track-lockup', html):
        chunk = html[match.start():match.start() + 3000]

        m = re.search(r'"title":"((?:\\.|[^"])*)"', chunk)
        if m:
            song_name = json.loads(f'"{m.group(1)}"')
            songs.append(song_name)

    # Save as JSON
    return songs

def get_spotify_playlist(url):
    html = requests.get(url).text

    soup = BeautifulSoup(html, "html.parser")

    songs = []

    for row in soup.select('[data-testid="track-row"]'):
        title = row.get("aria-label")
        if title:
            songs.append(title)
    return songs


def get_playlist_songs(url):
    domain = urlparse(url).netloc.lower()

    if "music.apple.com" in domain:
        return get_apple_playlist(url)

    elif "open.spotify.com" in domain:
        return get_spotify_playlist(url)

    else:
        raise ValueError(f"Unsupported music service: {domain}")
    

