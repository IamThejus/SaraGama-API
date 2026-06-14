# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Saragama API is a small FastAPI service that wraps `ytmusicapi` to expose a free music API (search/autocomplete, recommendations, playlist fetching, trending charts) for developers. The root `/` serves an interactive HTML docs/demo page.

## Running locally

```bash
pip install -r requirements.txt
python main.py
```

The server runs on `http://localhost:8000` by default; respects the `PORT` env var (used on Render/Railway deploys).

There is no test suite, linter, or build step configured in this repo.

## Docker

```bash
docker build -t saragama-api .
docker run -p 8000:8000 saragama-api
```

The Dockerfile intentionally does NOT expose a port or run uvicorn directly — `CMD ["python", "main.py"]` handles binding via the `PORT` env var. Don't add `EXPOSE` or change the CMD to call `uvicorn` directly.

## Architecture

- `main.py` — FastAPI app, CORS setup (`allow_origins=["*"]`), route definitions, and Jinja2 template rendering for the docs page. Creates a module-level `YTMusic()` client (`yt`).
- `yt_engine.py` — Core logic for talking to YouTube Music via `ytmusicapi`: `get_autocomplete`, `get_recommendation`, and the `clean_track` normalizer used to shape track data for API responses. Also instantiates its own `YTMusic()` client. `main.py` does `from yt_engine import *` to pull these in.
- `models.py` — Pydantic models (currently a `SONG` model, not yet wired into any route).
- `templates/index.html` — Single-page interactive docs/demo UI. Endpoint metadata (paths + query params) is duplicated in the `ENDPOINTS` JS object and must be kept in sync with the routes in `main.py` if endpoints change. The `BASE` URL constant points at the deployed Render instance.

## Endpoints (main.py)

- `GET /` — renders `templates/index.html`.
- `GET /playlist?playid=` — fetches a playlist via `yt.get_playlist`, strips `owned`; returns `[]` on any error (broad except).
- `GET /autocomplete?q=` — song search via `yt_engine.get_autocomplete`.
- `GET /trending` — `yt.get_charts(country="IN")`, strips `countries`, and pops index 0 from `daily` because that playlist ID returns `None` (intentional workaround, keep it).
- `GET /recommendation?video_id=` — related tracks via `yt_engine.get_recommendation` (returns tracks 1–10 from `get_watch_playlist`).

## Notes

- Both `main.py` and `yt_engine.py` independently instantiate `YTMusic()` — this duplication exists in the current code.
- `assets/` and `moods/` contain images referenced by the README/docs page; not part of the runtime.
