from fastapi import FastAPI
from ytmusicapi import YTMusic
import os
import json
import math
import random
from datetime import datetime, timezone

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


# ---------------------------------------------------------------------------
# Gravity Mixes
# ---------------------------------------------------------------------------
# Each mix is built by sampling tracks from one or more ytmusicapi "mood"
# categories. The category param strings are discovered at runtime via
# yt.get_mood_categories() (they are not stable, so we never hardcode them).

# Mix key -> definition. The key doubles as the image filename: moods/<key>.png
MIX_DEFINITIONS = {
    "focus":       {"title": "Focus Flow", "moods": ["Focus"],                          "size": 20},
    "night_drive": {"title": "Night Drive", "moods": ["Chill", "Commute"],              "size": 20},
    "moody":       {"title": "Moody",       "moods": ["Sad", "Romance"],                "size": 20},
    "energy":      {"title": "Energy",      "moods": ["Energize", "Workout"],           "size": 20},
    "feel_good":   {"title": "Feel Good",   "moods": ["Feel good", "Party"],            "size": 20},
    "discovery":   {"title": "Discovery",   "moods": ["Focus", "Chill", "Energize", "Feel good"], "size": 30},
}

# Tolerant matching for category titles that vary across ytmusicapi versions.
_MOOD_ALIASES = {
    "energy": ["energize"],
    "energize": ["energy"],
    "feel good": ["feelgood", "feel-good"],
    "feelgood": ["feel good"],
}


def clean_mix_track(track):
    """Normalize a playlist track into the same shape used elsewhere in the API.

    Mood/playlist tracks expose `thumbnails` and `duration`, unlike watch-list
    tracks (handled by clean_track), so this cleaner is defensive about keys.
    """
    return {
        "video_id": track.get("videoId"),
        "title": track.get("title"),
        "artist": track["artists"][0]["name"] if track.get("artists") else None,
        "artist_id": track["artists"][0]["id"] if track.get("artists") else None,
        "album": track["album"]["name"] if track.get("album") else None,
        "duration": track.get("duration"),
        "thumbnail": track["thumbnails"][-1]["url"] if track.get("thumbnails") else None,
    }


def dedupe_tracks(tracks):
    """Drop tracks with duplicate (or missing) video IDs, preserving order."""
    seen = set()
    unique = []
    for track in tracks:
        vid = track.get("videoId")
        if vid and vid not in seen:
            seen.add(vid)
            unique.append(track)
    return unique


def _get_mood_param_map():
    """Build a {lowercased category title: params} map from ytmusicapi."""
    param_map = {}
    categories = yt.get_mood_categories()
    for group in categories.values():
        for cat in group:
            param_map[cat["title"].strip().lower()] = cat["params"]
    return param_map


def _resolve_mood_params(mood_titles, param_map):
    """Resolve human mood names to category params, trying aliases on miss."""
    resolved = []
    for name in mood_titles:
        key = name.strip().lower()
        params = param_map.get(key)
        if not params:
            for alt in _MOOD_ALIASES.get(key, []):
                params = param_map.get(alt)
                if params:
                    break
        if params:
            resolved.append(params)
    return resolved


def get_mix_tracks(mood_titles, param_map, mix_size=20, playlists_per_mood=3):
    """Sample, dedupe and shuffle tracks across the given mood categories."""
    params_list = _resolve_mood_params(mood_titles, param_map)
    if not params_list:
        return []

    raw = []
    for params in params_list:
        try:
            playlists = yt.get_mood_playlists(params)[:playlists_per_mood]
        except Exception as e:
            print(f"Failed to load mood playlists ({params}): {e}")
            continue
        if not playlists:
            continue

        # Ceiling division so the combined pool can reach mix_size before we
        # dedupe and truncate; integer floor would routinely fall short.
        songs_per_playlist = max(
            1, math.ceil(mix_size / (len(params_list) * len(playlists)))
        )

        for playlist in playlists:
            try:
                data = yt.get_playlist(playlist["playlistId"], limit=100)
                tracks = data.get("tracks", [])
            except Exception as e:
                print(f"Failed playlist {playlist.get('title')}: {e}")
                continue

            if len(tracks) > songs_per_playlist:
                selected = random.sample(tracks, songs_per_playlist)
            else:
                selected = tracks
            raw.extend(selected)

    raw = dedupe_tracks(raw)
    random.shuffle(raw)
    raw = raw[:mix_size]
    return [clean_mix_track(t) for t in raw]


def generate_mixes(base_url=""):
    """Generate the full set of Gravity mixes and return the cache payload."""
    base_url = base_url.rstrip("/")
    param_map = _get_mood_param_map()

    mixes = {}
    for key, cfg in MIX_DEFINITIONS.items():
        tracks = get_mix_tracks(cfg["moods"], param_map, mix_size=cfg["size"])
        mixes[key] = {
            "title": cfg["title"],
            "image": f"{base_url}/moods/{key}.png",
            "trackCount": len(tracks),
            "tracks": tracks,
        }

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "mixes": mixes,
    }


# ---------------------------------------------------------------------------
# Cache: Redis if REDIS_URL is set and reachable, else in-memory dict.
# ---------------------------------------------------------------------------
_CACHE_KEY = "gravity:mixes"
_memory_cache = {}

_redis = None
try:
    import redis  # optional dependency
    _redis_url = os.environ.get("REDIS_URL")
    if _redis_url:
        _redis = redis.from_url(_redis_url, decode_responses=True)
        _redis.ping()
except Exception as e:
    print(f"Redis unavailable, falling back to in-memory cache: {e}")
    _redis = None


def get_cached_mixes():
    """Return the cached mixes payload, or None if nothing is cached yet."""
    if _redis:
        try:
            data = _redis.get(_CACHE_KEY)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Redis read failed, using in-memory cache: {e}")
    return _memory_cache.get(_CACHE_KEY)


def set_cached_mixes(payload):
    """Persist the mixes payload to Redis (preferred) or the in-memory dict."""
    if _redis:
        try:
            _redis.set(_CACHE_KEY, json.dumps(payload))
            return
        except Exception as e:
            print(f"Redis write failed, using in-memory cache: {e}")
    _memory_cache[_CACHE_KEY] = payload


def refresh_mixes(base_url=""):
    """Regenerate all mixes and replace the cache. Returns the new payload."""
    payload = generate_mixes(base_url)
    set_cached_mixes(payload)
    return payload
