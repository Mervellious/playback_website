# Playback — website

Flask site for *Playback*, a psychological thriller short film.

## Run locally

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/flask --app app run --debug --port 5001
```

## Deploy (Render, free web service)

Create a **Web Service** from this GitHub repo with:

| Setting | Value |
|---|---|
| Runtime | Python 3 |
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn app:app` |
| Environment variable | `SECRET_KEY` = a long random string, e.g. the output of `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` |

Notes:
- Under gunicorn the app runs with debug off, and placeholder links (`[...]` values in `EXTERNAL_LINKS`) are hidden.
- If `SECRET_KEY` is missing, the app logs a warning and falls back to an insecure development key; set it before going live.
- `static/video/*.mp4` is git-ignored, so the hero shows only its poster until a trimmed `hero.mp4` (< 10 MB) is added with `git add -f static/video/hero.mp4`.
