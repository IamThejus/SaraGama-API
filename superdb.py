from pymongo import MongoClient
from models import *

uri = "mongodb+srv://thejus:thejusnikarthil2004@saragamamusicapp.7ajufza.mongodb.net/?appName=SaraGamaMusicAPP"
client = MongoClient(uri)
database = client["SaraGama"]
songlibrary=database["SongLibrary"]

def add_music(music:SONG):
    try:
        songlibrary.insert_one(music.model_dump())
        return True
    except:
        return False
    
def get_songs():
    try:
        songs=list(songlibrary.find({},{"_id":0}))
        return songs
    except:
        return None

def get_latest_id():
    try:
        songlibrary=database["SongLibrary"]
        songs=songlibrary.find_one(sort=[("_id",-1)])
        return songs["id"]
    except:
        return None


