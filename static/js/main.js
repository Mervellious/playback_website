/* PLAYBACK — landing page
   Hero: hidden camera. JS only switches data-state (stby | live | end) on
   .hero-frame; CSS does the rest.
   Scroll section: one-time reveal when it enters the viewport. */

// The hero plays only the LAST HERO_CLIP_SECONDS of static/video/hero.mp4
// (the file itself is not trimmed yet).
const HERO_CLIP_SECONDS = 6;
// Length of the simulated clip used while static/video/hero.mp4 can't be played.
const CLIP_FALLBACK_SECONDS = 6;

document.documentElement.classList.add("js");

(() => {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ==========================================================================
  // Hero — hidden camera: STBY (paused, monochrome) → LIVE (watching) → END
  // ==========================================================================
  function initHiddenCamera() {
    const FPS = 24;
    const STATUS = { stby: "STBY", live: "REC", end: "NO SIGNAL" };

    const frame = document.querySelector(".hero-frame");
    if (!frame) return;
    const video = frame.querySelector(".hero-video");
    const source = video && video.querySelector("source");
    const watch = frame.querySelector(".hero-watch");
    const endPanel = frame.querySelector(".hero-end");
    const replay = frame.querySelector(".hero-replay");
    const statusText = frame.querySelector(".status-text");
    const timecode = frame.querySelector(".hero-label--tc");
    const announcer = document.getElementById("hero-status");
    if (!video || !watch || !endPanel || !replay || !statusText || !timecode) return;

    // Never autoplays, never loops, no sound.
    video.muted = true;
    video.defaultMuted = true;
    video.loop = false;
    video.autoplay = false;

    const canHover = () => window.matchMedia("(hover: hover)").matches;

    let state = "stby";
    let hovering = false;
    let ignoreFocus = false; // REPLAY moves focus back without starting playback
    let rafId = 0;
    let lastFrame = -1;

    // ---------- Fallback: no playable video → simulated clip on the poster ----------
    let fallback = false;
    let simTime = 0; // seconds watched (only advances while LIVE)
    let simLast = 0; // timestamp of the previous tick

    function useFallback() {
      if (fallback) return;
      fallback = true;
      simTime = 0;
      simLast = performance.now();
    }

    if (!source || video.error || video.networkState === HTMLMediaElement.NETWORK_NO_SOURCE) useFallback();
    video.addEventListener("error", useFallback);
    if (source) source.addEventListener("error", useFallback); // a missing file errors on <source>

    // ---------- Clip window: the last HERO_CLIP_SECONDS of the file ----------
    let clipStart = 0; // set once the duration is known

    function toClipStart() {
      try {
        video.currentTime = clipStart;
      } catch {
        /* metadata not loaded yet: loadedmetadata seeks */
      }
    }

    function onMetadata() {
      if (!Number.isFinite(video.duration)) return;
      clipStart = Math.max(0, video.duration - HERO_CLIP_SECONDS);
      if (video.currentTime < clipStart) toClipStart();
    }

    if (video.readyState >= HTMLMediaElement.HAVE_METADATA) onMetadata();
    video.addEventListener("loadedmetadata", onMetadata);

    const clipTime = () => (fallback ? simTime : Math.max(0, (video.currentTime || 0) - clipStart));

    // ---------- Timecode: HH:MM:SS:FF from the clip time ----------
    const pad = (n) => String(n).padStart(2, "0");

    function render(seconds) {
      const totalFrames = Math.max(0, Math.floor(seconds * FPS));
      if (totalFrames === lastFrame) return;
      lastFrame = totalFrames;
      const totalSeconds = Math.floor(totalFrames / FPS);
      timecode.textContent = [
        Math.floor(totalSeconds / 3600) % 100,
        Math.floor(totalSeconds / 60) % 60,
        totalSeconds % 60,
        totalFrames % FPS,
      ].map(pad).join(":");
    }

    function tick(now) {
      if (state !== "live") return;
      if (fallback) {
        simTime += Math.max(0, now - simLast) / 1000;
        simLast = now;
        if (simTime >= CLIP_FALLBACK_SECONDS) {
          simTime = CLIP_FALLBACK_SECONDS;
          setState("end");
          return;
        }
      }
      render(clipTime());
      rafId = requestAnimationFrame(tick);
    }

    // ---------- States ----------
    function setState(next) {
      if (next === state) return;
      state = next;
      frame.dataset.state = next;
      statusText.textContent = STATUS[next];
      endPanel.hidden = next !== "end";
      cancelAnimationFrame(rafId);

      if (next === "live") {
        if (!fallback) {
          if (video.currentTime < clipStart) toClipStart();
          const playing = video.play();
          if (playing) playing.catch(() => {});
        }
        simLast = performance.now();
        rafId = requestAnimationFrame(tick);
      } else {
        video.pause(); // keeps currentTime, so LIVE resumes where it stopped
        render(clipTime());
      }

      if (announcer) {
        announcer.textContent = next === "end" ? "Clip ended. Curious to see who is watching him?" : "";
      }
    }

    // Pointer devices: hover to watch.
    frame.addEventListener("mouseenter", () => {
      hovering = true;
      if (canHover() && state === "stby") setState("live");
    });
    frame.addEventListener("mouseleave", () => {
      hovering = false;
      if (canHover() && state === "live") setState("stby");
    });

    // Keyboard: focus to watch, blur to stop.
    watch.addEventListener("focus", () => {
      if (!ignoreFocus && canHover() && state === "stby") setState("live");
    });
    watch.addEventListener("blur", () => {
      if (canHover() && state === "live" && !hovering) setState("stby");
    });

    // Touch: tap toggles. Pointer/keyboard: Enter or a click starts watching.
    watch.addEventListener("click", () => {
      if (!canHover()) setState(state === "live" ? "stby" : "live");
      else if (state === "stby") setState("live");
    });

    video.addEventListener("ended", () => {
      if (state === "live") setState("end");
    });

    // Scrolled out of view while watching → back to STBY.
    if ("IntersectionObserver" in window) {
      new IntersectionObserver((entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting && state === "live") setState("stby");
        }
      }).observe(frame);
    }

    replay.addEventListener("click", () => {
      toClipStart();
      simTime = 0;
      setState("stby");
      lastFrame = -1;
      render(0); // 00:00:00:00
      ignoreFocus = true;
      watch.focus();
      ignoreFocus = false;
    });

    // ---------- Start: STBY ----------
    frame.dataset.state = "stby";
    statusText.textContent = STATUS.stby;
    endPanel.hidden = true;
    render(0);
  }

  // ==========================================================================
  // Scroll reveal — each [data-reveal] block reveals once
  // ==========================================================================
  function initReveal() {
    const blocks = document.querySelectorAll("[data-reveal]");
    if (!blocks.length) return;

    const reveal = (block) => block.classList.add("is-revealed");

    if (reduceMotion || !("IntersectionObserver" in window)) {
      blocks.forEach(reveal);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          reveal(entry.target);
          observer.unobserve(entry.target);
        }
      },
      { threshold: 0.3 }
    );
    blocks.forEach((block) => observer.observe(block));
  }

  // ==========================================================================
  // Trailer — facade: the embed is only created when the visitor presses play
  // ==========================================================================
  function initTrailer() {
    const trailer = document.querySelector("[data-trailer]");
    const button = trailer && trailer.querySelector("[data-trailer-play]");
    const { trailerKind: kind, trailerSrc: src } = trailer ? trailer.dataset : {};
    if (!button || !kind || !src) return; // no trailer yet: button stays disabled

    button.addEventListener("click", () => {
      let player;
      if (kind === "video") {
        player = document.createElement("video");
        player.controls = true;
        player.autoplay = true;
        player.playsInline = true;
      } else {
        player = document.createElement("iframe");
        player.title = "Playback — trailer";
        player.allow = "autoplay; fullscreen; picture-in-picture; encrypted-media";
        player.allowFullscreen = true;
      }
      player.className = "trailer__embed";
      player.src = src;
      trailer.append(player);
      trailer.classList.add("is-playing");
      player.focus();
    }, { once: true });
  }

  // ==========================================================================
  // Menu overlay — focus trap, Escape, scroll lock
  // ==========================================================================
  function initMenu() {
    const menu = document.querySelector("[data-menu]");
    const toggle = document.querySelector("[data-menu-open]");
    const closeButton = menu && menu.querySelector("[data-menu-close]");
    if (!menu || !toggle || !closeButton) return;

    const root = document.documentElement;
    let hideTimer = 0;

    const focusables = () => [...menu.querySelectorAll("a[href], button:not([disabled])")];

    function open() {
      clearTimeout(hideTimer);
      menu.hidden = false;
      void menu.offsetWidth; // start the fade from opacity 0
      menu.classList.add("is-open");
      root.classList.add("menu-open");
      toggle.setAttribute("aria-expanded", "true");
      closeButton.focus();
    }

    function close() {
      menu.classList.remove("is-open");
      root.classList.remove("menu-open");
      toggle.setAttribute("aria-expanded", "false");
      hideTimer = setTimeout(() => { menu.hidden = true; }, reduceMotion ? 0 : 200);
      toggle.focus({ preventScroll: true });
    }

    toggle.addEventListener("click", open);
    closeButton.addEventListener("click", close);

    menu.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        close();
        return;
      }
      if (event.key !== "Tab") return;

      const items = focusables();
      const first = items[0];
      const last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });
  }

  // ==========================================================================
  // Press Kit stills gallery — thumbnails, prev/next, arrow keys
  // ==========================================================================
  function initGallery() {
    const gallery = document.querySelector("[data-gallery]");
    if (!gallery) return;

    const image = gallery.querySelector("[data-gallery-image]");
    const thumbs = [...gallery.querySelectorAll("[data-gallery-thumb]")];
    if (!image || !thumbs.length) return;

    let current = 0;
    const last = thumbs.length - 1;

    const strip = gallery.querySelector("[data-gallery-strip]");
    const prevButton = gallery.querySelector("[data-strip-prev]");
    const nextButton = gallery.querySelector("[data-strip-next]");
    const scrollBehavior = reduceMotion ? "auto" : "smooth";

    // Keep the active thumb visible by scrolling the strip only, never the page
    // (same result as scrollIntoView({block: "nearest", inline: "nearest"}),
    // which would also scroll the page when the strip is partly off-screen).
    function revealThumb(thumb) {
      if (!strip) return;
      const item = thumb.parentElement;
      const pad = parseFloat(getComputedStyle(strip).paddingLeft) || 0;
      const start = item.offsetLeft - pad;
      const end = item.offsetLeft + item.offsetWidth + pad - strip.clientWidth;
      if (start < strip.scrollLeft) strip.scrollTo({ left: start, behavior: scrollBehavior });
      else if (end > strip.scrollLeft) strip.scrollTo({ left: end, behavior: scrollBehavior });
    }

    // Load the neighbouring stills ahead of time, so a change doesn't flicker.
    const preload = (i) => {
      if (i >= 0 && i <= last) new Image().src = thumbs[i].dataset.src;
    };

    function updateArrows() {
      prevButton?.setAttribute("aria-disabled", String(current === 0));
      nextButton?.setAttribute("aria-disabled", String(current === last));
    }

    // The one place the selection changes: big image, active thumb, strip and arrows stay in sync.
    function show(index, { focusThumb = false } = {}) {
      const next = Math.min(Math.max(index, 0), last); // no wrapping around
      const changed = next !== current;
      current = next;
      const thumb = thumbs[current];

      image.src = thumb.dataset.src;
      image.alt = thumb.dataset.alt;
      if (changed && !reduceMotion && image.animate) {
        image.animate([{ opacity: 0.35 }, { opacity: 1 }], { duration: 200, easing: "ease-out" });
      }

      thumbs.forEach((button, i) => {
        if (i === current) button.setAttribute("aria-current", "true");
        else button.removeAttribute("aria-current");
      });
      revealThumb(thumb);
      if (focusThumb) thumb.focus({ preventScroll: true });
      updateArrows();
      preload(current - 1);
      preload(current + 1);
    }

    thumbs.forEach((button, i) => button.addEventListener("click", () => show(i)));
    prevButton?.addEventListener("click", () => {
      if (prevButton.getAttribute("aria-disabled") !== "true") show(current - 1);
    });
    nextButton?.addEventListener("click", () => {
      if (nextButton.getAttribute("aria-disabled") !== "true") show(current + 1);
    });

    // Arrow keys while focus is anywhere inside the gallery.
    gallery.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      const onThumb = thumbs.includes(document.activeElement);
      show(current + (event.key === "ArrowRight" ? 1 : -1), { focusThumb: onThumb });
    });

    updateArrows();
    preload(1);
  }

  // Development only: the server lists unset links on <body> (SHOW_PLACEHOLDER_LINKS).
  function warnPlaceholderLinks() {
    const keys = document.body.dataset.placeholderLinks;
    if (keys) {
      console.warn(`[Playback] Placeholder external links (set them in EXTERNAL_LINKS in app.py): ${keys}`);
    }
  }

  initHiddenCamera();
  initReveal();
  initTrailer();
  initMenu();
  initGallery();
  warnPlaceholderLinks();
})();
