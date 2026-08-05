/* Client-side search for /search/.
 *
 * Absorbed from microdotblog/plugin-search-page (2026-08-05) so that plugin can
 * be uninstalled — it also shipped a layouts/list.archivejson.json using
 * .Site.Author.avatar, removed in Hugo 0.156, which is what broke full rebuilds
 * in June 2026 (see CLAUDE.md "Manual full rebuild"). Same approach as the
 * original: fetch the whole archive index once, match every keyword against
 * title + body. Differences are noted inline.
 *
 * The index it reads is this theme's own layouts/list.archivejson.json, which
 * emits full-text .Plain — keep that template; search depends on it.
 */
(function () {
  "use strict";

  var INDEX_URL = "/archive/index.json";
  var SLOW_MS = 1500;
  var DEBOUNCE_MS = 120;
  var SNIPPET = 200;

  var input = document.getElementById("search-input");
  var status = document.getElementById("search-status");
  var list = document.getElementById("search-results");
  /* Every other page loads this file too if it is ever added site-wide; bail
     quietly when the search markup isn't present. */
  if (!input || !status || !list) return;
  var form = input.form;
  var items = null;
  var pending = null;

  function say(text) {
    status.textContent = text;
  }

  /* Build rows with DOM nodes rather than innerHTML. The original assigned post
     text straight into innerHTML, so any markup surviving into content_text was
     re-parsed into the page. */
  function render(results, query) {
    list.textContent = "";

    if (!query) {
      say("");
      return;
    }
    if (!results.length) {
      say('No posts match "' + query + '".');
      return;
    }
    say(
      results.length === 1
        ? '1 post matches "' + query + '".'
        : results.length + ' posts match "' + query + '".'
    );

    var frag = document.createDocumentFragment();

    results.forEach(function (item) {
      var li = document.createElement("li");
      li.className = "search-result";

      var meta = document.createElement("div");
      meta.className = "search-result-meta";

      var when = new Date(item.date_published);
      if (!isNaN(when)) {
        var time = document.createElement("time");
        time.dateTime = when.toISOString().slice(0, 10);
        time.textContent = when.toLocaleDateString("en-US", {
          year: "numeric",
          month: "long",
          day: "numeric"
        });
        meta.appendChild(time);
      }
      li.appendChild(meta);

      var head = document.createElement("p");
      head.className = "search-result-title";
      var link = document.createElement("a");
      link.href = item.url;
      /* Untitled posts are the norm here, so fall back to the date for the link
         text — never an empty anchor, which the original could produce. */
      link.textContent =
        item.title && item.title.trim()
          ? item.title
          : time
            ? time.textContent
            : item.url;
      head.appendChild(link);
      li.appendChild(head);

      var body = (item.content_text || "").trim();
      if (body) {
        var p = document.createElement("p");
        p.className = "search-result-summary";
        p.textContent =
          body.length > SNIPPET ? body.slice(0, SNIPPET).trim() + "…" : body;
        li.appendChild(p);
      }

      frag.appendChild(li);
    });

    list.appendChild(frag);
  }

  function search(query) {
    var q = (query || "").trim();
    if (!items || !q) {
      render([], q);
      return;
    }
    var keywords = q.toLowerCase().split(/\s+/);
    var results = items.filter(function (item) {
      var haystack = (
        (item.title || "") +
        " " +
        (item.content_text || "")
      ).toLowerCase();
      return keywords.every(function (k) {
        return haystack.indexOf(k) !== -1;
      });
    });
    render(results, q);
  }

  /* Keep ?q= in the URL so a search is linkable and survives back/forward. */
  function syncURL(q) {
    var url = new URL(window.location.href);
    if (q) {
      url.searchParams.set("q", q);
    } else {
      url.searchParams.delete("q");
    }
    history.replaceState({}, "", url);
  }

  function onInput() {
    window.clearTimeout(pending);
    pending = window.setTimeout(function () {
      var q = input.value.trim();
      syncURL(q);
      search(q);
    }, DEBOUNCE_MS);
  }

  /* Listeners, not inline on* attributes. The original used onChange, which
     fires only on blur/Enter; this searches as you type. */
  input.addEventListener("input", onInput);
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      window.clearTimeout(pending);
      var q = input.value.trim();
      syncURL(q);
      search(q);
    });
  }

  var slow = window.setTimeout(function () {
    say("Loading posts…");
  }, SLOW_MS);

  fetch(INDEX_URL)
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(function (data) {
      window.clearTimeout(slow);
      items = (data && data.items) || [];
      var q = new URL(window.location.href).searchParams.get("q");
      if (q) {
        input.value = q;
        search(q);
      } else {
        say("");
      }
    })
    .catch(function () {
      window.clearTimeout(slow);
      /* The original had no error path at all — a failed fetch left "Loading
         posts..." on screen forever. */
      say("Search is unavailable right now. Try the archive instead.");
    });
})();
