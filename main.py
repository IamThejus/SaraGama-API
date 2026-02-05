from fastapi import FastAPI,BackgroundTasks
from yt_downloader import *
from models import *
from superdb import *
from upload_song_cloudinary import *

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


@app.post("/addsong")
def add_song_to_library(url:str,background_task:BackgroundTasks):
    background_task.add_task(add_song,url)
    return True
