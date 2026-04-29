from fastapi import FastAPI
from ytmusicapi import YTMusic

yt = YTMusic()

def clean_track(track):
    return {
        "video_id": track["videoId"],
        "title": track["title"],
        "artist": track["artists"][0]["name"] if track.get("artists") else None,
        "artist_id": track["artists"][0]["id"] if track.get("artists") else None,
        "album": track["album"]["name"] if track.get("album") else None,
        "duration": track.get("length"),
        "thumbnail": track["thumbnail"][-1]["url"]  # highest quality only
    }


def get_recommendation(video_id:str):
    watch_data = yt.get_watch_playlist(video_id)
    recommended = [clean_track(t) for t in watch_data["tracks"][1:11]]
    return recommended


def get_autocomplete(q):
    collection=[]
    if q=="suttuxtheju":
        data=yt.search("Javeda Zindagi", filter="songs",)
        data=[data[0]]
        for i in data:
            result={}
            result["title"]=i["title"]
            result["video_url"]=i["videoId"]
            result["artist"]=[artist["name"] for artist in i["artists"]]
            result["thumbnail"]="https://res.cloudinary.com/dnech6xpw/image/upload/v1777489604/suttuxthejus_gzj27q.jpg"
            result["duration"]=i["duration"]
            collection.append(result)
        return collection
        
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
