from fastapi import FastAPI

import os
import uvicorn
from ytmusicapi import YTMusic
yt = YTMusic()
from yt_engine import *

app=FastAPI()




@app.get("/")
def home():
    return "Welcome to saragama server (Render)"

@app.get("/playlist")
def get_playlist(playid:str):
    try:
        playlist = yt.get_playlist(playid)   
        del playlist["owned"]
    except:
        return [] 
    return playlist

@app.get("/autocomplete")
def autocomplete(q: str):
    return get_autocomplete(q)

@app.get("/trending")
def get_yt_trending():
    result=yt.get_charts(country="IN")
    del result["countries"]
    return result


@app.get("/recommendation")
def get_recommend(video_id:str):
    return get_recommendation(video_id=video_id)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
