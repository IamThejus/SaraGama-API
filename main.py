from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import os
import uvicorn
from ytmusicapi import YTMusic
yt = YTMusic()
from yt_engine import *

app=FastAPI()



templates=Jinja2Templates(directory="templates")



@app.get("/")
def home(request:Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Saramaga API",
            "message": "Music Infrastructure for Developers"
        }
    )

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
