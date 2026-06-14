from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
from ytmusicapi import YTMusic
from fastapi.middleware.cors import CORSMiddleware
from playlist_importer import get_playlist_songs

yt = YTMusic()
from yt_engine import *

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



templates=Jinja2Templates(directory="templates")

# Serve mood cover art at /moods/<name>.png
app.mount("/moods", StaticFiles(directory="moods"), name="moods")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
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
    result["daily"].pop(0)             ## Added this because,the playlistid of that index returns none
    return result


@app.get("/recommendation")
def get_recommend(video_id:str):
    return get_recommendation(video_id=video_id)


@app.get("/mixes")
def get_mixes(request: Request):
    # Serve from cache; generate lazily on the first request only.
    cached = get_cached_mixes()
    if cached is None:
        cached = refresh_mixes(base_url=str(request.base_url))
    return cached


@app.post("/mixes/refresh")
def post_mixes_refresh(request: Request):
    refresh_mixes(base_url=str(request.base_url))
    return {"success": True, "message": "Mixes refreshed"}

@app.post("/import-playlist")
async def import_playlist(url: str):
    result = get_playlist_songs(url)
    return result


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
