from fastapi import FastAPI

import os
import uvicorn
from ytmusicapi import YTMusic
yt = YTMusic()

app=FastAPI()




@app.get("/")
def home():
    return "Welcome to saragama server (Render)"

@app.get("/playlist")
def get_playlist(playid:str):
    playlist = yt.get_playlist(playid)   
    del playlist["owned"] 
    return playlist

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

@app.get("/gettrending")
def get_yt_trending():
    result=yt.get_charts(country="IN")
    del result["countries"]
    return result





if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
