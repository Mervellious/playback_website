/* PLAYBACK — Contact form (loaded only on /contact)
   Validates on blur and submit (same rules as validate_contact() in app.py),
   sends with fetch, and swaps the form for the "Message recorded." panel.
   Without JS the form posts normally and the server renders the same states. */
(() => {
  "use strict";

  const form = document.querySelector("[data-contact-form]");
  const success = document.querySelector("[data-contact-success]");
  if (!form || !success) return;

  const submit = form.querySelector("[data-contact-submit]");
  const submitLabel = form.querySelector("[data-submit-label]");
  const formError = form.querySelector("[data-form-error]");
  const again = success.querySelector("[data-contact-again]");
  const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

  // ---------- Rules ----------
  const rules = {
    topic: () => (form.querySelector('input[name="topic"]:checked') ? "" : "Choose what your message is about."),
    name: () => {
      const value = form.elements.name.value.trim();
      if (!value) return "Enter your name.";
      return value.length > 100 ? "Keep your name under 100 characters." : "";
    },
    email: () => {
      const value = form.elements.email.value.trim();
      if (!value) return "Enter your email address.";
      return value.length > 254 || !EMAIL_RE.test(value) ? "Enter a valid email address, like name@example.com." : "";
    },
    message: () => {
      const value = form.elements.message.value.trim();
      if (!value) return "Write your message.";
      return value.length > 5000 ? "Keep your message under 5000 characters." : "";
    },
    consent: () => (form.elements.consent.checked ? "" : "Tick the box so we can store your message and reply."),
  };

  // The element that carries aria-invalid / aria-describedby for each field.
  const target = (name) => (name === "topic" ? form.querySelector('[data-field="topic"]') : form.elements[name]);
  // Where focus goes when the field is the first invalid one.
  const focusable = (name) => (name === "topic" ? form.querySelector('input[name="topic"]') : form.elements[name]);

  function showError(name, message) {
    const el = target(name);
    const error = form.querySelector(`[data-error-for="${name}"]`);
    if (!el || !error) return;
    error.textContent = message;
    error.hidden = !message;
    if (message) {
      el.setAttribute("aria-invalid", "true");
      el.setAttribute("aria-describedby", error.id);
    } else {
      el.removeAttribute("aria-invalid");
      el.removeAttribute("aria-describedby");
    }
  }

  const check = (name) => {
    const message = rules[name]();
    showError(name, message);
    return message;
  };

  function validateAll() {
    const invalid = Object.keys(rules).filter((name) => check(name));
    if (invalid.length) focusable(invalid[0]).focus();
    return invalid.length === 0;
  }

  // ---------- Blur / change ----------
  ["name", "email", "message"].forEach((name) => {
    form.elements[name].addEventListener("blur", () => check(name));
  });
  form.elements.consent.addEventListener("change", () => check("consent"));
  form.querySelectorAll('input[name="topic"]').forEach((radio) => {
    radio.addEventListener("change", () => check("topic"));
  });
  // Leaving the chip group without choosing one.
  target("topic").addEventListener("focusout", (event) => {
    if (!target("topic").contains(event.relatedTarget)) check("topic");
  });

  // ---------- Topic chips can be unselected ----------
  // Still radio inputs (arrow keys keep working). Clicking the selected chip
  // again, or clicking outside the form, clears the choice. Clicks on the other
  // fields and on SEND MESSAGE keep it, or the form could never be sent.
  // The topic stays required: an empty choice shows the error on submit.
  const chipGroup = form.querySelector(".chips");
  const topicRadios = [...form.querySelectorAll('input[name="topic"]')];
  let checkedOnPress = null; // the radio that was already checked when the pointer went down

  const clearTopic = () => topicRadios.forEach((radio) => { radio.checked = false; });

  topicRadios.forEach((radio) => {
    radio.closest("label").addEventListener("pointerdown", () => {
      checkedOnPress = radio.checked ? radio : null;
    });
    radio.addEventListener("click", () => {
      if (checkedOnPress === radio) radio.checked = false; // second click on the same chip
      checkedOnPress = null;
    });
  });

  document.addEventListener("pointerdown", (event) => {
    if (chipGroup && !form.hidden && !form.contains(event.target)) clearTopic();
  });

  // ---------- States ----------
  function setSending(sending) {
    submit.disabled = sending;
    submitLabel.textContent = sending ? "RECORDING…" : "SEND MESSAGE";
  }

  function showFormError(message) {
    formError.textContent = message;
    formError.hidden = !message;
  }

  function showSuccess() {
    form.hidden = true;
    success.hidden = false;
    success.querySelector("h2").setAttribute("tabindex", "-1");
    success.querySelector("h2").focus();
  }

  again.addEventListener("click", (event) => {
    event.preventDefault();
    form.reset();
    Object.keys(rules).forEach((name) => showError(name, ""));
    showFormError("");
    success.hidden = true;
    form.hidden = false;
    focusable("topic").focus();
  });

  // ---------- Submit ----------
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    showFormError("");
    if (!validateAll()) return;

    setSending(true);
    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" },
        credentials: "same-origin",
      });
      const result = await response.json().catch(() => ({}));

      if (response.ok && result.ok) {
        showSuccess();
        return;
      }
      if (result.errors) {
        Object.keys(rules).forEach((name) => showError(name, result.errors[name] || ""));
        const first = Object.keys(rules).find((name) => result.errors[name]);
        if (first) focusable(first).focus();
      } else {
        showFormError(result.error || "Something went wrong and your message wasn't sent. Please try again.");
      }
    } catch {
      showFormError("We couldn't reach the server. Check your connection and try again.");
    } finally {
      setSending(false);
    }
  });
})();
