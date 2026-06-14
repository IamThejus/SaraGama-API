# 🎵 Saragama API

> **Music Infrastructure for Developers**

A free, open music API built on top of YouTube Music — designed for developers building streaming apps, discovery engines, playlist explorers, and experimental music platforms. Clean. Structured. No subscriptions. No ads.

🔗 **Live API:** [https://saragama-render.onrender.com](https://saragama-render.onrender.com)

---

## 📸 Screenshots

**Home**
![Saragama Home](assets/Saragama-api_Home_.png)

**API Reference / Docs**
![Saragama Docs](assets/saragama-api_docs_.png)

---

## ✨ Features

- 🔍 **Song Search / Autocomplete** — Search songs with metadata including artist, thumbnail, and duration
- 🎧 **Recommendations** — Get related tracks based on any YouTube Music video ID
- 📋 **Playlist Fetcher** — Fetch full playlist data by playlist ID
- 📈 **Trending Charts** — Get daily, weekly trending songs and top artists in India
- 🌌 **Gravity Mixes** — Curated, cached mood-based playlists (Focus Flow, Night Drive, Moody, Energy, Feel Good, Discovery)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/SaraGama-API.git
cd SaraGama-API

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The server starts at `http://localhost:8000` by default. You can override the port via the `PORT` environment variable.

### Optional: Redis caching for Gravity Mixes

The `/mixes` endpoint caches its results so they aren't regenerated on every request. By default this cache is an **in-memory dictionary** (no setup required). To use **Redis** instead (recommended for production, since it persists across restarts and can be shared across instances), set the `REDIS_URL` environment variable:

```bash
REDIS_URL=redis://localhost:6379
```

If `REDIS_URL` is not set, or Redis is unreachable, the API automatically falls back to the in-memory cache — no errors, no extra config needed.

---

## 🐳 Docker

```bash
# Build the image
docker build -t saragama-api .

# Run the container
docker run -p 8000:8000 saragama-api
```

---

## 📡 API Endpoints

### Base URL

```
https://saragama-render.onrender.com
```

---

### `GET /`

Returns the interactive API documentation page.

---

### `GET /autocomplete`

Search for songs by query string.

**Query Parameters**

| Parameter | Type   | Required | Description        |
|-----------|--------|----------|--------------------|
| `q`       | string | ✅ Yes   | Search query text  |

**Example Request**
```
GET /autocomplete?q=Kesariya
```

**Example Response**
```json
[
  {
    "title": "Kesariya",
    "video_url": "BddP6PYo2gs",
    "artist": ["Arijit Singh"],
    "thumbnail": "https://...",
    "duration": "4:34"
  }
]
```

---

### `GET /recommendation`

Get up to 10 recommended tracks based on a YouTube Music video ID.

**Query Parameters**

| Parameter  | Type   | Required | Description              |
|------------|--------|----------|--------------------------|
| `video_id` | string | ✅ Yes   | YouTube Music video ID   |

**Example Request**
```
GET /recommendation?video_id=BddP6PYo2gs
```

**Example Response**
```json
[
  {
    "video_id": "abc123",
    "title": "Tum Hi Ho",
    "artist": "Arijit Singh",
    "artist_id": "xyz",
    "album": "Aashiqui 2",
    "duration": "4:22",
    "thumbnail": "https://..."
  }
]
```

---

### `GET /playlist`

Fetch a YouTube Music playlist by its playlist ID.

**Query Parameters**

| Parameter | Type   | Required | Description          |
|-----------|--------|----------|----------------------|
| `playid`  | string | ✅ Yes   | YouTube playlist ID  |

**Example Request**
```
GET /playlist?playid=PLx0sYbCqOb8TBPRdmBHs5Iftvv9TPboYG
```

**Example Response**
```json
{
  "title": "Top Hits",
  "trackCount": 50,
  "tracks": [ ... ]
}
```

> Returns an empty array `[]` if the playlist ID is invalid.

---

### `GET /trending`

Get current trending music charts in India — includes daily picks, weekly charts, and top artists.

**No parameters required.**

**Example Request**
```
GET /trending
```

**Example Response**
```json
{
  "daily": [{ "title": "Trending 20 India" }],
  "weekly": [{ "title": "Top Weekly Videos Punjabi" }],
  "artists": [{ "title": "Alka Yagnik", "rank": "1" }]
}
```

---

### `GET /mixes`

Get six curated "Gravity Mix" playlists generated from YouTube Music's mood & genre categories. Results are **cached** — the mixes are generated once and served from cache on subsequent requests. Use `POST /mixes/refresh` to regenerate them.

**No parameters required.**

**Example Request**
```
GET /mixes
```

**Example Response**
```json
{
  "updated_at": "2026-06-14T10:32:00.123456+00:00",
  "mixes": {
    "focus": {
      "title": "Focus Flow",
      "image": "https://saragama-render.onrender.com/moods/focus.png",
      "trackCount": 20,
      "tracks": [
        {
          "video_id": "abc123",
          "title": "Weightless",
          "artist": "Marconi Union",
          "artist_id": "xyz",
          "album": "Weightless",
          "duration": "8:10",
          "thumbnail": "https://..."
        }
      ]
    },
    "night_drive": { "title": "Night Drive", "image": "https://.../moods/night_drive.png", "trackCount": 20, "tracks": [ ] },
    "moody":       { "title": "Moody",       "image": "https://.../moods/moody.png",       "trackCount": 20, "tracks": [ ] },
    "energy":      { "title": "Energy",      "image": "https://.../moods/energy.png",      "trackCount": 20, "tracks": [ ] },
    "feel_good":   { "title": "Feel Good",   "image": "https://.../moods/feel_good.png",   "trackCount": 20, "tracks": [ ] },
    "discovery":   { "title": "Discovery",   "image": "https://.../moods/discovery.png",   "trackCount": 30, "tracks": [ ] }
  }
}
```

**Mix Composition**

| Mix Key       | Title       | Source Moods                              | Track Count |
|----------------|-------------|--------------------------------------------|--------------|
| `focus`        | Focus Flow  | Focus                                       | 20 |
| `night_drive`  | Night Drive | Chill + Commute                             | 20 |
| `moody`        | Moody       | Sad + Romance                               | 20 |
| `energy`       | Energy      | Energize + Workout                          | 20 |
| `feel_good`    | Feel Good   | Feel good + Party                           | 20 |
| `discovery`    | Discovery   | Focus + Chill + Energize + Feel good        | 30 |

> Tracks are randomly sampled from each mood's playlists, deduplicated by video ID, and shuffled — so each refresh produces a fresh, varied set.

---

### `POST /mixes/refresh`

Regenerate all six Gravity Mixes and replace the cache. Useful for getting a fresh set of tracks on demand (e.g. via a scheduled job).

**No parameters required.**

**Example Request**
```
POST /mixes/refresh
```

**Example Response**
```json
{
  "success": true,
  "message": "Mixes refreshed"
}
```

---

### `GET /moods/{filename}`

Static cover images for the Gravity Mixes, served directly as files.

**Example Request**
```
GET /moods/focus.png
```

Available files: `focus.png`, `night_drive.png`, `moody.png`, `energy.png`, `feel_good.png`, `discovery.png` — these are the same URLs returned in the `image` field of `GET /mixes`.

---

## 🗂️ Project Structure

```
SaraGama-API/
├── main.py            # FastAPI app, route definitions, static file mounting
├── yt_engine.py       # Core YouTube Music logic (search, recommendations, Gravity Mixes, caching)
├── models.py          # Pydantic models
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
├── nixpacks.toml      # Nixpacks deploy configuration (Railway etc.)
├── moods/             # Cover images for Gravity Mixes, served at /moods/*
│   ├── focus.png
│   ├── night_drive.png
│   ├── moody.png
│   ├── energy.png
│   ├── feel_good.png
│   └── discovery.png
└── templates/
    └── index.html     # Interactive API docs landing page
```

---

## 🛠️ Tech Stack

| Layer       | Technology                  |
|-------------|-----------------------------|
| Framework   | FastAPI                     |
| Server      | Uvicorn                     |
| Music Data  | ytmusicapi (YouTube Music)  |
| Templating  | Jinja2                      |
| Caching     | Redis (optional, with in-memory fallback) |
| Container   | Docker                      |

---

## 📦 Dependencies

```
fastapi
uvicorn
python-dotenv
ytmusicapi
Jinja2
python-multipart
redis
```

> `redis` is only used if the `REDIS_URL` environment variable is set and reachable. Without it, the API still runs fully — Gravity Mixes are cached in memory instead.

---

## 🌐 Deployment

This project is deployed on **Render** and configured for platforms that support Nixpacks (like Railway) via `nixpacks.toml`.

The `PORT` environment variable is respected automatically:

```python
port = int(os.environ.get("PORT", 8000))
```

---

## 📄 License

This project is open-source and free to use. Built for developers, by developers.

---

> © 2026 **Saragama** · Music for Everyone · Built for Developers
