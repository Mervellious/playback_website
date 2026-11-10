import hmac
import os
import re
import secrets
from datetime import date, datetime, timezone

from flask import Flask, abort, jsonify, render_template, request, send_from_directory, session, url_for

app = Flask(__name__)

# Sessions (CSRF tokens) need a secret key. Set SECRET_KEY in production;
# the fallback is for local development only.
app.secret_key = os.environ.get("SECRET_KEY") or "dev-only-change-me"

# ---------------------------------------------------------------------------
# External links — the one place to change them. A link that is empty or still
# contains a "[placeholder]" is treated as not set: its icon is hidden and the
# film button shows "FILM COMING SOON".
# ---------------------------------------------------------------------------
EXTERNAL_LINKS = {
    "film_vimeo": "https://vimeo.com/[FILM-ID]",  # Vimeo link to the film
    "instagram": "https://www.instagram.com/[HANDLE]",
    "tiktok": "https://www.tiktok.com/@[HANDLE]",
    "imdb": "https://www.imdb.com/title/[TITLE-ID]/",
}

SOCIAL_KEYS = ("instagram", "tiktok", "imdb")

# While developing, show placeholder links anyway (pointing at the platform's
# homepage). None = follow app.debug (True with `python app.py` / `flask run
# --debug`, False in production). Set True/False to force it.
SHOW_PLACEHOLDER_LINKS = None

PLATFORM_HOMEPAGES = {
    "film_vimeo": "https://vimeo.com",
    "instagram": "https://www.instagram.com",
    "tiktok": "https://www.tiktok.com",
    "imdb": "https://www.imdb.com",
}


def is_live_link(url):
    """True for a real URL; False for empty or "[placeholder]" values."""
    return bool(url) and "[" not in url


def show_placeholder_links():
    # Read at request time: app.debug is only set once the server starts.
    return app.debug if SHOW_PLACEHOLDER_LINKS is None else SHOW_PLACEHOLDER_LINKS


def link_for(key):
    """How templates render an external link: {"href", "placeholder"} or None (hide it).

    Real link → use it. Placeholder → platform homepage in development, hidden in
    production. (JSON-LD never uses this; it only takes real links.)
    """
    url = EXTERNAL_LINKS.get(key, "")
    if is_live_link(url):
        return {"href": url, "placeholder": False}
    if show_placeholder_links():
        return {"href": PLATFORM_HOMEPAGES[key], "placeholder": True}
    return None


def placeholder_link_keys():
    return [key for key, url in EXTERNAL_LINKS.items() if not is_live_link(url)]


# Film call-to-action label. Switch to e.g. "WATCH THE TRAILER" while the film
# is not public (festivals); the URL is EXTERNAL_LINKS["film_vimeo"].
FILM_CTA_LABEL = "WATCH THE FILM"

# Trailer: a YouTube / Vimeo link or an .mp4 URL. Empty = "coming soon".
TRAILER_URL = ""
TRAILER_UPLOAD_DATE = ""  # e.g. "2026-11-20"; recommended by Google when a trailer is set

DIRECTOR_NAME = "[Director name]"

# ---------------------------------------------------------------------------
# Film — single source of truth for every page (homepage, Press Kit, JSON-LD).
# Placeholders in [brackets] still need to be written.
# ---------------------------------------------------------------------------
FILM = {
    "title": "Playback",
    "genre": "Psychological / Supernatural Thriller",
    "genres": ["Psychological Thriller", "Supernatural Thriller"],
    "runtime": "10 minutes",
    "runtime_minutes": 10,
    "year": "2026",
    "country": "United Kingdom",
    "country_code": "GB",
    "language": "English",
    "writer": "Shae Rozar",
    "director": DIRECTOR_NAME,
    "logline": "[LOGLINE: one sentence — who Daniel is, what he finds, what is at stake]",
    "short_synopsis": (
        "Late at night, alone in his edit suite, exhausted filmmaker Daniel finds "
        "clips on his timeline that he never shot: footage of his own room, ten "
        "minutes in the future. Every clip plays out exactly as recorded. The harder "
        "he tries to break the sequence, the deeper he falls into a time loop of his "
        "own making."
    ),
    "long_synopsis": "[LONG SYNOPSIS: 150–250 words — do not reveal the ending]",
    "director_bio": [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer posuere erat a ante "
        "venenatis dapibus, posuere velit aliquet. Cras mattis consectetur purus sit amet fermentum.",
        "Donec ullamcorper nulla non metus auctor fringilla. Maecenas faucibus mollis interdum. "
        "Nullam quis risus eget urna mollis ornare vel eu leo.",
    ],
    "director_statement": (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum id ligula porta felis "
        "euismod semper. Aenean lacinia bibendum nulla sed consectetur. Etiam porta sem malesuada "
        "magna mollis euismod."
    ),
    "cast": [("Daniel", "[Actor name]")],
    "crew": [
        ("Director", DIRECTOR_NAME),
        ("Writer", "Shae Rozar"),
        ("Producer", "[Name]"),
        ("Director of Photography", "[Name]"),
        ("Editor", "[Name]"),
        ("Sound Designer", "[Name]"),
    ],
    "tech_specs": [
        ("Runtime", "10 minutes"),
        ("Aspect ratio", "[TBC]"),
        ("Shooting format", "[TBC]"),
        ("Sound", "[TBC]"),
        ("Language", "[TBC]"),
        ("Subtitles", "[TBC]"),
        ("Country", "United Kingdom"),
        ("Year", "2026"),
    ],
    "press_email": "press@[domain]",
    "director_email": "director@[domain]",
    "stills": [
        {"key": f"still-{n:02d}", "alt": f"Still {n:02d} from Playback (placeholder): Daniel at his editing desk in the dark"}
        for n in range(1, 7)
    ],
    "posters": [
        {"key": "poster-portrait", "label": "[ POSTER — PORTRAIT ]", "alt": "Playback poster, portrait (placeholder)"},
    ],
    "presskit_zip": "presskit",
}

# ---------------------------------------------------------------------------
# Press kit downloads. Every download goes through /epk/download/<key>, so a
# request form can later be put in front of "gated" files in one place.
# ---------------------------------------------------------------------------
PRESSKIT_DIR = os.path.join(app.static_folder, "presskit")

PRESSKIT_DOWNLOADS = {
    "presskit": {"path": "playback-presskit.zip", "type": "ZIP", "gated": True},
    **{f"still-{n:02d}": {"path": f"stills/still-{n:02d}.jpg", "type": "JPG"} for n in range(1, 7)},
    "poster-portrait": {"path": "posters/poster-portrait.jpg", "type": "JPG"},
    "poster-landscape": {"path": "posters/poster-landscape.jpg", "type": "JPG"},
}


def human_size(num_bytes):
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024 or unit == "GB":
            return f"{num_bytes:.0f} {unit}" if unit in ("B", "KB") else f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024


def get_download(key):
    """Download info for templates: url, static_url, filename, meta ('JPG · 1.6 MB')."""
    item = PRESSKIT_DOWNLOADS.get(key)
    if item is None:
        return None
    full_path = os.path.join(PRESSKIT_DIR, item["path"])
    size = human_size(os.path.getsize(full_path)) if os.path.exists(full_path) else None
    return {
        "key": key,
        "url": url_for("presskit_download", key=key),
        "static_url": url_for("static", filename=f"presskit/{item['path']}"),
        "filename": os.path.basename(item["path"]),
        "meta": f"{item['type']} · {size}" if size else item["type"],
        "gated": item.get("gated", False),
    }

# Menu overlay: (index, label, endpoint)
NAV_ITEMS = [
    ("00", "Home", "index"),
    ("01", "Synopsis", "synopsis"),
    ("02", "Journal", "journal"),
    ("03", "Press Kit", "epk"),
    ("04", "Contact", "contact"),
]

# ---------------------------------------------------------------------------
# Journal — placeholder data. Later this comes from the database; only
# get_journal_entries() reads it, so that is the one place to swap.
# ---------------------------------------------------------------------------
LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer posuere erat "
    "a ante venenatis dapibus, posuere velit aliquet. Cras mattis consectetur purus "
    "sit amet fermentum. Donec ullamcorper nulla non metus auctor fringilla, vitae "
    "elementum leo cursus at."
)
LOREM_LONG = (
    "Maecenas faucibus mollis interdum. Nullam quis risus eget urna mollis ornare vel "
    "eu leo. Vestibulum id ligula porta felis euismod semper. Aenean lacinia bibendum "
    "nulla sed consectetur. Etiam porta sem malesuada magna mollis euismod, sed "
    "posuere consectetur est at lobortis. Curabitur blandit tempus porttitor."
)


def _placeholder_body(quote):
    return {
        "quote": quote,
        "intro": [LOREM, LOREM_LONG],
        "column": [LOREM_LONG, LOREM, LOREM_LONG],
        "column_image": "[ EDIT SUITE ]",
        "full_1": LOREM_LONG + " " + LOREM,
        "pair_images": ["[ PORTRAIT 01 ]", "[ PORTRAIT 02 ]"],
        "pair_text": [LOREM, LOREM_LONG],
        "full_2": LOREM + " " + LOREM_LONG,
    }


JOURNAL_ENTRIES = [
    {
        "slug": "day-01-building-the-edit-suite",
        "day": "DAY 01",
        "date": "2026-11-03",
        "title": "Day 01 — Building the edit suite",
        "excerpt": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Turning an empty room into Daniel's edit suite.",
        "cover_label": "[ SET BUILD ]",
        "body": _placeholder_body("The room had to feel like it had been lived in for years — by someone who never sleeps."),
    },
    {
        "slug": "day-02-lighting-a-room-at-3am",
        "day": "DAY 02",
        "date": "2026-11-04",
        "title": "Day 02 — Lighting a room at 3 a.m.",
        "excerpt": "Integer posuere erat a ante venenatis dapibus. Monitor glow, one practical, and a lot of black.",
        "cover_label": "[ LIGHTING TEST ]",
        "body": _placeholder_body("The only light in the room is the footage. Everything else has to disappear."),
    },
    {
        "slug": "day-03-the-footage-that-wasnt-there",
        "day": "DAY 03",
        "date": "2026-11-05",
        "title": "Day 03 — The footage that wasn't there",
        "excerpt": "Cras mattis consectetur purus sit amet fermentum. Shooting the clips Daniel never shot.",
        "cover_label": "[ MONITOR INSERT ]",
        "body": _placeholder_body("We shot the future first, so the present had something to catch up with."),
    },
]


def get_journal_entries():
    """All journal entries, oldest first. Swap this for a database query later."""
    return sorted(JOURNAL_ENTRIES, key=lambda entry: entry["date"])


def get_journal_entry(slug):
    """(entry, previous, next) for a slug, or (None, None, None)."""
    entries = get_journal_entries()
    for i, entry in enumerate(entries):
        if entry["slug"] == slug:
            prev_entry = entries[i - 1] if i > 0 else None
            next_entry = entries[i + 1] if i + 1 < len(entries) else None
            return entry, prev_entry, next_entry
    return None, None, None


@app.template_filter("display_date")
def display_date(iso):
    """'2026-11-03' → '3 NOV 2026'."""
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b').upper()} {d.year}"


@app.context_processor
def site_context():
    current = request.endpoint
    return {
        "nav_items": NAV_ITEMS,
        "current_section": "journal" if current == "journal_entry" else current,
        "director_name": DIRECTOR_NAME,
        "external_links": EXTERNAL_LINKS,
        "is_live_link": is_live_link,
        "link_for": link_for,
        # Listed on <body> in development so main.js can log one warning.
        "placeholder_links": placeholder_link_keys() if show_placeholder_links() else [],
    }


# ---------------------------------------------------------------------------
# Structured data
# ---------------------------------------------------------------------------
def poster_url():
    return url_for("static", filename="img/hero-poster-placeholder.png", _external=True)


def trailer_embed(url):
    """Turn TRAILER_URL into {"kind": "iframe" | "video", "src": ...}, or None."""
    if not url:
        return None
    youtube = re.search(r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([\w-]{11})", url)
    if youtube:
        return {"kind": "iframe", "src": f"https://www.youtube-nocookie.com/embed/{youtube.group(1)}?autoplay=1&rel=0"}
    vimeo = re.search(r"vimeo\.com/(?:video/)?(\d+)", url)
    if vimeo:
        return {"kind": "iframe", "src": f"https://player.vimeo.com/video/{vimeo.group(1)}?autoplay=1"}
    if url.lower().split("?")[0].endswith(".mp4"):
        return {"kind": "video", "src": url}
    return None


def movie_jsonld(trailer):
    data = {
        "@context": "https://schema.org",
        "@type": "Movie",
        "name": FILM["title"],
        "genre": FILM["genres"],
        "duration": f"PT{FILM['runtime_minutes']}M",
        "countryOfOrigin": {"@type": "Country", "name": FILM["country_code"]},
        "dateCreated": FILM["year"],
        "author": {"@type": "Person", "name": FILM["writer"]},
        "creator": {"@type": "Person", "name": FILM["writer"]},
        "description": FILM["short_synopsis"],
        "image": poster_url(),
    }
    if is_live_link(EXTERNAL_LINKS["film_vimeo"]):
        data["url"] = EXTERNAL_LINKS["film_vimeo"]
    same_as = [EXTERNAL_LINKS[key] for key in SOCIAL_KEYS if is_live_link(EXTERNAL_LINKS[key])]
    if same_as:
        data["sameAs"] = same_as
    if trailer:
        video = {
            "@type": "VideoObject",
            "name": "Playback — Trailer",
            "description": FILM["short_synopsis"],
            "thumbnailUrl": poster_url(),
        }
        video["embedUrl" if trailer["kind"] == "iframe" else "contentUrl"] = trailer["src"]
        if TRAILER_UPLOAD_DATE:
            video["uploadDate"] = TRAILER_UPLOAD_DATE
        data["trailer"] = video
    return data


def blog_posting_jsonld(entry):
    url = url_for("journal_entry", slug=entry["slug"], _external=True)
    return {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": entry["title"],
        "description": entry["excerpt"],
        "datePublished": entry["date"],
        "author": {"@type": "Person", "name": DIRECTOR_NAME},
        "image": poster_url(),
        "url": url,
        "mainEntityOfPage": url,
        "isPartOf": {"@type": "Movie", "name": "Playback", "url": url_for("index", _external=True)},
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    trailer = trailer_embed(TRAILER_URL)
    return render_template(
        "index.html",
        film_cta_label=FILM_CTA_LABEL,
        trailer_url=TRAILER_URL,
        trailer=trailer,
        film=FILM,
        movie_jsonld=movie_jsonld(trailer),
    )


@app.route("/journal")
def journal():
    return render_template("journal/index.html", entries=get_journal_entries())


@app.route("/journal/<slug>")
def journal_entry(slug):
    entry, prev_entry, next_entry = get_journal_entry(slug)
    if entry is None:
        abort(404)
    return render_template(
        "journal/entry.html",
        entry=entry,
        prev_entry=prev_entry,
        next_entry=next_entry,
        jsonld=blog_posting_jsonld(entry),
    )


@app.route("/epk")
def epk():
    return render_template(
        "epk.html",
        film=FILM,
        get_download=get_download,
        movie_jsonld=movie_jsonld(trailer_embed(TRAILER_URL)),
    )


@app.route("/epk/download/<key>")
def presskit_download(key):
    item = PRESSKIT_DOWNLOADS.get(key)
    if item is None:
        abort(404)
    # Later: if item.get("gated"), show the request form (name, outlet, email) first.
    return send_from_directory(PRESSKIT_DIR, item["path"], as_attachment=True)


# Placeholder pages until they are designed.
@app.route("/synopsis")
def synopsis():
    return render_template("placeholder.html", page_title="Synopsis")




# ---------------------------------------------------------------------------
# Contact form
# ---------------------------------------------------------------------------
CONTACT_TOPICS = ["FESTIVAL", "PRESS", "DISTRIBUTION", "JUST SAYING HI"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def csrf_token():
    """Per-session CSRF token, rendered as a hidden field."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def csrf_is_valid(token):
    expected = session.get("csrf_token")
    return bool(expected and token) and hmac.compare_digest(expected, token)


def validate_contact(form):
    """Same rules as static/js/contact.js. Returns (data, errors)."""
    data = {
        "topic": form.get("topic", ""),
        "name": form.get("name", "").strip(),
        "email": form.get("email", "").strip(),
        "message": form.get("message", "").strip(),
        "consent": form.get("consent") == "yes",
    }
    errors = {}
    if data["topic"] not in CONTACT_TOPICS:
        errors["topic"] = "Choose what your message is about."
    if not data["name"]:
        errors["name"] = "Enter your name."
    elif len(data["name"]) > 100:
        errors["name"] = "Keep your name under 100 characters."
    if not data["email"]:
        errors["email"] = "Enter your email address."
    elif len(data["email"]) > 254 or not EMAIL_RE.match(data["email"]):
        errors["email"] = "Enter a valid email address, like name@example.com."
    if not data["message"]:
        errors["message"] = "Write your message."
    elif len(data["message"]) > 5000:
        errors["message"] = "Keep your message under 5000 characters."
    if not data["consent"]:
        errors["consent"] = "Tick the box so we can store your message and reply."
    return data, errors


def save_contact_message(data):
    # TODO: store in the database (topic, name, email, message, consent, created_at).
    record = {**data, "created_at": datetime.now(timezone.utc).isoformat()}
    app.logger.info("Contact message received: %s", record)


@app.context_processor
def csrf_context():
    return {"csrf_token": csrf_token}


@app.route("/contact", methods=["GET", "POST"])
def contact():
    wants_json = request.accept_mimetypes.best == "application/json"
    jsonld = {
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "name": "Contact · Playback",
        "url": url_for("contact", _external=True),
        "description": "Contact the Playback team: festival, press and distribution enquiries.",
        "about": {"@type": "Movie", "name": FILM["title"], "url": url_for("index", _external=True)},
    }

    def page(status=200, **context):
        context = {"errors": {}, "values": {}, "sent": False, "form_error": None, **context}
        return render_template("contact.html", film=FILM, topics=CONTACT_TOPICS, jsonld=jsonld, **context), status

    if request.method == "GET":
        return page()

    if not csrf_is_valid(request.form.get("csrf_token", "")):
        if wants_json:
            return jsonify(ok=False, error="Your session expired. Reload the page and try again."), 400
        return page(400, form_error="Your session expired. Please try again.", values=request.form)

    # Honeypot: bots fill the hidden "website" field. Pretend it worked, store nothing.
    if request.form.get("website"):
        return jsonify(ok=True) if wants_json else page(sent=True)

    data, errors = validate_contact(request.form)
    if errors:
        if wants_json:
            return jsonify(ok=False, errors=errors), 400
        return page(400, errors=errors, values=request.form)

    save_contact_message(data)
    return jsonify(ok=True) if wants_json else page(sent=True)


@app.route("/privacy")
def privacy():
    return render_template("placeholder.html", page_title="Privacy", label="PRIVACY")


if __name__ == "__main__":
    app.run(debug=True)
