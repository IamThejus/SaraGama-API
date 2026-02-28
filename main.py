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
    collection=[]
    data=yt.search(q, filter="songs",)
    for i in data:
        result={}
        result["title"]=i["title"]
        result["video_url"]=i["videoId"]
        result["artist"]=[artist["name"] for artist in i["artists"]]
        result["thumbnail"]=i["thumbnails"][-1]["url"]
        result["duration"]=i["duration"]
        collection.append(result)
    return collection

@app.get("/getupdates")
def get_yt_updates():
    result=yt.get_charts(country="IN")
    del result["countries"]
    return result


@app.post("/addsong")
def add_song_to_library(url:str,background_task:BackgroundTasks):
    background_task.add_task(add_song,url)
    return True


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
