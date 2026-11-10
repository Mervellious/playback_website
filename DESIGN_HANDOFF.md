# PLAYBACK — Landing Page · Design Handoff (v2)

Website for **Playback**, a 10-minute psychological / supernatural thriller (UK, 2026, written by Shae Rozar).
This document is the single source of truth for the landing page. **v2 replaces v1.** Where the current code differs from this file, this file wins.

**Concept:** the landing page is a professional **camera monitor / viewfinder**. The moment the page opens, the camera is **already recording** Daniel at his edit desk; the user secretly watches. Simple REC / PLAY / STOP controls let them stop, play back or continue. Scrolling down asks the question the hero sets up — *"Curious to see who is watching him?"* — and leads to **WATCH THE FILM**.

---

## 0. What changed from v1

| v1 | v2 |
|---|---|
| Page opened in STBY, one big REC button in the middle | Page opens **recording** (REC mode, timecode running from 00:00:00:00) |
| One REC/STOP toggle | **Three buttons: REC, PLAY, STOP** |
| Bottom status bar (○ STBY / ● REC) under the frame | **Removed.** The active button's glow + the timecode colour show the mode |
| Clip name, "A 18 min" in bottom bar | Clip name removed; "A / 18 min" moved to the left tag column |
| No hero copy | Hero line inside the frame: *"Daniel is editing alone, late at night. Someone is watching."* |
| No scroll | Long blue-glow **scroll arrow** under the frame → new section **"Curious to see who is watching him?"** + **WATCH THE FILM** |
| Sound planned | **No sound at all** for now. Video is always muted |
| Camera values in the top bar, tags outside the frame | **Website layer vs camera layer:** outside the frame = website (menu + logo, divider); inside the frame = camera (info strip with timecode, tags, controls). Frame grows to 1312 × 708 |

---

## 1. Project structure (unchanged — Flask-ready)

```
PLAYBACK_Website/
├── app.py                 # routes, FILM data, EXTERNAL_LINKS (§16), trailer config, downloads, journal data
├── requirements.txt
├── templates/
│   ├── base.html          # <head>, inner-page nav, footer, menu overlay (§10–11)
│   ├── _nav.html          # nav row partial (menu button, centred logo, divider)
│   ├── index.html         # homepage (extends base)
│   ├── placeholder.html   # /synopsis, /privacy (noindex)
│   ├── contact.html       # /contact (§17)
│   ├── epk.html           # /epk Press Kit (§15)
│   ├── _downloads.html    # download_link() macro (§15)
│   ├── _social.html       # social icon links (§16)
│   └── journal/
│       ├── index.html     # /journal (§13)
│       └── entry.html     # /journal/<slug> (§14)
└── static/
    ├── css/style.css
    ├── js/main.js
    ├── js/contact.js      # contact form, loaded only on /contact (§17)
    ├── img/hero-poster-placeholder.png
    ├── presskit/          # ZIP, stills/*.jpg, posters/*.jpg (placeholders)
    └── video/hero.mp4    # hero video (no audio)
```

Plain HTML / CSS / vanilla JS. Use `url_for('static', ...)`. All repeated values as CSS custom properties.

**CTA config:** the film button's label is `FILM_CTA_LABEL` in `app.py` (switch to e.g. "WATCH THE TRAILER" during festivals); its URL is `EXTERNAL_LINKS["film_vimeo"]` (§16).

---

## 2. Design tokens

### Colours
| Token | Value | Use |
|---|---|---|
| `--black` | `#030303` | page background |
| `--frame-bg` | `#02040A` | video frame background |
| `--midnight` | `#072044` | glows, gradients |
| `--indigo` | `#1C1CA0` | background glow |
| `--electric` | `#0A43FF` | tags, corner marks, button borders, glows, PLAY active |
| `--electric-light` | `#8FB0FF` | timecode while PLAYing |
| `--white` | `#F5F5F5` | text, icons |
| `--soft-white` | `#D6D6D6` | secondary text |
| `--camera-text` | `#AFC0E6` | camera info values (24 FPS, SHUTTER, 3200K) |
| `--label` | `#8E96A6` | section labels, fact labels |
| `--grey` | `#B0B0B0` | "TRAILER COMING SOON" |
| `--line` | `1px solid rgba(176,176,176,.14)` | section and fact dividers |
| `--rec-red` | `#FF2B2B` | REC dot, timecode while recording |

### Typography (Google Fonts)
`https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap`

| Role | Font | Settings |
|---|---|---|
| Logo `<h1>` "PLAYBACK" | Archivo | `font-stretch: 62%`, 800, 40px, letter-spacing .04em |
| Hero line | Inter | **700**, 32px, line-height 1.35 |
| Tags | Archivo | `font-stretch: 87%`, 500 (tags 700) |
| Timecode | Archivo | `font-stretch: 87%`, 600, 40px, letter-spacing .04em |
| Camera info values | JetBrains Mono | 14px, letter-spacing .12em, `#AFC0E6` |
| "Curious…" heading | Archivo | `font-stretch: 62%`, 800, `clamp(48px, 7vw, 104px)`, line-height .95 |
| CTA button label | JetBrains Mono | 13px, letter-spacing .2em, uppercase |

`font-variant-numeric: tabular-nums` on the page.

### Effects
- **Blue-glow button:** `border: 1px solid rgba(10,67,255,.6); border-radius: 10px; background: radial-gradient(120% 120% at 50% 50%, rgba(10,67,255,.22) 0%, rgba(7,32,68,.7) 60%, #04070F 100%); box-shadow: 0 0 22px -2px rgba(10,67,255,.7), inset 0 0 10px rgba(10,67,255,.25);`
- **Blue tag:** `background: #0A43FF; border-radius: 3px; font-weight: 700; box-shadow: 0 0 16px -2px rgba(10,67,255,.8);`
- **Corner marks:** 2px solid `#0A43FF`, `filter: drop-shadow(0 0 6px rgba(10,67,255,.9))`.

---

## 3. Hero — desktop reference 1440 × 900 (fills the first viewport: `100vh` / `100dvh`)

```
┌───────────────────────────────────────────────────────────────────────┐
│ [≡] PLAYBACK                                                          │ row 1: website nav
│ ───────────────────────────────────────────────────────────────────── │ divider (top 72px)
│  Daniel is editing alone, late at night. Someone is watching.         │ hero line
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ ⌜     24 FPS     00:00:12:08     SHUTTER 180.0°  3200K        ⌝ │  │ camera info strip
│  │ CAM                                                             │  │
│  │ LOG                                                             │  │
│  │ 6K                     (video / poster)                         │  │
│  │17:9                                                             │  │
│  │  A                                                              │  │
│  │18min                                                            │  │
│  │                      ( ● )  ( ▶ )  ( ■ )                        │  │
│  │ ⌞                                                             ⌟ │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                  ↓   (long glowing scroll arrow)      │
└───────────────────────────────────────────────────────────────────────┘
```

**Principle:** outside the video frame = **website** layer; inside the video frame = **camera** layer.

### 3.1 Background glow
Ellipse 1120×640 at (160, 120): `radial-gradient(closest-side, rgba(28,28,160,.5), rgba(7,32,68,.35) 55%, transparent 100%)`, `filter: blur(40px)`, `aria-hidden`.

### 3.2 Row 1 — site navigation (website layer, outside the frame)
- Only the menu button and the logo. Nothing from the camera UI.
- Menu button 44×44 at `left: 24px; top: 16px`, blue-glow button, 3-line icon, `aria-label="Open menu"` (links to `#` for now).
- Logo `<h1>` **centred on the viewport** (`left: 50%; transform: translateX(-50%)`), independent of the menu button, vertically aligned with it, links to `/`.
- Divider under the row: `1px solid rgba(245,245,245,.12)`, top 72px, from `left: 24px` to `right: 24px`.
- **Hero line** (real text, not aria-hidden), between the divider and the frame: *"Daniel is editing alone, late at night. Someone is watching."* — Inter 700, line-height 1.1, `#F5F5F5`, left-aligned, `white-space: nowrap`, `text-shadow: 0 0 20px rgba(3,3,3,.95)`.
  - Container: left/right 64px (1312px wide) — slightly wider than the frame; it does not need to align with the frame edges.
  - Top 112px (≈40px below the divider), ≈32px above the frame.
  - **Size fits the width:** `fitText()` in `main.js` measures the text and sets `font-size` so the single line fills the container exactly (≈41px at 1440 × 900). Recalculated with `ResizeObserver` and after `document.fonts.ready`. CSS fallback: `font-size: clamp(28px, 3.2vw, 56px)`.

### 3.3 Camera info strip and tags (camera layer, inside the frame, `aria-hidden`)
- **Info strip:** inside the frame, 40–100px from its top edge, horizontally between the top corner marks (left/right 112px). **3-column grid `1fr auto 1fr`** (column-gap 56px) so the timecode is exactly centred: left column right-aligned `24 FPS` · centre **timecode** (min-width 300px) · right column `SHUTTER 180.0°` and `3200K` (56px apart).
  - `24 FPS` / `SHUTTER` / `3200K`: JetBrains Mono 14px, letter-spacing .12em, `#AFC0E6`.
  - Timecode: Archivo 87%, 600, 40px; colours per mode (§4).
- **Tag column:** 40px from the frame's left edge, width 68px, centred text, vertically centred in the frame (between the left corner marks), gap 10px. Top → bottom:
  1. `CAM` (17px, 500) above a blue tag `LOG` (6px gap), then +8px
  2. blue tag `6K` (20px)
  3. blue tag `17:9` (20px)
  4. +8px, blue tag `A` (20px, full width) above `18 min` (17px, 500)

Nothing outside the frame on the left or right.

### 3.4 Video frame
- `left: 80px; top: 190px; 1280 × 614` (centred; ≈2.08:1, **never wider than 2.1:1**; bottom at 804px, above the scroll arrow), radius 4px, `overflow: hidden`, bg `#02040A`, `box-shadow: 0 0 90px -16px rgba(10,67,255,.6)`.
- Media: the hero uses **`static/video/hero.mp4`**: `<video muted loop playsinline preload="metadata" poster="img/hero-poster-placeholder.png">` (both via `url_for`), `object-fit: cover; object-position: 50% 62%`. No sound. Playback is controlled by JS (§4); no `autoplay` attribute.
- If the video fails to load or autoplay is blocked, the poster image is shown and the timecode and controls keep working.
- Filter: REC / PLAY → `none`; STOP → `brightness(.7) saturate(.7)` (400ms transition).
- Overlay: `linear-gradient(180deg, rgba(2,4,10,.65) 0%, transparent 42%, transparent 58%, rgba(2,4,10,.88) 100%)`.
- **Four corner marks** 56×56, inset 40px.
- **Hero line** — now in the website layer, see §3.2.
- **Controls** (`role="group" aria-label="Camera controls"`), centred, inside the bottom corner marks: row bottom **44px above the frame's bottom edge**, height 72px, three buttons 56×56, gap 16px:
  - **REC**: red dot 24×24 `#FF2B2B` with glow, `aria-label="Record"`
  - **PLAY**: white play triangle 22px, `aria-label="Play back your footage"`
  - **STOP**: white square 18×18 radius 3px, `aria-label="Stop"`
  - All: circle, `background: rgba(3,3,3,.55)`, `border: 2px solid rgba(245,245,245,.55)` when inactive.
  - Active: REC `border-color: #FF2B2B; box-shadow: 0 0 28px -2px rgba(255,43,43,.85)` · PLAY `#0A43FF; 0 0 28px -2px rgba(10,67,255,.9)` · STOP `#F5F5F5; 0 0 22px -4px rgba(245,245,245,.6)`. Use `aria-pressed`.

### 3.5 Scroll arrow
- Centred under the frame: `top: 808px`, 48 × 88 hit area, arrow SVG 32 × 80 (`M16 4v70M5 62l11 12 11-12`), stroke `#F5F5F5` 2.2px, round caps, `filter: drop-shadow(0 0 8px rgba(10,67,255,.9))`.
- It is a real link: `<a href="#curious" aria-label="Scroll down to discover more">`, smooth-scrolls to the next section.
- Gentle bob animation (translateY 0 → 6px, 1.8s ease-in-out, infinite) — **off** under `prefers-reduced-motion`.

---

## 4. Hero behaviour — REC / PLAY / STOP

State lives in `static/js/main.js`; set `data-mode="rec|play|stop"` on the hero and let CSS do the visuals.

| | **REC** (default on load) | **STOP** | **PLAY** |
|---|---|---|---|
| Media | playing (muted, loop) | paused on current frame, dimmed | plays back from the start of the recorded footage |
| Timecode | counts up from the stored total, 24 fps, `#FF2B2B` + `text-shadow: 0 0 18px rgba(255,43,43,.6)` | holds its value, `#F5F5F5`, no glow | counts from `00:00:00:00` up to the recorded total, `#8FB0FF` + `0 0 18px rgba(10,67,255,.7)` |
| Active button | REC | STOP | PLAY |

Rules:
- **On load the page starts in REC** and the timecode starts at `00:00:00:00` — as if recording began the moment the user arrived.
- **STOP** pauses; it never resets the timecode.
- **REC** after STOP continues counting from the held value.
- **PLAY** is only available when recorded time > 0. When playback reaches the recorded total it switches to **STOP** automatically (timecode shows the recorded total again).
- Pressing REC during PLAY ends playback and resumes recording from the recorded total.
- Timecode format `HH:MM:SS:FF` (FF 00–23). Compute from real elapsed time (`performance.now()` + `requestAnimationFrame`), never by counting interval ticks.
- Persist the recorded total in **sessionStorage** (try/catch) so a reload in the same tab continues; a new visit starts at 00:00:00:00.
- `Escape` = STOP.
- **No sound.** The video is always muted.
- `prefers-reduced-motion: reduce` → the page loads in **STOP** (nothing moves until the user presses REC or PLAY).

---

## 5. Scroll section — "Curious to see who is watching him?"

Directly below the hero (the page now scrolls).

- `<section id="curious" aria-labelledby="curious-title">`, `min-height: 640px` (or ~80vh), content centred horizontally and vertically, padding 120px 24px, background `radial-gradient(55% 55% at 50% 50%, rgba(28,28,160,.3) 0%, rgba(7,32,68,.15) 45%, transparent 75%)` on `#030303`.
- `<h2 id="curious-title">` **"Curious to see who is watching him?"** — Archivo 62% 800, `clamp(48px, 7vw, 104px)`, line-height .95, `#F5F5F5`, `max-width: 1000px` (wraps to two balanced lines; `text-wrap: balance`).
- **WATCH THE FILM** link-button, 44px below: `min-height: 56px; padding: 0 28px; border-radius: 12px; border: 1px solid rgba(10,67,255,.7); background: radial-gradient(120% 120% at 50% 50%, rgba(10,67,255,.3) 0%, rgba(7,32,68,.75) 60%, #04070F 100%); box-shadow: 0 0 34px -4px rgba(10,67,255,.8), inset 0 0 12px rgba(10,67,255,.3);` JetBrains Mono 13px, .2em, white play icon 16px + 12px gap. Label and `href` come from `app.py` (see §1). Hover/focus: stronger glow; visible focus ring.
- **Reveal animation:** when the section enters the viewport (IntersectionObserver, threshold ~0.3), the heading fades in and rises (opacity 0 → 1, `translateY(24px)` → 0, 600ms ease-out), then the button 120ms later. Run once. Under `prefers-reduced-motion` show both immediately, no animation.
- Followed by the **Film** section (§6), the Journal link (§12) and the footer (§10).

---

## 6. Film section — synopsis & trailer

Directly below the "Curious" section.

- `<section id="film" aria-labelledby="film-title">`, `border-top: 1px solid rgba(176,176,176,.14)`, background `#030303`. Inner container `max-width: 1312px`, centred, padding `96px 24px`.
- **Section label** style (reused): JetBrains Mono 11px, letter-spacing .18em, `#8E96A6`.

### 6.1 Synopsis
Two columns: `display: flex; flex-wrap: wrap; gap: 48px 64px`, each column `flex: 1 1 420px` (stacks on mobile).
- **Left:** label `01 · THE FILM`; `<h2 id="film-title">` *"A 10-minute psychological thriller set in a single edit suite."* — Archivo 62% 800, `clamp(40px, 5vw, 64px)`, line-height .95, `#F5F5F5`, 16px under the label.
- **Right:**
  - Paragraph, Inter 300 19px, line-height 1.6, `#D6D6D6`: *"Late at night, alone in his edit suite, exhausted filmmaker Daniel finds clips on his timeline that he never shot: footage of his own room, ten minutes in the future. Every clip plays out exactly as recorded. The harder he tries to break the sequence, the deeper he falls into a time loop of his own making."*
  - Fact list `<dl>`, 2-column grid, 32px under the paragraph, `border-top` on the grid; each item `padding: 14px 0`, `border-bottom: 1px solid rgba(176,176,176,.14)`. `<dt>` JetBrains Mono 11px .14em `#8E96A6`; `<dd>` Inter 15px `#F5F5F5`.
    GENRE — Psychological / Supernatural Thriller · RUNTIME — 10 minutes · WRITTEN BY — Shae Rozar · COUNTRY · YEAR — United Kingdom · 2026
  - Link **READ THE FULL SYNOPSIS →** to `/synopsis`: JetBrains Mono 12px .14em, `border-bottom: 1px solid rgba(245,245,245,.4)`, min-height 44px. `/synopsis` is a placeholder Flask page for now.

### 6.2 Trailer
64px below the synopsis.
- Label `02 · TRAILER`.
- **16:9 frame**, full container width, radius 4px, `overflow: hidden`, bg `#02040A`, `box-shadow: 0 0 90px -16px rgba(10,67,255,.6)`. No corner marks.
- Poster `static/img/hero-poster-placeholder.png`, `object-fit: cover`, `filter: brightness(.6) saturate(.7)`.
- Centred **play button** 88 × 88 circle, blue-glow style (`border: 1px solid rgba(10,67,255,.6)`, radial gradient, `box-shadow: 0 0 34px -4px rgba(10,67,255,.8)`), white play icon 30px, `aria-label="Play the trailer"`.
- **Facade / lite-embed:** nothing loads on page load. `TRAILER_URL` is set in `app.py` (empty for now):
  - YouTube / Vimeo link → clicking play swaps the poster for the iframe (`youtube-nocookie.com` / `player.vimeo.com`, `autoplay=1`); `.mp4` → `<video controls autoplay playsinline>`. Focus moves to the player. The trailer may play with sound (the visitor starts it).
  - Empty → button disabled, **TRAILER COMING SOON** under it (JetBrains Mono 12px, .2em, `#B0B0B0`).

### 6.3 Motion
Same reveal as §5 (IntersectionObserver, threshold 0.3, opacity 0 → 1 + `translateY(24px)` → 0, 600ms ease-out, once) for the left column, the right column (+120ms) and the trailer frame. Off under `prefers-reduced-motion`.

### 6.4 Structured data
JSON-LD `Movie` in `<head>`: name, genre, `duration: PT10M`, `countryOfOrigin: GB`, `dateCreated: 2026`, author/creator Shae Rozar, description = synopsis, image = poster. A `trailer` `VideoObject` is added only when `TRAILER_URL` is set (`uploadDate` from `TRAILER_UPLOAD_DATE` when given).

---

## 7. Accessibility
- Real `<button>`s with `aria-pressed`; visible focus ring (2px `#0A43FF` outline, 4px offset) on all controls, the arrow and the CTA.
- Monitor values, tags, corner marks, glows → `aria-hidden="true"`. The hero line, the heading and the CTA are real, readable content.
- Touch targets ≥ 44px. Contrast ≥ 4.5:1.
- STOP is the pause control for the auto-playing video (WCAG 2.2.2).

## 8. SEO (head)
- `<title>Playback — A 10-Minute Psychological Thriller Short Film</title>`
- `<meta name="description" content="Playback is a 10-minute psychological thriller short film. Daniel is editing alone, late at night — but someone is watching.">`
- viewport, Open Graph (`og:type=video.movie`, `og:image` = poster), Twitter card, `preconnect` to Google Fonts.

## 9. Responsive
- **< 1024px:** hide the tag column and `SHUTTER` / `3200K`; frame keeps the desktop proportions (1280 × 614 reference).
- **Mobile (reference 390 × 844):**
  - Row 1: menu button (left 12px) + logo 34px centred, divider underneath (top 64px, 12px from each side).
  - Hero line Inter 700 `clamp(22px, 6vw, 28px)`, line-height 1.1, may wrap to two lines, left/right 12px (frame edges), top 88px (≈24px below the divider, ≈20px above the frame). `fitText` is off.
  - Frame 366 × ~548 at top 160px (bottom stays above the scroll arrow), video / poster `object-position: 68% 50%`, corner marks 36 × 36 inset 18px.
  - Inside the frame, top: **timecode** centred (24px) between the top corner marks; under it a row with `6K` `17:9` on the left and `CAM` + `LOG` on the right. `24 FPS`, `SHUTTER`, `3200K` hidden.
  - Controls inside the bottom corner marks: three 48px buttons (gap 10px) on the left, `A 18 min` on the right.
  - Scroll arrow centred under the frame (~64px tall).
  - "Curious…" heading uses the clamp minimum (48px); CTA full-width up to 320px.

---

## 10. Base layout (all pages)

- `templates/base.html` holds `<head>`, the nav row, the footer and the menu overlay; every page uses `{% extends "base.html" %}`.
- **Head blocks:** `title`, `description`, `og_type`, `robots`, `structured_data`. Open Graph / Twitter titles and descriptions reuse the page's own title and description. `<link rel="canonical">` = the page URL without query string.
- **Nav row** (`_nav.html`): same as §3.2 — menu button left 24 / top 16, logo centred on the viewport, divider at 72px.
  - Homepage: rendered inside the hero stage (scales with the hero); the logo is the page's `<h1>`.
  - Inner pages: rendered in a 76px header (64px on mobile) in plain px; the logo is a plain link (each page has its own `<h1>`).
- **Footer:** `border-top: 1px solid rgba(176,176,176,.16)`, inner container 1312px, padding 24px.
  - Left: `© 2026 PLAYBACK · DESIGNED & DEVELOPED BY STUDIO MU` — JetBrains Mono 11px, .12em, `#B0B0B0`.
  - Right: Instagram, TikTok and IMDb icon links, 44 × 44, `aria-label`s, `href="#"` for now; hover = blue drop-shadow.
  - Stacks (left-aligned) on mobile.

## 11. Menu overlay

- The menu button is a `<button aria-expanded aria-controls="site-menu">`. The overlay is `role="dialog" aria-modal="true"`, full screen, background `#030303`.
- Its top row repeats the nav row: a **Close (X)** button in the hamburger's spot, logo centred, divider.
- **Nav list** at left 96px, ≈150px from the top; 1px divider `rgba(176,176,176,.12)` between items. Each item: index in JetBrains Mono 11px .14em `#8E96A6` + label in Archivo 62% 800, 88px, line-height 1 (`clamp(48px, 12vw, 88px)`, left 24px on mobile):
  `00 · Home` `/` · `01 · Synopsis` /synopsis · `02 · Journal` /journal · `03 · Press Kit` /epk · `04 · Contact` /contact
- **Current page:** `aria-current="page"` (journal entries mark Journal with `aria-current="true"`), label `#8E96A6`.
- **Hover / focus:** label `#FFFFFF` + `text-shadow: 0 0 28px rgba(10,67,255,.85)`; index turns `#FF2B2B` with a small red dot.
- **Behaviour:** focus moves to Close and is trapped in the overlay; `Escape` closes it (and does not STOP the hero camera); focus returns to the menu button; page scroll is locked while open. 200ms fade, none under `prefers-reduced-motion`.
- `/synopsis` is a placeholder page for now; `/epk` is the Press Kit (§15), `/contact` the Contact page (§17).

## 12. Homepage — Journal link

After the Film section: `<section class="more">`, padding 96px 24px, centred, `border-top: 1px solid rgba(176,176,176,.14)`.
- *"Curious to know more?"* — Archivo 62% 800, `clamp(32px, 4vw, 48px)`.
- **EXPLORE THE JOURNAL** + long right arrow (24px gap), JetBrains Mono 13px .2em, `border-bottom: 1px solid rgba(245,245,245,.4)`, `href="/journal"`. Hover/focus: blue border and blue glow.
- Same reveal as §5 (link 120ms after the heading).

## 13. Journal index — `/journal`

- **Data:** `JOURNAL_ENTRIES` in `app.py` (slug, day, date ISO, title, excerpt, cover_label, body). Only `get_journal_entries()` / `get_journal_entry(slug)` read it, so they can be swapped for database queries. Dates display as `3 NOV 2026`.
- Page container: `max-width: 1312px`, padding 96px 24px (64px on mobile).
- **Intro** (two columns, `flex: 1 1 420px`, gap 48px 64px, stacks on mobile):
  - Left: label `02 · JOURNAL`; `<h1>` *"Hi, I'm [Director name]."* (Archivo 62% 800, `clamp(40px, 5vw, 64px)`); intro paragraph (Inter 300 19px, line-height 1.6, `#D6D6D6`).
  - Right: 4:3 glow-card placeholder `[ ON-SET SELFIE ]` in a `<figure>` with `<figcaption>`.
- **Glow card** (shared): `border-radius: 16px; padding: 24px; border: 1px solid rgba(10,67,255,.45); background: radial-gradient(120% 100% at 50% 0%, rgba(10,67,255,.22) 0%, rgba(7,32,68,.5) 45%, #04070F 100%); box-shadow: 0 0 60px -14px rgba(10,67,255,.6), inset 0 0 30px rgba(10,67,255,.14);`
- **Entries grid**, 64px below: `repeat(auto-fit, minmax(300px, 1fr))`, gap 24px. Each card is one `<a>` to `/journal/<slug>`:
  - top row `DAY 01` + date (JetBrains Mono 11px .14em `#B0B0B0`);
  - thumbnail placeholder 16:10, radius 10px, `border: 1px solid rgba(10,67,255,.3)`, bg `#02040A`, mono label;
  - title Archivo 62% 800 32px; excerpt Inter 15px `#B0B0B0`; arrow icon bottom right.
  - Hover/focus: border `rgba(10,67,255,.8)`, stronger glow, `translateY(-4px)`, 250ms (no movement under reduced motion).
- Reveal: intro block and each card.

## 14. Journal entry — `/journal/<slug>` (404 if not found)

Container `max-width: 1312px`, padding 96px 24px; blocks 80px apart (56px on mobile); every block reveals on scroll; all columns stack on mobile.
- **a) Header:** `← ALL ENTRIES` (JetBrains Mono 12px) · `DAY 01 · 3 NOV 2026` (mono 11px `#8E96A6`) · title `<h1>` (Archivo 62% 800, `clamp(48px, 6vw, 88px)`).
- **b) Pull quote:** Archivo 62% 700, `clamp(28px, 3vw, 40px)`, 2px `#0A43FF` left accent with a blue glow; then two paragraphs.
- **Body text:** Inter 300 18px, line-height 1.7, `#D6D6D6`, max 72ch.
- **c)** Two columns: long text left, 4:3 glow-card image placeholder right.
- **d)** Full-width paragraph.
- **e)** Two 3:4 portrait placeholders side by side (left), text (right).
- **f)** Full-width paragraph.
- **g) Closing row:** *"Curious about anything else?"* (Archivo 62% 800 36px) + long arrow + **GET IN TOUCH** → `/contact`.
- **h) Prev / next** entry links, JetBrains Mono 12px, top border.
- Image placeholders: glow-card `<figure>` + `<figcaption>`, mono label, ready for `<img alt="">`.
- **SEO:** title `"<entry title> · Playback Journal"`, description = excerpt, `og:type=article`, JSON-LD `BlogPosting` (headline, datePublished, author `[Director name]`, image, `isPartOf` the Playback `Movie`).

## 15. Press Kit page — `/epk`

**Audience:** press, festival programmers, producers — facts and downloads fast. Clean and scannable; motion is only the one-time reveal per section (none under `prefers-reduced-motion`).

**Single source of truth:** the `FILM` dict in `app.py` (title, genre, runtime, year, country, language, logline, short/long synopsis, director bio and statement, cast, crew, tech specs, press email, stills, posters, press-kit ZIP). The homepage Film section, the homepage title/description and every Movie JSON-LD read from it. Unwritten copy uses `[bracketed placeholders]`; bio and statement are lorem ipsum. The long synopsis must never reveal the ending.

**Layout:** container 1312px, padding 96px 24px. Each section: `border-top: 1px solid rgba(176,176,176,.14)`, padding 48px 0, grid `1fr 3fr` (stacked on mobile) with the `<h2>` styled as the label (JetBrains Mono 11px .18em `#8E96A6`) on the left.
- **a) Header:** label `03 · PRESS KIT`, `<h1>` "Press Kit" (Archivo 62% 800, `clamp(48px, 6vw, 88px)`); **DOWNLOAD FULL PRESS KIT (.ZIP)** (blue-glow button as §5, download icon, min-height 56px, radius 12px) + **PRESS CONTACT** (mailto, outline: `1px solid rgba(245,245,245,.4)`, radius 12px, blue glow on hover).
- **b) Key facts:** `<dl>` rows (dt mono 11px `#8E96A6` / dd Inter 15px, `padding: 14px 0`, divider lines): Title, Genre, Runtime, Year, Country, Language; then the logline, Inter 300 22px.
- **c) Synopsis:** short synopsis, then the long synopsis.
- **d) Cast & Crew:** two lists (Cast / Crew, small mono `<h3>`), same rows. Cast: Daniel → `[Actor name]`. Crew: Director, Writer (Shae Rozar), Producer, Director of Photography, Editor, Sound Designer.
- **e) Director:** 1:1 glow-card portrait `[ DIRECTOR PORTRAIT ]`, bio, then **Director's Statement** with the 2px `#0A43FF` left accent (as §14 b), Inter 300 19px.
- **f) Stills gallery:** 16:9 viewer (blue border + glow, four corner marks 56 × 56 inset 40px; 36/18 on mobile); prev/next buttons 44 × 44 blue-glow with `aria-label`s; caption `Still 01 / 06` (`aria-live="polite"`) + **DOWNLOAD THIS STILL (JPG)**; a row of thumbnail `<button>`s (6 across, 3 on mobile) with `aria-current="true"` on the active one. Left/Right arrow keys work while focus is inside the gallery. All images have alt text; everything except the first viewer image is `loading="lazy"`.
- **g) Posters:** two 2:3 glow cards (`[ POSTER — PORTRAIT ]`, `[ POSTER — LANDSCAPE / KEY ART ]`, max 320px wide), each with **DOWNLOAD POSTER (JPG)**.
- **h) Technical specs:** `<dl>` rows — Runtime, Aspect ratio, Shooting format, Sound, Language, Subtitles, Country, Year (`[TBC]` when unknown).
- **i) Press contact:** the email as a big link (Archivo 62% 800, `clamp(28px, 3vw, 40px)`), "Screeners available on request for festivals and press.", and the ZIP button again.

**Downloads:** files live in `static/presskit/` (placeholders for now). Every download goes through the `download_link()` macro (`_downloads.html`) and the route `/epk/download/<key>` (`PRESSKIT_DOWNLOADS` in `app.py`): HTML `download` attribute, and the file type + size shown next to the link (e.g. `JPG · 158 KB`, read from disk). The ZIP is flagged `gated` — a request form (name, outlet, email) can later be added in that route/macro without touching the layout. Not built yet.

**SEO:** `<title>Press Kit · Playback (2026) — Psychological Thriller Short Film</title>`, meta description, canonical, Open Graph image = poster, Movie JSON-LD from `FILM`. One `<h1>`, one `<h2>` per section, tables as `<dl>`, visible focus rings.

## 16. External links

**Where to change them:** the `EXTERNAL_LINKS` dict at the top of `app.py` — the only place. A context processor makes it available in every template (footer, homepage, any page).

| Key | Drives |
|---|---|
| `film_vimeo` | **WATCH THE FILM** button (§5) + Movie JSON-LD `url` |
| `instagram` | Instagram icon + JSON-LD `sameAs` |
| `tiktok` | TikTok icon + JSON-LD `sameAs` |
| `imdb` | IMDb icon + JSON-LD `sameAs` |

- **Placeholder rule** (`is_live_link()`): a value that is empty or still contains `[` (e.g. `https://vimeo.com/[FILM-ID]`) counts as *not set*:
  - Film button → disabled (`role="link" aria-disabled="true"`, no `href`, opacity .5, no glow), label **FILM COMING SOON**.
  - Social icon → not rendered (no `href="#"`); the whole list is skipped if none are set.
  - JSON-LD → that URL is left out.
- **When set:** links open in a new tab (`target="_blank" rel="noopener noreferrer"`). The film button gets visually hidden "(opens in a new tab)" text (no visible external-link icon); icon links get `aria-label="Playback on Instagram (opens in a new tab)"` etc. 44 × 44 hit area and hover/focus glow unchanged.
- Social icons come from `templates/_social.html` (`{% include "_social.html" %}`). They appear in the footer, in the menu overlay (bottom-left, under the nav list) and in the Contact page's FOLLOW row (`social_variant="glow"`: 44 × 44 blue-glow buttons; the footer and menu keep the plain style).

### SHOW_PLACEHOLDER_LINKS (development preview)
- Setting in `app.py`. Default `None` = follow `app.debug`: **on** with `python app.py` / `flask run --debug`, **off** in production. Set `True` / `False` to force it. (Read per request, because `app.debug` is only set when the server starts.)
- **On:** the film button and every social icon render with their normal enabled styles and glow. A link that is still a placeholder points to the platform's homepage instead (`https://vimeo.com`, `https://www.instagram.com`, `https://www.tiktok.com`, `https://www.imdb.com`), still `target="_blank" rel="noopener noreferrer"`, and gets `data-placeholder="true"`. `<body data-placeholder-links="…">` lists the unset keys and `main.js` logs **one** `console.warn` naming them.
- **Off:** the placeholder rule above applies (icon hidden, **FILM COMING SOON** disabled button).
- `link_for(key)` in `app.py` makes this decision for every template. **JSON-LD never uses it**: placeholder or fallback URLs are never written into `url` / `sameAs`, in any mode.

## 17. Contact page — `/contact`

Extends `base.html`. JSON-LD `ContactPage`; `<title>Contact · Playback — Short Film</title>`, meta description, canonical. One `<h1>`.

**Background:** `#030303` + a decorative glow (`aria-hidden`): ellipse 1100 × 700, centred, top 220px, `radial-gradient(closest-side, rgba(28,28,160,.35), rgba(7,32,68,.2) 55%, transparent)`, `blur(50px)` (clipped horizontally so phones don't scroll sideways).
**Container:** max-width 1312px, padding `88px 24px 112px`.

- **Header:** label `04 · CONTACT`; `<h1>` *"Want to know more about Playback?"* — Archivo 62% 800, `clamp(44px, 5.5vw, 80px)`, line-height .95, max-width 900px, 16px under the label; subline 20px below — Inter 300 19px, line-height 1.6, `#D6D6D6`, max 60ch.
- **Columns** 56px below: `flex-wrap`, gap 48px 64px, `align-items: flex-start`. Form `flex: 3 1 560px`, contacts `flex: 2 1 320px`. Stacked on mobile, form first.

### 17.1 Form card
- Glow card: padding 40px (24px on mobile), radius 16px, `border: 1px solid rgba(10,67,255,.45)`, `radial-gradient(120% 100% at 50% 0%, rgba(10,67,255,.18) 0%, rgba(7,32,68,.5) 45%, #04070F 100%)`, `box-shadow: 0 0 60px -14px rgba(10,67,255,.6), inset 0 0 30px rgba(10,67,255,.14)`.
- **No corner marks on this card.** Corner marks are only for camera frames (hero, stills viewer).
- `<form method="post" action="/contact" novalidate>`, 24px gaps:
  - **Topic** — `<fieldset>` + `<legend>` "What's it about?" (Inter 500 14px). Four radio chips (real `<input type="radio" name="topic">`, visually hidden, inside a `<label>`): FESTIVAL · PRESS · DISTRIBUTION · JUST SAYING HI. **Nothing pre-selected; required.**
    Chip: min-height 44px, padding 0 18px, radius 22px, JetBrains Mono 12px .14em, `#F5F5F5`, gap 10px, wraps.
    | State | Style |
    |---|---|
    | default | `border: 1px solid rgba(245,245,245,.25)`, transparent, no glow |
    | hover | border `#0A43FF`, bg `rgba(10,67,255,.12)`, `box-shadow: 0 0 16px -4px rgba(10,67,255,.7)` |
    | checked | border `#0A43FF`, bg `rgba(10,67,255,.18)`, `box-shadow: 0 0 20px -4px rgba(10,67,255,.8)` |
    | keyboard focus | `outline: 2px solid #0A43FF; outline-offset: 3px` (`:focus-visible` on the radio) |
    Transitions 200ms, none under reduced motion.
  - **Name + Email side by side** (grid, 2 columns, gap 24px; stacked on mobile). Real `<label>`s above (Inter 500 14px, 8px gap), `autocomplete="name"` / `"email"`, required.
  - **Your message** — textarea, 6 rows, `resize: vertical`, required.
  - **Consent** checkbox (20 × 20, `accent-color: #0A43FF`): "I agree that Playback can store my message to reply to me." + **Privacy** link → `/privacy` (placeholder). Required.
  - Hidden honeypot `name="website"` and a CSRF token field.
  - **SEND MESSAGE** — 10px red dot (`#FF2B2B`, glow) before the label; blue-glow (min-height 56px, padding 0 32px, radius 12px, `border: 1px solid rgba(10,67,255,.7)`, radial gradient, `box-shadow: 0 0 34px -4px rgba(10,67,255,.8)`), JetBrains Mono 13px .2em, left-aligned; full width on mobile.
- **Inputs:** min-height 52px, padding 0 16px (textarea 14px 16px), radius 8px, `border: 1px solid rgba(245,245,245,.18)`, bg `#02040A`, Inter 16px `#F5F5F5`. Focus: border `#0A43FF` + `0 0 0 3px rgba(10,67,255,.35)`.

### 17.2 Validation & states (`static/js/contact.js`, only on this page)
- Rules (same in `validate_contact()` in `app.py`): topic one of the four; name required ≤ 100; email required, valid, ≤ 254; message required ≤ 5000; consent ticked.
- Validate on blur and submit. Inline errors under each field in `#FF6B6B` with `aria-describedby` + `aria-invalid` (topic error under the chips, on the fieldset); focus the first invalid field. No `alert()`.
- Sending: button disabled, label **RECORDING…**. Sent with `fetch` (`Accept: application/json`).
- **Success:** the form is replaced by a centred panel in the same card (min-height 480px, `role="status"`): red dot + timecode `00:00:03:12` (Archivo 87% 600 32px, `#FF2B2B`, red glow, tabular numbers) · `<h2>` "Message recorded." (Archivo 62% 800 56px, 44px on mobile) · "Thanks — we'll get back to you soon." (Inter 300 18px `#D6D6D6`) · **SEND ANOTHER MESSAGE** text button (resets the form).
- **Error** (network / server / expired session): the form stays and a message appears above the button.
- **Without JS:** a normal POST renders the same page with inline errors (values kept) or the success panel.

### 17.3 Backend
- `POST /contact`: CSRF check (session token, `SECRET_KEY` from the environment — **set it in production**), honeypot silently ignored (shows success, stores nothing), server-side validation, then the success state. JSON for `fetch`, HTML otherwise.
- `save_contact_message(data)` only logs for now — TODO: database (topic, name, email, message, consent, created_at).

### 17.4 Direct contacts (right column)
Rows with padding 24px 0 and `border-bottom: 1px solid rgba(176,176,176,.14)` (first row no top padding):
- **DIRECTOR** → `director@[domain]` (mailto, `FILM["director_email"]`)
- **PRESS** → `press@[domain]` (mailto, `FILM["press_email"]`)
- **PRESS KIT** → **VIEW THE PRESS KIT** + long arrow → `/epk` (mono 13px .14em, `border-bottom: 1px solid rgba(245,245,245,.4)`, min-height 44px)
- **FOLLOW** (no divider) → social icons as 44 × 44 blue-glow buttons (radius 10px, `border: 1px solid rgba(10,67,255,.6)`, radial gradient, `box-shadow: 0 0 18px -4px rgba(10,67,255,.7)`), gap 8px — `_social.html` with `social_variant="glow"`, `EXTERNAL_LINKS` + `SHOW_PLACEHOLDER_LINKS` (§16).
- Labels JetBrains Mono 11px .18em `#8E96A6`; emails Archivo 62% 800 34px, line-height 1.1, no underline, 10px under the label.
- No "screeners available on request" note here (that lives on the Press Kit page).
