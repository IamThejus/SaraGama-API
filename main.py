from fastapi import FastAPI,BackgroundTasks
from yt_downloader import *
from models import *
from superdb import *
from upload_song_cloudinary import *
import os
import uvicorn
from ytmusicapi import YTMusic
yt = YTMusic()

app=FastAPI()

def add_song(url:str):
    current_id=get_latest_id()
    payload=download_music(url)
    song_id=current_id+1
    song_url=upload_song(song_id)
    payload.update({
        "id":song_id,
        "url":song_url
    })
    song=SONG(**payload)
    status=add_music(song)
    if status:
        return True
    else:
        return False


@app.get("/")
def home():
    return "Welcome to saragama server (Railway)"

@app.get("/autocomplete")
def autocomplete(q: str):
    if len(q) < 2:
        return []

    data = yt.search(q, filter="songs", limit=8)
    return [i["title"] for i in data if "title" in i]


@app.post("/addsong")
def add_song_to_library(url:str,background_task:BackgroundTasks):
    background_task.add_task(add_song,url)
    return True


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
