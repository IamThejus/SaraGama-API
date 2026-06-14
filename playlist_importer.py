import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse



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
    

