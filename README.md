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
- Optional environment variable `SHOW_PLACEHOLDER_LINKS`: `1`/`true` shows the placeholder social icons on the live site as disabled "Coming soon" icons (`href="#"`, nothing happens on click); `0`/`false` always hides them; not set = hidden under gunicorn, shown locally in debug mode. The film button stays "FILM COMING SOON" until the real Vimeo link is set.
- If `SECRET_KEY` is missing, the app logs a warning and falls back to an insecure development key; set it before going live.
- `static/video/*.mp4` is git-ignored; only the trimmed 6 s `hero.mp4` is committed (added with `git add -f`). Re-add it the same way after replacing it.
