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
- `static/video/*.mp4` is git-ignored; only the trimmed 6 s `hero.mp4` is committed (added with `git add -f`). Re-add it the same way after replacing it.
