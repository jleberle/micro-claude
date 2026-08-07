#!/usr/bin/env python3
"""
Assertions over a built faithful-repro site. Run by scripts/repro.sh.

These encode the invariants that CI cannot check, because CI builds this theme
standalone with no plugins and no theme-blank. The failure class they cover is
the one behind the June 2026 incident: another theme in the stack quietly
winning a template we believe is ours.

Exit code is the number of failures, so the caller can gate on it.
"""
import json
import os
import re
import sys

ENTITY = re.compile(r"&(?:[a-zA-Z][a-zA-Z0-9]*|#\d+);")
# a bare & not starting a valid character reference is an ambiguous ampersand
BARE_AMP = re.compile(r"&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#\d+|#[xX][0-9a-fA-F]+);)")

fails = []
notes = []


def check(ok, label, detail=""):
    print("  %s %s%s" % ("PASS" if ok else "FAIL", label,
                         "" if ok else "  <- " + detail))
    if not ok:
        fails.append(label)


def note(label, detail):
    print("  NOTE %s  %s" % (label, detail))
    notes.append(label)


def read(p):
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: assert-repro.py <public-dir> [live-homepage.html]")
    pub = sys.argv[1]
    live = sys.argv[2] if len(sys.argv) > 2 and os.path.exists(sys.argv[2]) else None

    home = read(os.path.join(pub, "index.html"))

    # ---- 1. contested templates: nine paths are defined by more than one theme
    # in the stack (verified with a uniq -d over their layouts/ trees). We are
    # loaded leftmost so ours must win every one. Each marker below appears ONLY
    # in our version.
    print("\n[1] contested templates resolve to THIS theme")
    for label, path, marker in [
        ("head.html (CSP)",            "index.html",          "Content-Security-Policy"),
        ("head.html (JSON-LD)",        "index.html",          "application/ld+json"),
        ("baseof.html (skip-link)",    "index.html",          "skip-link"),
        ("header.html (.site-nav)",    "index.html",          "site-nav"),
        ("footer.html (Elsewhere)",    "index.html",          "Elsewhere"),
        ("robots.txt (AI blocks)",     "robots.txt",          "GPTBot"),
        ("list.archivehtml.html",      "archive/index.html",  "archive-month"),
        ("list.photoshtml.html",       "photos/index.html",   "photos-grid"),
        ("list.archivejson.json",      "archive/index.json",  "content_text"),
    ]:
        p = os.path.join(pub, path)
        check(os.path.exists(p) and marker in read(p), label,
              "marker %r absent from %s" % (marker, path))

    # Markup unique to theme-blank's own templates. Its presence means
    # theme-blank rendered a page we meant to own.
    # NOT usable as a marker: <meta name=generator>. That is Hugo's automatic
    # injection, present on every page including production's — an earlier
    # version of this check used it and flagged all three pages as leaks.
    print("\n[2] no theme-blank leakage")
    leaked = [(f, m) for f, m in (("archive/index.html", "archive_categories"),
                                  ("index.html", "microblog_syndication"))
              if os.path.exists(os.path.join(pub, f))
              and m in read(os.path.join(pub, f))]
    check(not leaked, "no theme-blank markup on our pages", "leaked: %s" % leaked)

    # ---- 3. permalink shape must match micro.blog's /YYYY/MM/DD/slug.html
    print("\n[3] permalink shape")
    idx = json.load(open(os.path.join(pub, "archive", "index.json")))
    urls = [i["url"] for i in idx["items"]]
    bad = [u for u in urls if not re.search(r"/\d{4}/\d{2}/\d{2}/[^/]+\.html$", u)]
    check(not bad, "all %d post URLs are /YYYY/MM/DD/slug.html" % len(urls),
          "e.g. %s" % bad[:2])

    # ---- 4. the search index must be plain text (JSON Feed requires it, and
    # search.js renders snippets with textContent, which does not decode)
    print("\n[4] search index is plain text")
    ent = [i["url"] for i in idx["items"] if ENTITY.search(i.get("content_text") or "")]
    check(not ent, "no HTML entities in content_text (%d items)" % len(idx["items"]),
          "%d affected, e.g. %s" % (len(ent), ent[:1]))
    secs = [i["url"] for i in idx["items"] if i["url"].rstrip("/").endswith("/post")]
    check(not secs, "no section-page entries", str(secs[:2]))

    # ---- 5. JSON-LD carries real characters, not entity text
    print("\n[5] JSON-LD is clean")
    bad_ld, ws = [], []
    for root, _, files in os.walk(pub):
        for f in files:
            if not f.endswith(".html"):
                continue
            for blob in re.findall(
                    r'<script type="?application/ld\+json"?>(.*?)</script>',
                    read(os.path.join(root, f)), re.S):
                try:
                    graph = json.loads(blob)["@graph"]
                except Exception as exc:
                    bad_ld.append("unparseable in %s: %s" % (f, exc))
                    continue
                for node in graph:
                    for k, v in node.items():
                        if not isinstance(v, str):
                            continue
                        if ENTITY.search(v):
                            bad_ld.append("%s.%s=%r" % (node.get("@type"), k, v[:40]))
                        elif v != v.strip():
                            # cosmetic only: consumers trim. Not a gate, because
                            # the fix would mean adding a filter to head.html's
                            # derivation pipeline, and that pipeline's escaping
                            # behaviour is order-sensitive (see its comment).
                            ws.append("%s.%s" % (node.get("@type"), k))
    check(not bad_ld, "no HTML entities in any JSON-LD",
          "%d issues, e.g. %s" % (len(bad_ld), bad_ld[:2]))
    if ws:
        note("%d JSON-LD value(s) with edge whitespace" % len(ws), "cosmetic, not gated")

    # ---- 6. no template artifacts anywhere in the output
    print("\n[6] no template artifacts")
    artifacts = ("error calling", 'executing "', "<no value>", "ZgotmplZ",
                 "0001-01-01", "January 1, 0001")
    hits = []
    for root, _, files in os.walk(pub):
        for f in files:
            if not f.rsplit(".", 1)[-1] in ("html", "json", "xml", "txt"):
                continue
            # sitemap.xml is theme-blank's template, not ours, and it emits
            # 0001-01-01 for undated standing pages — production's live sitemap
            # contains exactly the same one. Not our artifact to gate on.
            if f == "sitemap.xml":
                continue
            body = read(os.path.join(root, f))
            for a in artifacts:
                if a in body:
                    hits.append("%s: %r" % (os.path.relpath(os.path.join(root, f), pub), a))
    check(not hits, "no artifact strings in rendered output",
          "%d hits, e.g. %s" % (len(hits), hits[:2]))

    # ---- 7. the stylesheet actually went through Hugo Pipes
    print("\n[7] CSS pipeline")
    href = re.search(r'href=["\']?(/css/main[^"\'>\s]*\.css)', home)
    check(bool(href), "stylesheet link present")
    if href:
        f = os.path.join(pub, href.group(1).lstrip("/"))
        check("main.min." in href.group(1), "stylesheet is minified+fingerprinted",
              href.group(1))
        check(os.path.exists(f), "fingerprinted file exists on disk", f)
        if os.path.exists(f):
            size = os.path.getsize(f)
            check(size < 30000, "minified size %d < 30000" % size)

    # ---- 8. comparison against production, when a live copy was fetched
    print("\n[8] parity with production")
    if not live:
        note("skipped", "no live homepage available (offline or --no-live)")
    else:
        liv = read(live)

        def section_rows(html, header):
            m = re.search(re.escape(header) + r".*?</ul>", html, re.S)
            return len(re.findall(r"media-entry-info", m.group(0))) if m else 0

        # exact: these are driven purely by post content, which the backup has
        for name, hdr in [("Finished Reading", "Finished Reading")]:
            a, b = section_rows(home, hdr), section_rows(liv, hdr)
            check(a == b, "%s rows match live (%d)" % (name, b), "local %d vs live %d" % (a, b))
        a = len(re.findall(r'post-entry[ "]', home))
        b = len(re.findall(r'post-entry[ "]', liv))
        check(a == b, "Highlights rows match live (%d)" % b, "local %d vs live %d" % (a, b))

        for name, pat in [("JSON-LD", "application/ld"), ("CSP", "Content-Security-Policy"),
                          ("skip-link", "skip-link")]:
            a, b = len(re.findall(pat, home)), len(re.findall(pat, liv))
            check(a == b, "%s count matches live (%d)" % (name, b),
                  "local %d vs live %d" % (a, b))

        # advisory: these CANNOT match locally and it is not a defect.
        # Currently Reading merges data/bookshelves.json, which micro.blog
        # generates at build time and the backup does not contain. Movies is
        # capped by a backend plugin field whose value is invisible locally
        # (config.json's default is 6; production was observed at 5).
        for name, hdr in [("Currently Reading", "Currently Reading"), ("Movies", ">Movies<")]:
            a, b = section_rows(home, hdr), section_rows(liv, hdr)
            if a == b:
                print("  PASS %s rows match live (%d)" % (name, b))
            else:
                note("%s local %d vs live %d" % (name, a, b),
                     "expected: fixture shelf data / backend-only field")

    print("\n%s  %d failure(s), %d advisory note(s)" %
          ("FAILED" if fails else "OK", len(fails), len(notes)))
    if fails:
        for f in fails:
            print("  - %s" % f)
    return len(fails)


if __name__ == "__main__":
    sys.exit(main())
