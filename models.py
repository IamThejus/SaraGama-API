from pydantic import BaseModel



class SONG(BaseModel):
    id:int
    title:str
    artist:str
    url:str