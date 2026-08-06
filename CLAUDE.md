# micro-claude theme — Claude session notes
Last updated: 2026-08-05 (RSS re-import landmine diagnosed; bookgoals + bookshelf + search-page + cc plugins absorbed; robots.txt/security.txt self-served; audits: bug sweep, dead-code, units, readability, web standards; palette sync)

## What this repo is
A custom Hugo theme for Jared Eberle's micro.blog at **eberle.blog**.
- GitHub: `github.com/jleberle/micro-claude`
- micro.blog pulls from the **main** branch (the remote default — push to main).
  CLAUDE.md previously said "master"; that was STALE — on 2026-06-10 the remote's
  only branch and default was `main` (recent live deploys all came from it). A
  stray remote `master` created that day by pushing on autopilot was deleted.
- Local dev: `hugo server` from `/Users/jaredeberle/git/microblog-theme/`
- Hugo locally: 0.163 (Homebrew) | micro.blog production: **0.158**
  Also kept: pinned `~/.local/bin/hugo-0.158` and `/tmp/hugo091/hugo` (0.91.2,
  re-download from GitHub releases if gone — /tmp is not persistent)

### Installed on micro.blog as a PLUGIN, not a Theme
- It is added under micro.blog's **Plugins**, not selected as the active Theme.
  Reason: `opengraph.html` (the OG card template) is **only loaded for plugins** —
  when this repo is installed as the active Theme, micro.blog does NOT render
  opengraph.html and the custom OG card never generates. As a plugin it overlays
  the active/default theme and the card works.
- Consequence: `plugin.json` `fields` become editable settings in the micro.blog
  backend. Social links live there (see "Editable settings" below) instead of being
  hardcoded-only. Our `config.json` `params` are now LOW-precedence defaults that
  backend field values override.

## Identities to keep straight
- micro.blog username: **eberle** (hosts eberle.blog, avatar URL uses this)
- Personal site / Bluesky / LibraryThing handle: **jaredeberle**
- Avatar: `https://micro.blog/eberle/avatar.jpg` (jaredeberle/avatar.jpg is 404)
- Always push: `git push origin main`

## Editable settings (plugin.json fields)
Because this is installed as a plugin, `plugin.json` `fields` render as form
inputs in the micro.blog backend (Plugins → this plugin). Real micro.blog schema
(confirmed from installed plugins like plugin-cc / wayback-link-preserver):
```json
{ "field": "params.social_bluesky_url", "label": "Bluesky URL",
  "placeholder": "https://...", "type": "string" }
```
- Key is `"field"` (dotted `params.<name>`), NOT `name`. Types: `string` / `boolean`.
- There is NO `default` mechanism — `placeholder` is only a hint. A value typed in
  the backend overrides any `config.json` `params` default. **VERIFIED in production
  (2026-06-06):** edited a `social_*_url` field in the micro.blog backend and the
  live link updated accordingly, confirming backend > config.json precedence.
- Currently exposed: the 5 `social_*_url` links. Templates read `.Site.Params.
  social_*_url` and guard with `{{ with }}`, so an empty field just hides that link.
- **The social URLs now live ONLY in the backend (plugin.json fields).** Their
  `config.json` defaults were removed (2026-06-06) once the backend was verified as
  the source of truth. Consequences: (a) a backend field left BLANK hides that link
  on the live site — no fallback; (b) local `hugo server` no longer shows the social
  links at all, since plugin.json fields are backend-only and config.json no longer
  carries them. If you want them back in local preview, re-add them to config.json
  `params` as low-precedence defaults (backend still overrides).

## How micro.blog renders this theme
micro.blog uses **its own base template** for the page skeleton:
- Header: `<header id=site-header>` (NOT our header.html class)
- Main content: `<main class=main id=main>`
- Footer: `<footer id=site-footer>`

Our theme provides:
- `{{ define "main" }}` content blocks (index.html, list.html, single.html, etc.) — **these ARE used**
- CSS in `static/css/main.css` — **loaded on every page**
- Partials (header.html, footer.html, baseof.html) — **may or may not be used depending on build**

CSS must target BOTH `#site-header` and `.site-header` (and same for footer/main)
to handle both micro.blog's default structure and our custom partials.

## Known platform behavior
### Manual full rebuild (Hugo 0.158) — FIXED & VERIFIED IN PRODUCTION (2026-06-06)
- A live full rebuild now succeeds with the home page + feeds intact. Full
  rebuilds are safe again. Upstream issue reported to plugin-search-page.
- Symptom: triggering "full rebuild" broke the **home page + RSS/JSON feeds**
  (404) while every other page rendered fine. Fastpublish was unaffected; a 0.117
  full rebuild was also fine.
- **Actual root cause:** the `plugin-search-page` plugin ships
  `layouts/list.archivejson.json` whose line 4 uses `.Site.Author.avatar`
  (REMOVED in Hugo 0.156). That template renders the home node's **ArchiveJSON**
  output format — one of ~10 output formats the home node emits (HTML, RSS, JSON,
  RSD, ArchiveHTML/JSON, PhotosHTML/JSON, PodcastXML/JSON). When it faults, the
  WHOLE home node fails, taking the home page and both feeds (feed.xml/feed.json)
  with it. Other page kinds don't emit ArchiveJSON, so they survive.
- Why each clue fit: home+feed only = same node; 0.158 only = `.Site.Author`
  removed in 0.156 (present in 0.117); full-rebuild only = fastpublish serves the
  ArchiveJSON output from cache; custom-theme only = stock theme ships its own
  correct `list.archivejson.json` that shadows the plugin's; ours did not.
- The old "PR #14601 / platform RSS bug" theory was WRONG. `opengraph.html`
  presence was also NOT the cause (Mythos theme has it and full-rebuilds fine).
- **Fix (shipped):** added `layouts/list.archivejson.json` to this theme with the
  correct `.Site.Params.author.avatar` (keeps the plugin's full-text `.Plain`
  search index). Theme out-ranks plugins in template lookup, so ours shadows the
  broken copy. Full rebuilds should now be safe.
- **Reported upstream** (2026-06-07) to github.com/microdotblog/plugin-search-page
  (line 4 should be `.Site.Params.author.avatar`). Our override stays until the fix
  lands there; once it does, the override can go.

### ArchiveJSON output lags builds (observed 2026-06-10)
- After pushing the `feed_url` fix and running a manual FULL rebuild, every output
  (photos HTML, archive HTML, CSS, homepage) served the new code — EXCEPT
  `/archive/index.json`, which had a fresh last-modified (same second as the rest
  of the build) but the PREVIOUS generation's content. micro.blog apparently
  copies a previously-rendered ArchiveJSON artifact into new builds rather than
  always re-rendering it. Expect this file to be stale-by-one; it should catch up
  on a later build. Not harmful (only the feed_url metadata differed).
- **Template-winner fingerprints** for /archive/index.json (who actually rendered it):
  theme-blank → `content_text` truncated to 100 chars; plugin-search-page → fatal
  on 0.158 (`.Site.Author.avatar`); OUR override → full-text `.Plain` +
  `Params.author.avatar` icon + `feed_url` ending `archive/index.json`.
- **2026-08-05, resolved — our override IS winning, but the file can be stale by
  a build.** Mid-session the live file served
  `"feed_url":"https://eberle.blog/photos/index.json"`, a string our committed
  template cannot emit (ours says `archive/`) with `HEAD == origin/main`, which
  looked like proof the override was losing. After a fresh build later the same
  day it serves `archive/index.json` — so all three fingerprints (full-text
  `.Plain`, `Params.author.avatar` icon, correct `feed_url`) now line up and the
  override is confirmed. The earlier reading was the documented "ArchiveJSON
  output lags builds" behaviour, just lagging by longer than one build.
  - **Lesson: do not diagnose this file from a single fetch.** Its content can be
    current while its metadata is a generation behind. Force a rebuild, then
    re-check.
  - **Still true regardless:** uninstalling plugin-search-page removes its broken
    `.Site.Author.avatar` template from the build outright, which is a stronger
    guarantee than shadowing it.
- **theme-blank is the ORIGIN of the `feed_url: photos/index.json` copy-paste bug**
  (its own `list.archivejson.json` has it; plugin-search-page copied it, and so did
  our first override).

### "Raw HTML omitted" WARNs = micro.blog's GitHub-archive job, NOT the site build
- UPDATE 2026-06-11: these warnings are NOT only stale-log residue — fresh ones
  appeared after the log was cleared on 2026-06-10 (naming book posts with raw
  `<img>` covers), DESPITE our config.json carrying `ignoreLogs` the whole time.
  That's production proof that a plugin/theme config.json cannot suppress them.
- Per micro.blog staff (Manton, help.micro.blog/t/occasional-error-message/4297):
  the warnings come from the **automated GitHub archiving process**, which runs
  its own render pass with default goldmark settings (unsafe=false). The REAL
  site build runs unsafe=true — which is why live post pages render their raw
  HTML fine while the error log still collects these WARNs. Cosmetic only.
- **For "finished reading" BOOK posts the raw HTML is INJECTED by micro.blog, NOT
  in your source — so it is NOT editable-away (VERIFIED 2026-06-14).** The editable
  post body is pure markdown (`Finished reading: [Title](https://micro.blog/books/
  <ISBN>) by Author 📚`), but micro.blog's book pipeline PREPENDS a raw cover `<img>`
  at render time. Confirmed from the live `feed.json` content_html:
  `<img src="https://cdn.micro.blog/books/<ISBN>/cover.jpg" align="left"
  class="microblog_book" style="max-width:60px;…">` ahead of the `<p>`. The real
  build (unsafe=true) keeps that `<img>`; the archive pass (unsafe=false) strips it →
  the WARN. Because the tag isn't in your markdown, lever (a) below CANNOT remove it.
- User-side levers: (a) edit the offending posts, replacing any raw `<img ...>` you
  AUTHORED with markdown `![alt](url)` — goldmark renders md images natively, so no
  warning in ANY pass; use md image syntax in future posts. **Does not help the
  book-post case above** (the `<img>` is platform-injected, source is already clean).
  (b) Disable GitHub archiving (stops the job, loses the backup) — the only lever
  that silences the book-post WARNs. (c) Clear the log manually and ignore (cosmetic;
  live site unaffected). There is NO config fix available to users for the archive pass.
- **`config.json`'s top-level `markup`/`ignoreLogs`/`minify`/`pluralizeListTitles`
  keys were REMOVED (2026-07-29) — confirmed dead in PRODUCTION, not just local
  testing.** Vanilla Hugo only merges `params`/`menus`/`outputFormats`/
  `mediaTypes` from a theme's config.json (verified empirically — even
  `pluralizeListTitles: false` didn't merge). That was originally logged as a
  "local builds" footnote, but it isn't local-only: plugins load through the
  exact same Hugo `--theme` mechanism as themes — the local 0.158 repro command
  above passes this repo and every installed plugin together in one
  `--theme=micro-theme,plugin-cc,...` flag. micro.blog's Theme-vs-Plugin
  distinction only changes whether `opengraph.html` loads and which settings
  become backend fields; it doesn't change how Hugo merges config.json. So
  these four keys did nothing in production either, while still reading as if
  they controlled something (raw-HTML warnings, minification, goldmark safety).
  For LOCAL testing, set them in the SITE-ROOT export's own `config.json`
  instead (e.g. `markup.goldmark.renderer.unsafe: true`) — production already
  runs `unsafe=true` and its own minify/log settings regardless of what this
  repo ships.

### micro.blog strips `<style>` tags from theme template output
- Cannot inject page-scoped CSS via `<style>` tags in layout files
- Use `main.css` with `:has()` selectors instead for page-specific rules

### Archive/Photos pages are HOME-node outputs (root-level template rule)
- `/archive/` and `/photos/` are NOT section lists — they are the **home node's**
  `ArchiveHTML` / `PhotosHTML` output formats (`path: "archive"`/`"photos"`,
  `baseName: "index"`). Same node family as the HTML page, RSS, and JSON feeds.
- **Lookup consequence:** for the *home* kind, Hugo checks `layouts/list.archivehtml.html`
  (ROOT) BEFORE `layouts/_default/list.archivehtml.html`. micro.blog's default
  `theme-blank` ships the ROOT-level copies (`list.archivehtml.html`,
  `list.photoshtml.html`, etc.), so a `_default/` copy from a theme OR plugin **never
  wins** — regardless of plugin order. This is why `plugin-archive-months` and
  `plugin-photos-months` (both templates at `_default/`) silently did nothing and the
  plain theme-blank flat lists rendered (no months). Our old archive override was also
  at `_default/` → dead, and its classes didn't even match `main.css`.
- **Fix (2026-06):** added ROOT-level `layouts/list.archivehtml.html` and
  `layouts/list.photoshtml.html` (mirroring `list.archivejson.json`), matching
  `main.css` classes (`.archive-cats`/`.archive-month`/`.archive-entry-*` and
  `.photos-grid`; photo months reuse `.archive-month`). Both are themed + month-grouped;
  archive honors `archive_months_photos`. Verified via the local 0.158 + full-plugin
  repro: our markers render, theme-blank's `h-feed`/`h-entry`/`photos-grid-container` gone.
- **Both month plugins are superseded and were UNINSTALLED on micro.blog
  (2026-06-10)** — `plugin-archive-months` and `plugin-photos-months` provided only
  `_default/` templates that could never win. The `archive_months_photos` toggle was
  moved into THIS repo's `plugin.json` (boolean field), with `config.json` keeping
  `true` as the default.
- Same rule applies to any home-node output override (feeds, RSD): put it at ROOT,
  not `_default/`.

### microblog_head.html
- micro.blog INJECTS this partial at the platform level — it is NOT in the theme repo
- `.gitignore` includes `layouts/partials/microblog_head.html` for the local dev stub
- Local stub provides RSS alternate link so `hugo server` works without errors
- NEVER commit the local stub — micro.blog provides the real one in production
- Do NOT use `templates.Exists` guard — platform partials return false and break feed

## File structure
```
static/
  .well-known/
    security.txt           # RFC 9116; unsigned copy of ~/git/website's, +eberle.blog
                           #   Canonical. static/ works here because micro.blog has
                           #   no default at this path — contrast robots.txt below
layouts/
  robots.txt               # MUST be layouts/, not static/ — micro.blog ships a
                           #   default robots.txt and only a layout overrides it
  shortcodes/
    readinggoals.html      # PREFERRED name in content — micro.blog re-installs
                           #   plugin-bookgoals whenever content calls the
                           #   `bookgoals` name, and the plugin then wins
    bookgoals.html         # fallback under the plugin's own name
    bookshelf.html         # bookshelf embed, absorbed from the plugin
  partials/
    reading-goals.html     # shared logic behind both goals shortcodes
  _default/
    baseof.html              # page skeleton (may be overridden by micro.blog)
    list.html                # category/section list pages
    single.html              # generic single page
  list.archivehtml.html      # /archive/ — ROOT level (NOT _default) so it wins the
                             #   home-node ArchiveHTML lookup vs theme-blank; themed
                             #   month-grouped archive (see "Archive/Photos pages" below)
  list.photoshtml.html       # /photos/ — ROOT level; themed month-grouped photo grid
                             #   (.photos-grid). Supersedes plugin-photos-months.
  list.archivejson.json      # home-node ArchiveJSON (search index + Author fix)
  opengraph.html             # OG card template (micro.blog's non-Hugo renderer)
  partials/
    head.html                # <head> block including microblog_head.html call
    header.html              # site header with conditional avatar
    footer.html              # custom footer: RSS · Micro.blog · Theme · Codeberg
    intro.html               # homepage bio card with avatar + social links
    custom_footer.html       # intentionally blank override hook
  post/
    single.html              # post pages with microformat markup + categories
  section/
    replies.html             # /replies/ page
  index.html                 # HOMEPAGE: intro + status + currently reading +
                             #           books/movies + highlights
content/
  search.md                # /search/ page + nav entry, absorbed from
                           #   plugin-search-page (see that section)
static/js/search.js        # the only JS this theme owns; powers /search/
static/css/main.css          # all styling — Northeaster palette (light-only,
                             #   shared token names/values with ~/git/website)
config.json                  # Hugo config + local dev params
plugin.json                  # micro.blog theme metadata + settings fields
.gitignore                   # excludes public/, resources/, microblog_head.html
```

## Homepage sections (layouts/index.html)
1. **Intro card** — avatar + bio + social links (from `intro.html`)
2. **Status card** — most recent post in "Status" category
3. **Currently Reading** — merged: imported `Started reading:` posts with no matching
   finished entry (dated, newest first), then Micro.blog's Currently Reading bookshelf
   (`.Site.Data.bookshelves`, undated, shelf order) for books with no post at all
4. **Finished Reading | Movies** — two-column, recent `Finished reading:`/Movies posts
5. **Highlights** — recent posts in "Highlights" category

- **Sourcing:** one base slice — `(where .Site.RegularPages "Type" "post").ByDate.Reverse`
  — then per-section `where ... "Params.categories" "intersect" (slice <name>)`. `where`
  preserves order, so derived slices are NOT re-sorted.
- **Category names + counts are params.** Names (`home_cat_status/started_reading/
  finished_reading/movies/highlights`) live in `config.json`. Counts (`home_reading_count`/
  `home_books_count`/`home_movies_count`/`home_highlights_count`) are `config.json` defaults
  AND exposed as **backend fields** in
  `plugin.json` so they can be tuned without a push. **Counts are validated, never cast
  raw (2026-06-11):** Hugo's `int` is FATAL on any malformed string — even `"5 "` with a
  trailing space (verified empirically on 0.158) — and a fault in index.html kills the
  whole home node (page + feeds), so a typo in the backend settings form could have taken
  the site down on the next full rebuild. Each count now starts at a hardcoded default
  (5/6/10, mirroring config.json) and is overwritten only when a digits-only
  `findRE` (pattern `^(0|[1-9][0-9]*)$`) matches the space-trimmed `printf "%v"`. The
  regex also rejects leading zeros because Go's cast parses them as OCTAL (`int "010"` =
  8, verified). Blank/missing/malformed values fall back silently. Guard verified on
  0.91.2, 0.158, and 0.163 (matrix: "8"→8, 7→7, "5 "/""/"abc"/"010"/missing→default).
- **De-duplicated across sections:** a `$seen` slice of permalinks is built in section
  order (Status → Currently Reading → Finished Reading → Movies → Highlights); each section
  filters with `where ... "Permalink" "not in" $seen` so a post in multiple categories
  appears only once (e.g. a Finished Reading+Status post shows in Status, not again below).
- **Currently Reading is derived from Started/Finished pairs, not the bookshelf plugin.**
  Started-reading posts are detected by either the `Started Reading` category OR a first
  line beginning `Started reading:`; finished-reading posts are detected the same way with
  `Finished Reading` / `Finished reading:`. Started-reading posts are shown until a matching
  finished-reading post exists. That lets imported RSS posts behave like native Micro.blog
  book entries without a brittle dependency on exact category labels.
- **Currently Reading merges TWO sources (2026-07-27): started-reading POSTS and
  Micro.blog's Currently Reading BOOKSHELF.** The shelf is the point: a book moved
  onto it in the Micro.blog backend shows up **without any post existing**. Shelf data
  is `.Site.Data.bookshelves.<shelf>` where `<shelf>` is the shelf name lowercased with
  spaces removed (`currentlyreading`), configurable via `home_shelf_currently_reading`
  (config.json default + plugin.json backend field). Each book has EXACTLY
  `title`/`author`/`isbn`/`cover_url` — **no date** (confirmed against
  help.micro.blog/t/bookshelves/515), which is why shelf entries cannot be interleaved
  chronologically and are appended AFTER the dated post entries, in shelf order.
  - **The list is built from dicts, not Pages** (`label`/`review`/`cover`/`coverLink`/
    `link`/`date`/`dated`) — a shelf book has no Page behind it, so the old
    `range` -over-Pages render loop could not represent one.
  - **De-dup, both directions:** a shelf book is skipped when a post already covers it
    (the POST wins — it has a date, permalink and notes) or when it is already finished
    (shelf not yet updated after a `Finished reading:` post). Matching is by ISBN OR by
    the same normalized `<title> by <author>` key used for started/finished pairing —
    the shelf's `title` + `author` normalize to exactly that shape, which is what makes
    cross-source matching work for ISBN-less academic entries.
  - **Rows read `<title> by <author>` regardless of source** (the `$label` field: the
    headline minus the action prefix and minus 📚-onward), so the two sources are
    visually indistinguishable. The Finished Reading column still shows full headlines
    (`$m.title`) — deliberate, it has no shelf merge; unify it if that seam bothers you.
  - Degrades silently when the data is absent (`with` guards): no `data/` dir at all
    (local `hugo server`), a shelf key that matches nothing, and an empty shelf array
    all just render the post-derived entries. Verified.
  - **Capped by `home_reading_count` (default 8, added 2026-07-27) — AFTER merging, not
    before.** Every other homepage section was already capped; this one wasn't, and it's
    unbounded on two independent axes now (unfinished started-posts accumulate; shelves
    grow). Capping before merging would let a full page of one source crowd out the other
    depending on which was built first; `{{ $reading = first $readingCount $reading }}`
    runs once, after both sources are appended, same validated-int-or-fallback guard as
    the other counts.
  - **Cover links get a real `aria-label`, not a stripped-from-tree treatment.** The cover
    and title link often point at genuinely DIFFERENT destinations — cover → the Micro.blog
    book page (`coverLink`), title → the post permalink (`link`) — whenever an ISBN post
    exists. An earlier draft of this fix used `aria-hidden="true" tabindex="-1"` on the
    cover anchor to kill the duplicate-announcement problem, which was WRONG: it silently
    removed keyboard/AT access to that second destination, not just a redundant label.
    Corrected to `alt=""` on the image + `aria-label="View <label> on Micro.blog"` on the
    anchor — same fix applied to the Finished Reading and Movies cover links for
    consistency (same duplicate-link-text pattern existed in both, pre-existing, not new).
    Movies is conditional: `$movieURL` falls back to the post permalink when no TMDB link
    is found in the content, so the cover's aria-label only claims "on The Movie Database"
    when `$onTMDB` is true — otherwise it just repeats the title, matching where the link
    actually goes.
  - **A shelf book with a `cover_url` but no ISBN is now cover-less by design.** `coverLink`
    for a shelf entry is built only from `$isbn`; before this pass, `$cover` was set from
    `.cover_url` regardless, which — for that particular combination — would have rendered
    an image inside `<a href="">`. Gated `$cover` on `$isbn` too so the two either both
    exist or neither does.
- **Pairing key: ISBN first, normalized "<title> by <author>" second (2026-07-27).** The
  ISBN comes from `.Params.books` when present, else from a `https://micro.blog/books/<isbn>`
  link in the body. **ISBN alone is not enough**, because the website ledger only emits that
  link for `type == "book"` entries that have an `isbn` (`~/git/website`
  `layouts/reading.rss.xml`) — an academic source with only a `doi`/`access_url` gets none,
  and the old `or (not $isbn) …` filter then kept it in Currently Reading **forever**, even
  after its finished event imported (reproduced, then fixed). The fallback key is the title
  line with the `Started/Finished reading:` prefix and everything from `📚` onward stripped,
  whitespace-collapsed, lowercased, trailing punctuation trimmed — identical across a
  source's two events because only the notes after `📚` differ. A started post retires when
  EITHER signal matches a finished post.
- **All per-post reading values are computed once into `$readingMeta`** (a dict keyed by
  permalink: `isbn`/`key`/`title`/`review`), built in the same pass that classifies
  started/finished. The render loops only look values up — previously the ISBN-extraction
  block was copy-pasted in four places and drifted-prone.
- **Status card body is capped** with `.Summary` (HTML-safe, word-bounded by
  summaryLength) instead of full `.Content` — never truncate raw `.Content`, it can sever
  tags. When `.Truncated`, the card's link becomes "Read more →" to the post.
- **Reading cover/link uses structured data first, body link second.** Reading posts use
  the ISBN in front matter (`.Params.books` → `["<isbn>"]`) when present; if absent, the
  homepage falls back to parsing a `https://micro.blog/books/<isbn>` link from `.Content`.
  The cover is then `https://cdn.micro.blog/books/<isbn>/cover.jpg` and the canonical book
  link `https://micro.blog/books/<isbn>`. Title/review are still content-derived for BOTH
  reading and movies (these posts have no title/author front matter), but parsed with exact
  string ops — `trim` + `split "\n"` (first line = title) + `strings.TrimPrefix` (rest =
  review) — instead of fragile `replaceRE`/`^Watched:` patterns.
- **Title/review split falls back to the `📚` marker (2026-07-27).** The newline split above
  works for native Micro.blog book posts (review on its own line) but NOT for the website
  ledger, which packs headline + notes into a single `<p>` (`$content := printf "<p>%s</p>"
  $htmlBody`). With no newline the whole run-on became the title link, untruncated, and
  `.media-entry-review` never rendered — the two sources visibly diverged in the same list.
  So: when the newline split yields an empty review, re-split at `findRE "^.*?📚"`. Both
  shapes carry the `📚`, so one rule covers both. Movies are untouched (Micro.blog-only,
  already multi-line).
- **Column balance:** book rows have a cover (taller) and movie rows are text-only, so the
  two columns diverge in height. Cover width is trimmed in that grid to bring row heights
  closer; the movie count is also backend-tunable to fill remaining space.
  **Corrected 2026-08-05:** this used to say `.media-columns .media-cover { width: 56px }`
  and "currently-reading keeps 80px". Neither `.media-columns` nor those px values exist —
  the live rules are `.media-cover { width: 4.5rem }` with
  `.media-list--reading .media-cover { width: 4.125rem }` (so it is the *reading* list that
  is narrower, the opposite of what was written). Verified against `main.css` and the live
  homepage's rendered classes.

## Hugo version compatibility notes
### The 0.91-vs-0.158 tension (root of the full-rebuild class of bugs)
- micro.blog tells theme/plugin authors to target **Hugo 0.91** as the
  compatibility floor, but **runs 0.158 in production**. So 0.91-era APIs that
  Hugo has since REMOVED are latent landmines: valid by the recommended baseline,
  but they fault on the real engine — and only on a **full rebuild** (fastpublish
  serves cached output). That's exactly how `.Site.Author.avatar` in
  plugin-search-page took down the home node (see "Manual full rebuild").
- Prefer APIs that work on BOTH 0.91 and 0.158. `.Site.Params.author.avatar` is
  the canonical example — valid on 0.91 AND 0.158, unlike the removed
  `.Site.Author.avatar`. Everything changed in the June 2026 session is
  0.91-compatible.
- **0.91 compat VERIFIED with a real 0.91.2 binary — now with ZERO exceptions
  (re-verified 2026-07-27).** The `hugo.Data` call in index.html that used to be the
  one known 0.91 fault ("can't evaluate field Data") is gone; `grep -rn "hugo\.Data\|
  \.Site\.Data" layouts/` returns nothing, and 0.91.2 / 0.158 / 0.164 now render
  byte-comparable homepage output on the same fixture. Gotcha when testing: 0.91 only
  reads `config.toml`, not `hugo.toml`/`hugo.yaml` — a `hugo.yaml`-only fixture builds
  "successfully" while silently ignoring your config.
- **Do NOT migrate to the Hugo 0.146+ "new template system" layout structure.**
  Verified empirically: new-style root-level `layouts/single.html`/`list.html` are
  INVISIBLE to 0.91 (kinds silently get "found no layout file") while working on
  0.163 — migrating would break the 0.91 floor wholesale, not just one line. The
  current old-style tree (`_default/`, `section/replies.html`, `post/single.html`)
  runs on 0.158/0.163 via the legacy compat layer, which micro.blog cannot drop
  without breaking theme-blank and every plugin (all old-style). The root-level
  home-output templates (`list.archivehtml.html` etc.) are valid in BOTH systems.
  Revisit only if/when micro.blog migrates theme-blank itself — and re-verify the
  theme-vs-theme-blank shadowing then (the archive/photos fix depends on lookup
  order).
- **Future landmines** (deprecated on 0.158, not yet removed — will break the same
  way when micro.blog next bumps Hugo): `.Site.LanguageCode` (→ `.Site.Language.Locale`),
  config keys `languageCode` (→ `locale`) and `paginate`, and — **deliberately
  re-introduced 2026-07-27** — `.Site.Data` in `index.html` (the bookshelf merge).
  **`.Site.Data` is the accepted risk, not an oversight:** it is the ONLY accessor
  that works on both the 0.91 floor and production 0.158, because `hugo.Data`
  (0.155+) is fatal on 0.91. Deprecated in 0.156; WARNs on 0.164, silent on 0.158.
  **A version gate does NOT work** — `ge hugo.Version "0.155.0"` returns **TRUE on
  0.91.2** (verified empirically), so the guarded branch executes anyway and still
  faults with "can't evaluate field Data". When micro.blog ships a Hugo that removes
  `.Site.Data`, the fix is a one-line swap to `hugo.Data`; until then this is the
  single highest-priority line to check on any micro.blog Hugo bump, because it sits
  in the home node (page + RSS/JSON feeds all die together).
  NOTE: `.Site.LanguageCode` already misbehaves on micro.blog's 0.158 — it returns
  the literal `-`, which is why `og:locale` was rendering `content="-"`. Fixed by
  hardcoding `og:locale` to `en_US` in head.html (single-locale English blog).
- **Early-warning tool:** the pinned `hugo-0.158` + full-plugin local repro (see
  "Faithful local 0.158 reproduction"). Re-run it against a newer pinned binary
  whenever micro.blog upgrades Hugo to catch the next round of removals before they
  ship. Watch installed PLUGINS too, not just this theme — they carry the same risk.

- `hugo.Data` introduced ~0.155 — now used in `index.html` (switched from `.Site.Data`
  which generates a deprecation WARN on 0.158). Safe: micro.blog runs 0.158 in production
  and won't go backwards. The 0.91 compat guideline is about not using *removed* APIs,
  not about avoiding newer ones.
- `.Site.Author.*` **removed in Hugo 0.156** (deprecated 0.124) — use
  `.Site.Params.author.*`. This is the exact bug that broke full rebuilds via the
  search plugin (see "Manual full rebuild" above).
- `{{ .Title | default .Date.Format "January 2, 2006" }}` invalid in 0.158
  — use `{{ if .Title }}{{ .Title }}{{ else }}{{ .Date.Format "..." }}{{ end }}`
- `opengraph.html` in layouts/ is FINE on 0.158 (Mythos theme proves it) — earlier
  belief that it broke the feed was wrong. **Hugo never renders it**: it's not a
  recognized layout name for any output format, so it's an unused template at build
  time (that's why its contents can't break a full rebuild). It is instead consumed
  by micro.blog's **separate, non-Hugo OG card renderer** (600×315 card, "older web
  renderer ~2010 web standards; uses simple logic similar to Hugo but is NOT Hugo"
  per help.micro.blog/t/open-graph-templates/4011). **Consequence:** the Hugo-0.156
  removal of `.Site.Author.*` does NOT apply here — `.Site.Author.avatar` is the
  DOCUMENTED, correct variable for this file (contrast `list.archivejson.json`,
  which Hugo DOES render, where `.Site.Author.avatar` is fatal). So we use the
  documented `data-avatar-url="{{ .Site.Author.avatar }}"`. Documented OG vars:
  `.Site.Author.avatar/.name/.header`, `.Site.Title/.BaseURL/.Hostname/.Params`,
  and post `.Title/.Content/.Plain/.Summary/.Permalink/.Date/.Params.photos`.
  Put colors in BOTH the inline `style` and the matching `data-*` attribute.
- **micro.blog OVERRIDES `og:image` on POST pages** with the generated card. Even
  though head.html falls back to the avatar for text posts, the live post HTML
  shows `og:image`/`twitter:image` = `https://s3.amazonaws.com/micro.blog/opengraph/
  YYYY/MM/DD/<id>.png` (the rendered opengraph.html card). The HOME page is NOT a
  post, gets no card, so its og:image stays the avatar (by design). So the theme's
  avatar fallback only actually shows for non-post pages.
- **OG cards not appearing on Bluesky/X = scraper cache, not markup.** Verify with
  `curl "https://cardyb.bsky.app/v1/extract?url=<POST_URL>"` (Bluesky's card
  service) — if it returns the right image, the markup is fine. Bluesky snapshots
  the card into the post at posting time and never refreshes, so only NEW posts
  reflect a changed card; X caches ~7 days (append `?x=1` to bust). The card PNG
  regenerates (new s3 filename) when the post or opengraph.html changes.

## CSS: avatar hiding on homepage
```css
/* Only hides avatar when .intro is present — exclusively on homepage */
body:has(.intro) #site-header .site-title img,
body:has(.intro) .site-header .site-title img { display: none; }
```
The `<style>` tag approach in template files does NOT work — micro.blog strips them.

## Local development
```bash
cd /Users/jaredeberle/git/microblog-theme
hugo server
# Requires gitignored stub: layouts/partials/microblog_head.html
# config.json has local dev params (author.avatar, itunes_description, etc.)
```

## Faithful local 0.158 reproduction (matches micro.blog full rebuild)
This is what found the full-rebuild bug. Reproduces production far better than
`hugo server` because it includes the real platform theme + all installed plugins.
- **HEADS UP — the local test folder is NOT persisted and must be RECREATED before
  running any local test.** The site-root export + `themes/` (this theme + every
  installed plugin cloned in + theme-blank) is not kept in this repo. Before running
  either `hugo server` or the pinned-0.158 repro, re-create it: get a fresh micro.blog
  export for the site root, drop in the gitignored `microblog_head.html` stub, and
  re-clone each plugin listed below into `themes/`. Don't assume a prior test folder
  is still there.
- Pinned binary: `~/.local/bin/hugo-0.158` (extended; extracted from
  `hugo_extended_0.158.0_darwin-universal.pkg` so it doesn't clash with Homebrew's
  newer hugo). macOS only ships a `.pkg` for darwin now — no `.tar.gz`.
  **Re-fetch recipe** (the pinned binaries keep disappearing; Homebrew's `hugo` was
  0.164 as of 2026-07-27):
  ```bash
  curl -sL -o h158.pkg https://github.com/gohugoio/hugo/releases/download/v0.158.0/hugo_extended_0.158.0_darwin-universal.pkg
  pkgutil --expand h158.pkg h158exp && cd h158exp && cat Payload | gunzip -dc | cpio -i   # → ./hugo
  # 0.91.2 DOES still ship a tarball (name it exactly, there is no darwin-universal):
  curl -sL https://github.com/gohugoio/hugo/releases/download/v0.91.2/hugo_extended_0.91.2_macOS-ARM64.tar.gz | tar xz -C h091
  ```
- Site root: a micro.blog **export** (content + merged config.json + data + static),
  e.g. `~/jleberle_<id>/`, with a `themes/` dir.
- `theme-blank` IS micro.blog's real default/fallback theme (provides baseof,
  microblog_head, rss.xml, index.xml/json, and ALL home output-format templates:
  list.archive*/photos*/podcast*/rsd). Load YOUR theme first, then every installed
  plugin, then theme-blank last:
```bash
~/.local/bin/hugo-0.158 -s <siteroot> --themesDir=<siteroot>/themes --gc \
  --theme=micro-theme,wayback-link-preserver,mbplugin-youtube-nocookie,theme-blank
```
- Installed plugins (clone each into themes/): **only two remain** —
  wayback-link-preserver and flschr/mbplugin-youtube-nocookie. Both are real
  software this theme has no intention of reproducing (see "plugin-search-page
  absorbed" for the assessment of all five).
- **Five plugins uninstalled 2026-08-05, all verified gone in production the
  same day:** `plugin-cc` (absorbed into `head.html` — live head now carries
  exactly one `rel=license`, not two), `plugin-search-page` (absorbed into
  `content/search.md` + `static/js/search.js` — `/search/` is 200 with our
  `<label>` and no "January 1, 0001"), `microdotblog-bookshelf-shortcode` and
  `plugin-bookgoals` (absorbed into `layouts/shortcodes/` — `/reading/` renders
  `bookshelf-*`/`bookgoals-cover` with 34 `loading=lazy` and no `width="100"`),
  and the AI-blocking robots.txt plugin (superseded by `layouts/robots.txt`,
  94 lines served live). `plugin-archive-months`/`plugin-photos-months` went
  earlier, on 2026-06-10.
  - **The June full-rebuild landmine is now genuinely gone, not merely
    shadowed.** Uninstalling plugin-search-page removes its
    `.Site.Author.avatar` `list.archivejson.json` from the build outright.
    Live `/archive/index.json` confirms ours renders it: `feed_url` ends
    `archive/index.json`, icon from `Params.author.avatar`, 152 items with
    full `.Plain` bodies. **Keep `layouts/list.archivejson.json`** — `/search/`
    depends on that full-text index.
- The local `hugo` CLI aborts the WHOLE build on the first render error (so
  public/ ends up empty); micro.blog tolerates per-node failures and ships the
  rest — which is why prod showed only home+feed gone. Plugins inject head partials
  via `.Site.Params.plugins_html`; missing ones = "partial X not found".

## CI build check (2026-07-29)
`.github/workflows/build-check.yml` runs on every push/PR to `main`: installs the
pinned production Hugo (0.158.0, same binary source as the local repro above) and
builds this theme standalone against the fixture site in `testsite/`, failing the
job on any fatal template error or on "error calling"/`executing "` text leaking
into rendered output.
- **This is a smoke test, not the faithful repro.** No installed plugins, no
  theme-blank — it can't catch a cross-plugin conflict (the actual cause of the
  "Manual full rebuild" incident above). What it DOES catch cheaply, on every
  push, is a template that's fatally broken on its own — the same blast radius
  (home node: page + both feeds), just a different trigger. Use the pinned-0.158
  full-plugin repro above for anything plugin-interaction-shaped.
- `testsite/config.toml`'s `outputFormats` (ArchiveHTML/PhotosHTML/ArchiveJSON)
  are a RECONSTRUCTION from the path/baseName facts recorded elsewhere in this
  file, not micro.blog's actual platform export config — good enough to route
  Hugo's home-node build through `list.archivehtml.html`/`list.photoshtml.html`/
  `list.archivejson.json` so a fatal error in any of them still fails CI, which
  is the point; not a claim that it's byte-identical to production.
- `testsite/` ships its own `layouts/partials/microblog_head.html` stub — this is
  fine and NOT the same violation as committing one inside the theme's own
  `layouts/` (gitignored, see "microblog_head.html" above): `testsite/` is a
  separate fixture site that happens to load this theme, exactly like the
  site-root export used for the manual repro, just checked in instead of
  recreated by hand each time.
- Verified locally before committing: built clean with the pinned
  `~/.local/bin/hugo-0.158` binary, checked actual rendered output (not just
  exit code) — homepage merge/dedup logic, archive/photos grids, and
  `archive/index.json` all confirmed correct. Caught one real fixture bug this
  way: `movie.md` originally used a same-paragraph soft line break between
  title and review, which `plainify` collapses to a space — only an actual
  blank-line paragraph break (two `<p>` tags) reproduces the "review on its own
  line" shape `index.html`'s title/review split depends on.

## Things still outstanding / to watch
- **footer.html** custom footer — VERIFIED rendering live (2026-06-07). micro.blog
  uses OUR custom header/footer partials, not its default. The copyright name now
  links to `/humans.txt` (`rel="author"`); the RSS · Micro.blog · Theme · Codeberg
  links render too. (Since the custom partials ARE used, future header/footer edits
  show up live.)
- **Manual full rebuild** — FIXED & verified in production (stale
  `.Site.Author.avatar` in plugin-search-page's archivejson template). Safe to use.

## Hardening pass (2026-06-10)
- **index.html: guarded `index $statusPosts 0`** — `index` errors on an empty slice,
  and a fault in the home HTML template kills the whole home node (page + feeds),
  same blast radius as the plugin-search-page bug. Now `$status` stays "" when the
  Status category is empty and the card simply doesn't render.
- **index.html: "All …" links derive from the `home_cat_*` params** (`urlize`d) —
  previously hardcoded `/categories/<name>`, which would silently 404 after a
  backend category rename.
- head.html: `about_me` piped through `plainify` before meta tags (it can contain
  HTML); post `meta description` truncated to 160; dropped redundant `| absURL` on
  canonical.
- list.archivejson.json: `feed_url` corrected `photos/` → `archive/` (copy-paste
  from the plugin).
- list.photoshtml.html: photo links got `aria-label` (date) — were `<a><img alt="">`
  with no accessible name.
- main.css: dark-mode `--secondary` Base01 → Base1 (`#93a1a1`) for WCAG AA contrast
  on meta text; removed dead `.media-entry-content`/`.media-shelf-label` rules
  (leftovers from the old content-scraping homepage).
- Uninstalled `plugin-archive-months` + `plugin-photos-months` on micro.blog.

## Currently Reading hardening pass (2026-07-27)
Follow-up to the bookshelf merge above, after profiling the homepage against real
eberle.blog data (218-post archive) and a synthetic 1500-post stress build — see that
section for the perf finding (index.html cost is negligible at real scale; not worth
optimizing further) and the discovery of ~60 duplicate ledger posts (a website/import-side
issue, not fixed here).
- **Capped Currently Reading at `home_reading_count`** (default 8) — it was the one
  homepage section with no limit, on two independent unbounded axes (accumulating
  unfinished started-posts, growing shelves).
- **Cover-image links on Currently Reading, Finished Reading, and Movies got real
  `aria-label`s** instead of duplicating the adjacent title text as their `alt`. The cover
  and title anchors frequently point at different URLs (Micro.blog book page / TMDB vs. the
  post permalink) — pruning the cover link from the accessibility tree (`aria-hidden` +
  `tabindex="-1"`) was considered and rejected, since it would silently remove keyboard/AT
  access to that second, legitimate destination. Movies' label is conditional
  (`$onTMDB`) so it doesn't claim a TMDB destination when the cover actually links back to
  the post.
- **Shelf books with a `cover_url` but no ISBN no longer render a cover.** `coverLink` is
  ISBN-derived; before this pass `$cover` wasn't, so that combination would have produced
  `<img>` wrapped in `<a href="">`.
- Removed `.media-entry-sub` from `main.css`'s shared selector lists — dead since the
  pre-RSS bookshelf-shortcode markup it styled was replaced; the shared rules themselves
  (`.media-entry-date`/`.media-entry-review` etc.) are still live and were kept.

## Finished Reading de-dup + reading-feed guid fix (2026-07-27)
Root-caused the ~60 duplicate posts found during the profiling pass above: `~/git/website`'s
`layouts/reading.rss.xml` built each RSS item's guid from `urn:reading-event:<type>:<slug>:
<event>`, where `<slug>` was the source's **folder name**. Renaming a `content/sources/<key>/`
folder rewrote every guid it had ever emitted, and Micro.blog re-imported any event still
inside the 20-item feed window as if it were new — confirmed empirically against the live
`/archive/`: 45 groups, 60 extra posts, still happening in 2026 (not historical residue).
- **Fixed at the source** (`~/git/website/layouts/reading.rss.xml`): the guid key is now a
  sanitized `isbn`/`doi`/`access_url` — the work's own stable identifier — falling back to
  the folder slug only for the ~2 sources with none of the three (verified: only
  `gardiner2015` actually reaches the feed window; `wyman2010` has no started/finished
  dates so it never emits an item regardless). Renaming a folder is now guid-invisible for
  every source that has an identifier. Verified: built with the feed limit temporarily
  raised to 200, 46 events, zero guid collisions; `scripts/checks/feed-lint.py` clean. Also
  updated that repo's `docs/reading.md`, which had documented the old (now largely fixed)
  rename cost as a blanket warning.
- **Added a de-dup pass on THIS repo's Finished Reading list** (`layouts/index.html`,
  before `$books := first $booksCount ...`) as a safety net regardless of what happens
  upstream — the guid fix prevents NEW duplicates but does nothing for ones already
  imported, and doesn't protect against a different future duplication cause. Same
  ISBN-or-`$key` matching as the Currently Reading merge, applied to `$finishedPosts`
  (newest-first) so the first occurrence of a match — the most recent copy — wins and
  later duplicates are dropped before the `$booksCount` cap runs, so a duplicate can't
  waste a slot that a distinct book should have gotten. Verified against both failure
  modes found on the live site: byte-identical re-imports (same ISBN) and the ISBN-less
  academic case (matches on the `$key` text, since two `doi`/`access_url` imports of the
  same work have no ISBN to key on) — both collapse to one row; a `home_books_count`
  cap test confirmed no cap slot goes to a suppressed duplicate. Confirmed on 0.91.2/0.158/
  0.164.

## Accessibility pass (2026-06-22) — PageSpeed/Lighthouse a11y 93 → target 100
Lighthouse reported 100/100/100 except Accessibility 93. Two flagged audits, both fixed:
- **"Document does not have a main landmark"** (Best Practices) — `baseof.html` wrapped
  content in `<div class="wrapper" id="main-content">`, so the live page had NO `<main>`
  element (this confirms micro.blog renders OUR baseof, not its own — consistent with the
  custom footer/header being used live). Changed that wrapper from `<div>` to `<main>`.
  The CSS selector `.page-content > .wrapper, #main` still matches (class `wrapper` kept),
  and the skip-link target `#main-content` now lands on the `<main>`.
- **"Background and foreground colors do not have a sufficient contrast ratio"** (Contrast)
  — light-mode `--secondary` (Base01 `#586e75`) on the `--entry`/Base2 card background was
  **4.39:1**, just under AA 4.5. Nudged to `#50666d` (4.95:1 on entry, 5.62:1 on bg).
  Verified with the relative-luminance formula, not eyeballed.
- **Latent dark-mode failure fixed too** (not flagged by the light-mode run): `--primary`
  body text (Base0 `#839496`) on `--entry`/Base02 cards was **4.11:1**. Bumped to Base1
  `#93a1a1` (4.86:1 on entry, 5.61:1 on bg). Dark `--primary` and `--secondary` now both
  Base1 — body/meta hierarchy in dark mode leans on size/weight (it was already inverted
  before, meta brighter than body, so nothing real was lost).
- Polish: decorative SVGs in `intro.html` social links got `aria-hidden="true"
  focusable="false"` (the links already carry an `aria-label` + visible text).
- **Header site title is now `<h1>` on the home node** (`header.html`): the homepage
  previously had NO `<h1>` (sections start at `<h2>`). Conditioned on `.IsHome` —
  the only page-level signal available, since `/archive/` and `/photos/` are home-node
  outputs whose `.RelPermalink` is also `/` (VERIFIED: a RelPermalink/IsHome probe
  returns `/`+true for the ArchiveHTML output, so neither distinguishes them from the
  home HTML). Consequence: archive/photos carry the masthead `<h1>` PLUS their own
  `page-title` `<h1>` — two `<h1>`s, but no skipped levels, which Lighthouse/axe allow.
  Content pages (`.IsHome` false) keep the title as an inline `<span>` so the
  article/section heading stays that page's sole top-level `<h1>`. The `<h1>` is
  styled `.site-title-text { font: inherit; margin: 0; letter-spacing: normal }` to
  render identically to the `<span>` (inherits 1rem/700 from `.site-title`).
- **NOT theme-fixable** (platform-side, perf already 100; "diagnostics don't affect score"):
  render-blocking CSS, cache lifetimes (no per-blog response headers — see head.html),
  image delivery (micro.blog CDN), minify CSS/JS + unused CSS (main.css is served as-is
  from `static/`; Hugo's `minifyOutput` only touches generated HTML/feeds, not static
  assets — moving CSS to `assets/` + Hugo Pipes would minify/fingerprint it but is
  unverified on micro.blog's build and unnecessary at a 100 perf score).

## Dark theme removal + palette normalization (2026-07-07)
- **Deleted the `@media (prefers-color-scheme: dark)` block in `main.css`.**
  `~/git/website` (the main site, "Northeaster" palette, `assets/css/site/
  01-tokens.css`) has no dark theme at all — `color-scheme: light` only, no
  dark media query anywhere in its `assets/css/site/*.css`. This theme's dark
  variant was a one-off addition that had drifted from that source of truth;
  removing it also drops one more surface that could silently break on a
  future Hugo bump. Verified live in a browser preview with `prefers-color-
  scheme: dark` emulated + a hard reload — page still renders the light
  palette, confirming no residual dark styling anywhere in the theme (grepped
  the whole repo for "dark" first — `main.css` was the only hit).
- **Normalized the `--fog-*`/`--driftwood`/`--tide*` hex values to match
  `~/git/website`'s `01-tokens.css` exactly**, plus the body background
  gradient's `color-mix` percentage (26% → 28%, matching the main site). The
  theme's copy of this palette had quietly diverged (bluer/darker variants of
  the same named tokens) since it was first ported — same token names, drifted
  values. `--gap`/`--nav-width`/`--content-gap`/`--header-height`/
  `--footer-height` were deliberately NOT synced — those are layout knobs the
  main site's structural CSS files (`10-layout.css` etc.) depend on directly,
  and this theme's homepage grid is intentionally different (see the file
  header comment). Same reasoning for the main site's self-hosted Source
  Serif 4 body font (`03-fonts.css`) — left as this theme's system serif
  stack; swapping would mean shipping additional font files through the
  micro.blog plugin, out of scope for a token/contrast pass. Fraunces
  (headings) was already identical between the two.
- **`--fog-driftgray` (the `--secondary`/meta-text color) was intentionally
  NOT copied verbatim.** The main site's own value (`#667076`) only reaches
  3.9:1 against `--entry`/`#dfe2e1` — this theme uses that color at smaller
  meta-text sizes (dates, kickers, footer links, ~0.74–0.88rem) than the main
  site does, where AA requires 4.5:1, not the 3:1 large-text minimum. Darkened
  to `#5b646a` (4.6:1 on `--entry`, 5.2:1 on `--theme`) — same hue, enough
  margin to survive rounding. Every other shared token (primary, content,
  link, accent) already cleared AA at the main site's own values once ported
  (checked with the relative-luminance formula against both `--theme` and
  `--entry` backgrounds, not eyeballed — smallest margin was link-on-entry at
  6.16:1).
- Verified visually via a throwaway static HTML fixture (not committed) served
  locally and screenshotted through the browser preview tool — not a full
  micro.blog export rebuild, since this was a pure CSS variable change with no
  template/logic touched. Re-run the full pinned-0.158 repro (see "Faithful
  local 0.158 reproduction") if a future change here touches templates.

## Self-hosted Charter body font (2026-08-03)
- **Reverses the 2026-07-07 "system serif stack" decision** (see the palette
  section above) — the user explicitly asked to mirror `~/git/website`'s fonts,
  not just its color tokens, so shipping the font files through the plugin
  moved back into scope.
- Copied `charter-400-latin.woff2`, `charter-400i-latin.woff2`, and
  `charter-LICENSE.txt` from `~/git/website/static/fonts/` into this repo's
  `static/fonts/` (alongside the Fraunces files already there). Same XCharter
  build, same subsetted unicode-range — byte-identical files, not re-exported.
- `main.css` now declares Charter (regular + italic) and a metrics-matched
  `'Charter Fallback'` `@font-face` (Georgia-based `size-adjust`/`ascent-
  override`/`descent-override`), copied verbatim from the main site's
  `03-fonts.css` — same computed values, so no re-derivation needed. Body
  `font-family` updated to `Charter, "Charter Fallback", Georgia, Cambria,
  "Times New Roman", Times, serif`, matching the main site's stack exactly
  (previously: system-only `Charter, "Iowan Old Style", "Palatino Linotype",
  "Book Antiqua", "URW Palladio L", Georgia, serif` — the `Charter` name was
  already there but nothing actually served that face, so it silently always
  fell through to the system fallback).
- `head.html` preloads `fonts/charter-400-latin.woff2` alongside the existing
  Fraunces preload, mirroring `~/git/website`'s `extend_head.html`. Italic
  Charter is not preloaded (the main site only preloads it on pages with an
  above-the-fold `.Description`, which this theme's templates don't set) —
  loads on demand via `font-display: swap` wherever `font-style: italic` is
  used (e.g. Currently Reading title links).
- Fraunces was already self-hosted identically to the main site (same file,
  same fallback metrics) — untouched by this pass.
- Deliberately NOT touched: base `html { font-size }` (106.25% here vs. the
  main site's unset 16px + `body { font-size: 1.125rem }`) and meta-text
  `letter-spacing` (0.03em here vs. 0.015em there). Both are sizing/spacing
  choices this theme's own component rem-values are already tuned around
  (see "Accessibility pass" and the homepage sections above for the values
  those rems assume) — changing the base would cascade through every
  rem-sized rule in the file for a cosmetic delta, not a font-identity one.
  Revisit only if a future pass is specifically about matching those metrics
  too, not as a side effect of a font-swap.
- Verified with the pinned-0.158 CI-style build (this repo's theme loaded
  standalone against `testsite/`, per the "CI build check" section): build
  clean, `static/fonts/charter-*.woff2` present in output, preload `<link>`
  and `@font-face` `src` both resolve to `fonts/charter-400-latin.woff2`.

## Mobile-first responsive rewrite (2026-08-03)
Follow-up to a responsive-sizing review (root sizing, breakpoints, tap targets)
that found the CSS was desktop-first with `px` breakpoints and `px` layout
tokens — not broken, but not current best practice either.
- **`--gap`/`--nav-width`/`--main-width`/`--radius` converted `px` → `rem`**
  (same numbers, divided by 16: `24px→1.5rem`, `1080px→67.5rem`,
  `700px→43.75rem`, `10px→0.625rem`). This is NOT a sync to `~/git/website`'s
  own rem values (still deliberately different — see the "Dark theme removal"
  section above) — only the unit changed, so these now scale with
  `html { font-size }` (100%/106.25%, see below) exactly like the type scale
  already does. Before this, a reader bumping their root text-size preference
  got bigger type in a layout column that stayed pixel-fixed — the measure
  benefit of a wider column doesn't materialize if the column itself can't
  grow.
- **Every `@media (max-width: ...px)` block rewritten mobile-first**
  (`@media (min-width: ...em)`, narrow-viewport values promoted to the
  unprefixed base rule). Breakpoints converted at a 16px reference
  (`560px→35em`, `720px→45em`, `900px→56.25em`) — deliberately NOT re-derived
  from the new rem tokens, since media-query length units resolve against the
  browser's initial font-size (spec-defined ~16px), not the page's actual
  root size, so `em` there and `rem` in layout tokens are solving two
  different problems (breakpoints shift with root-size preference; layout
  dimensions scale with it) that happen to share a unit family.
  **`html`'s own `font-size` (100%/106.25%) is itself now mobile-first** —
  base is 100%, `@media (min-width: 35em)` promotes to 106.25% — so the root
  scale itself follows the same pattern as everything depending on it.
  Verified byte-for-byte equivalent at every documented breakpoint by tracing
  each overridden property's mobile/tablet/desktop value from the OLD
  desktop-first cascade before rewriting (the footer grid has three tiers —
  mobile/≤900 tablet/>900 desktop — each needed explicit values in two
  `min-width` blocks, not one, since `justify-self` differs at all three).
  No browser available in-session to screenshot-diff; verification was build
  success (pinned 0.158) + brace-balance check + manual value tracing, not a
  pixel comparison — re-verify visually in a real browser before relying on
  this for a visually load-bearing change.
- **`.intro-social a` padding bumped `4px 9px` → `0.45rem 0.65rem`** — the
  pill was ~25px tall against WCAG 2.5.5's 24px minimum target size, clearing
  it by only ~1px. Everywhere else these are the theme's only non-exempt
  small tap targets (`.pagination`/`.footer-link-list`/`.site-nav` links are
  inline text-flow links, which 2.5.5 exempts).

## Contrast pass (2026-08-03)
Follow-up to a full WCAG relative-luminance audit of every color pairing
actually used in `main.css` (including composited `color-mix()` backgrounds,
not just the raw tokens) — found one token with no headroom and one
component with no visible boundary at all.
- **`--fog-driftgray` (`--secondary`, meta text) darkened `#5b646a` →
  `#4c545a`.** The old value cleared AA (4.5:1) on `--entry` by only 0.13
  (4.63:1) — no margin for rounding or a different renderer — despite
  already being one AA-driven darkening past the main site's own value (see
  "Dark theme removal" above). New value: 5.91:1 on `--entry` / 6.70:1 on
  `--theme`, real headroom, short of AAA (7:1) but close.
- **Added a `prefers-contrast: more` block**, mirroring `~/git/website`'s
  `01-tokens.css` (`--content:#262f34`, `--secondary:#3f464b`, `--link`/
  `--accent: var(--tide-deep)`) — light-mode only, since this theme has no
  dark palette. Verified those exact hex values are safe to reuse: this
  theme's `--theme`/`--entry` backgrounds are byte-identical to the main
  site's, so the contrast math the main site already validated carries over
  unchanged.
- **`.intro-social a` border swapped `var(--border)` → `color-mix(in srgb,
  var(--secondary), transparent 20%)`.** `--border` against the page was
  ~1.3:1 — the pill's boundary was effectively invisible, relying entirely on
  its faint fill (`color-mix(theme, white 22%)`, itself only ~1.04:1 against
  the page) and inter-chip spacing to read as a discrete tappable shape. New
  border resolves to ~4.17:1, clearing WCAG 1.4.11's 3:1 non-text/UI-
  component target with margin.
- Verified with the pinned-0.158 build + a standalone Python re-derivation of
  every ratio above (relative-luminance formula, not eyeballed) against the
  final token values. No browser available in-session for a live contrast
  checker cross-check.

## LANDMINE: deleted RSS-import posts come back (diagnosed 2026-08-05)
**Micro.blog re-creates any feed item it cannot find a post for.** Deleting an
imported post does NOT tell the importer to forget it — on the next poll the item
is still in the feed, there is no matching post, so it is imported again. A
deletion only sticks once the item has aged out of the feed window.

**Dedup is on `<link>`, NOT `<guid>`** (documented in `~/git/website`'s
`layouts/reading.rss.xml` header, found when a started+finished pair sharing one
link silently dropped the second). This is why the 2026-07 guid fix was necessary
but not sufficient: **a published `<link>` must be treated as immutable.** Any
change to it — a URL-scheme change, a folder rename for a source with no
isbn/doi/access_url, adding or removing a `#started`/`#finished` suffix — creates
a NEW post for every affected item then inside the window.

**State on 2026-08-05:** 8 works duplicated, **15 extra posts**, all 2012-2015
`finished` events (down from 45 groups / 60 extras in the 2026-07 cleanup — so
that cleanup mostly held, and these are the ones that returned).

**The slug generations are the fingerprint of how many times each was imported.**
Micro.blog cannot reuse a slug, so each re-import falls back further:
`000000.html`/`010000.html` (untitled post at midnight — the oldest import) →
6-char hex `ae5528.html` (collision fallback) → `finished-reading-<title>.html`
(newest scheme). Three slug styles for one book = three separate imports at three
different times, which lines up with the ledger's URL-scheme changes (cite-key →
`/sources/` taxonomy in b8fce17, then the `#started`/`#finished` suffix work in
d060262/9cc9c99).

**Safe to delete now:** all 8 works are OUTSIDE the current 20-item window, which
spans **2025-01-05 → 2026-08-01** (checked against the live
`jaredeberle.org/reading/index.xml`). Nothing in the feed can resurrect them.
- **Before deleting any future duplicate, check whether its item is in the
  current 20.** If it is, deletion will not stick — fix the link first, or wait
  for it to age out. This is the check that was missing.
- Keep the title-slug copy where one exists; it is the newest import and the only
  one with a readable URL.

**Prevention (not yet implemented, `~/git/website` is a separate repo):** commit a
snapshot of every `<link>` the feed has emitted and have
`scripts/checks/feed-lint.py` fail when a previously-published link changes or
disappears while still inside the window. The guid is already stable; the link is
the one that actually controls duplication and nothing currently guards it.

**Theme-side exposure:** `index.html`'s Finished Reading de-dup (2026-07-27) hides
these on the homepage, but `/archive/`, `/search/` and the feeds all still show
every copy — the theme can only paper over this, not fix it.

## plugin-bookgoals absorbed into the theme (2026-08-05)
Absorbed `microdotblog/plugin-bookgoals` — the per-year finished-books grids on
`/reading/`. `layouts/shortcodes/bookgoals.html`, same call signature
(`{{< bookgoals 2026 >}}`, `{{< bookgoals progress >}}`), so content needs no
edit. **The plugin MUST be uninstalled for ours to take effect** — see the
correction under the bookshelf section below; an installed plugin's shortcode
beats the theme's on micro.blog.

**Only `bookgoals` was reproduced. `bookcalendar` was deliberately NOT** — it is
unused here and pins versioned micro.blog assets (`calendar.css?v=20260710.5`,
`calendar.js?v=20260711.1`) that only an upstream plugin update can refresh. If
the month-by-month calendar view is ever wanted, reinstall the plugin rather than
copying that shortcode in; it is also undocumented (absent from the plugin's
README and plugin.json), so treat it as unsupported.

**The case for absorbing was two markup defects that CSS cannot reach**
(measured on the live page, not assumed):
- **No lazy loading at all.** `/reading/` carries **44 covers averaging ~38 KB —
  about 1 MB fetched eagerly**, essentially all below the fold. `loading` can
  only be set in markup.
- **`width="100" height="120"` on every cover — a 0.833 ratio that is wrong for
  all of them.** Sampled real covers: 0.667, 0.667, 0.667, 0.737, 0.657. With
  `height: auto` the browser reserved a wrong-shaped box and reflowed on load,
  44 times. Replaced with CSS `aspect-ratio: 2/3` + `object-fit: cover`,
  matching `.media-cover` / `.bookshelf-cover`.

Other changes:
- **Every cover is lazy here, unlike `bookshelf.html` which leaves its first
  eager.** A year-in-review grid is 20-40 covers deep and never the LCP element;
  on `/reading/` it sits below the Currently Reading shelf. Revisit only if a
  page ever opens with this shortcode as its first content.
- **`alt` keeps the book title here** — the anchor wraps only the image, so the
  alt IS the link's accessible name. This is the opposite of the `alt=""` +
  `aria-label` pattern used in `index.html` and `bookshelf.html`, where a visible
  title sits beside the cover and alt text would double-announce. Both are
  correct; the difference is whether adjacent text already names the link.
- Class is `bookgoals-cover`, not the plugin's `cover`, so its stylesheet cannot
  reach our markup while both are installed. **This retires the `max-width: none`
  workaround** that existed only to defeat its `.bookgoals .cover
  { max-width: 100px }`, which had been silently clamping the rem width set in
  the units audit.
- Books with no `cover_url` are skipped; a book with no `post_url` renders as a
  bare image rather than `<a href="">`. A bare `{{< bookgoals >}}` now defaults to
  the current year (upstream rendered nothing).
- **DE-DUPED by normalized title, added 2026-08-05, strengthened the same day.**
  Micro.blog's goal data lists the same WORK twice when two editions have been
  recorded. Verified live: 6 repeated titles across 2025/2026, **every pair with
  two different but adjacent ISBNs** (Ghosts of Crook County as 9780807012994 and
  9780807007372; Train Dreams as 9781250007650 and 9781429995207; etc.) — so no
  ISBN in either year actually repeats. **This is platform data, NOT residue from
  the RSS-import duplicates**, which is why deleting those posts and running a
  full rebuild changed nothing here. Title is the only usable key precisely
  because the ISBNs differ; the accepted trade is that two genuinely different
  books sharing a title AND author would collapse. The real fix is removing the
  duplicate edition from the year's goal in Micro.blog — this is a display-level
  safety net, the same role the Finished Reading de-dup plays in `index.html`.
  - **An exact title match was NOT enough** — the first version caught nothing in
    production. The two records of a work rarely share a title string: live 2026
    had "The Blood Countess: Murder, Betrayal, and the Making of a Monster" vs
    "The Blood Countess", "Blood in Winter" vs "The Blood in Winter", "Hated by
    All the Right People: Tucker Carlson…" vs the bare title. The key now strips
    the subtitle after a colon, a leading article, and punctuation.
  - **Volume suffixes are deliberately NOT stripped.** It would merge
    "Chronicles Vol. 1" with "Chronicles Vol. 2", and hiding a distinct volume is
    worse than showing one duplicate. Cost: "Chronicles" / "Chronicles Vol. 1",
    a real pair in the 2026 goal, still renders twice — fix that one in
    Micro.blog.
  - **Author is a TIE-BREAKER, not part of the key.** A hard `title|author` key
    was the first version and matched nothing — it only takes ONE record with the
    field blank for a pair to miss. Dropping author entirely was the second, and
    over-corrected. Current rule: same normalized title merges UNLESS both
    records carry an author and they disagree. Missing metadata no longer blocks
    a merge; conflicting metadata still prevents one, so two different books that
    happen to share a title stay apart. `author` IS a documented field
    (help.micro.blog/t/bookshelves/515), so it is worth using — just not as a
    requirement.

### Where the duplicate book records actually come from
The goals page has no editor — a goal is DERIVED from Micro.blog's book records,
so there is nothing to de-duplicate in the UI, which is why the CSV export and
the currently-reading shelf both look clean while the goal grid does not. The
duplicates are two separate BOOK RECORDS for one work, each with its own ISBN.

**Root cause, confirmed by ISBN (2026-08-05):** `~/git/website`'s reading feed
emits `https://micro.blog/books/<isbn>` using the `isbn` in that source's front
matter, and Micro.blog associates an imported post with a book by that link. When
the ledger's ISBN names a DIFFERENT EDITION than the record Micro.blog already
holds, a second book record is created and both land in the year's goal:

| work | ledger ISBN (feed guid) | Micro.blog record ISBN |
|---|---|---|
| Puhak, *The Blood Countess* | 9781639732159 | 9781639732166 |

Same book, adjacent ISBNs, two records. That also explains the title variance the
de-dup has to cope with: the ledger carries the full title with subtitle, the
Micro.blog record the short one.

**Durable fix is source-side and in your control:** set each `content/sources/*`
`isbn` to the edition Micro.blog already tracks, and no new pair can form. Worth
doing before adding a book to the ledger, since correcting it afterwards changes
the feed `<link>` only if the source folder moves — the ISBN itself is not part
of the link, so an ISBN correction is safe (it changes the guid, but Micro.blog
dedupes on link; see the link-immutability section).

**Micropub is the formal path and the RSS import cannot use it.**
help.micro.blog/t/books-books-books/1424 documents `read-of` with `name` + `uid`
as how a client states "this post is about THIS book". An RSS import has no such
channel, so association falls back to the ISBN link in the body — which is why
the ISBN has to be right. If duplicates keep appearing despite matching ISBNs,
posting via Micropub with `read-of` instead of the RSS import is the next lever.
- **Fixtures:** `testsite/data/bookgoals.json` (two years, a coverless book, a
  book with no post_url, two editions of one work, and two same-title books by
  different authors) and four more sections in `testsite/content/reading.md`. Verified in the build: 3 covers render, all lazy
  + `decoding="async"`, no `width`/`height` attributes, coverless book skipped,
  unlinked book has no empty anchor, `progress` renders "12 of 30", an unknown
  year renders nothing. `/reading/` heading levels still have no skips.

## wayback-link-preserver breaks flex layouts (diagnosed 2026-08-06)
The ragged first row of `/reading/`'s 2026 bookgoals grid was NOT a cover or a
CSS problem — every cover returns 200 and renders at an identical
`6.25rem × aspect-ratio 2/3` box. The plugin injects its badge as a **SIBLING**
of the link it flags:
```js
link.parentNode.insertBefore(badge, link.nextSibling);   // <span class=wlp-broken-badge>
```
`.bookgoals` is `display: flex` and `.bookgoals-link` is a direct child, so the
badge becomes **a flex item** — ~16px plus the 0.6rem gap — shifting the rest of
that row off the 117px column pitch every other row uses. Fixed with
`.bookgoals .wlp-broken-badge, .bookgoals .wlp-indicator { display: none }`
(0,2,0 beats the plugin's 0,1,0, which is required because micro.blog loads
plugin CSS after `main.css`). **Scoped to `.bookgoals` deliberately** — in
`.bookshelf` the badge lands inside the `<h3>` beside real link text, where it
is inline, useful and harmless.
- **The flag was a false positive**, and this is the general risk: the plugin
  judges liveness with a `mode: "no-cors"` fetch on an 8s timeout, so one slow
  response reads as dead, and the verdict is cached in `localStorage` for a day
  (`livenessCacheDays: 1`). It flagged `micro.blog/books/9781639732159`, which
  returns 200.
- **This class of bug is INVISIBLE to `curl`.** The badge is injected at
  runtime, so fetched HTML looks perfect — the screenshot was the only evidence.
  Same caveat already recorded for `.microblog_reply_form` in the dead-code
  audit.
- `contentSelector` is `.post-content, .e-content, article .content,
  .h-entry .e-content`, so ANY shortcode output inside a post body is in scope.
  Assume the same hazard for any future flex/grid container holding links.
- `maxLinksPerPage: 30` explains why only 2026 was affected: `/reading/` has 35
  links (31 bookgoals + 4 bookshelf), so the plugin stops partway through the
  first grid and never examines 2025.

## bookshelf shortcode absorbed into the theme (2026-08-05)
Absorbed `kottkrig/microdotblog-bookshelf-shortcode` so it can be uninstalled.
It drives exactly one thing on the live site: the **"Currently Reading" block on
`/reading/`** (the per-year sections below it are `plugin-bookgoals`, which
stays). Note the homepage's Currently Reading is NOT this — that is
`index.html`'s own merge of started-reading posts + the same shelf data, which is
why the homepage shows one more book than `/reading/` does.

- **`layouts/shortcodes/bookshelf.html` — call signature is IDENTICAL**, so
  existing content needs no edit: positional `{{< bookshelf "shelf" >}}`, named
  `shelf=`, and `variant="list"|"grid"`, same `currentlyreading`/`list` defaults.
- **micro.blog RE-INSTALLS a plugin whose shortcode your content calls
  (2026-08-05).** Uninstalling `plugin-bookgoals` and reloading the Plugins page
  put it straight back, repeatedly, while `/reading/` still contained
  `{{< bookgoals 2026 >}}`. That is coherent platform behaviour — an unknown
  shortcode is a FATAL Hugo error, so the platform reinstates whatever provides
  the name. Combined with the next point (an installed plugin's shortcode wins),
  absorbing a shortcode under the plugin's own name can never take effect.
  - **Fix: rename, don't fight.** `layouts/shortcodes/readinggoals.html` is the
    same output under a name nothing owns, so there is no plugin to reinstate
    and nothing to shadow it. **`/reading/` content must be edited to call
    `{{< readinggoals 2026 >}}` / `{{< readinggoals progress >}}`** — that
    content lives on micro.blog, not in this repo, so it is a manual step.
  - `shortcodes/bookgoals.html` is kept as a fallback for the day the plugin is
    genuinely gone. Both are thin callers over `partials/reading-goals.html`, so
    the logic lives once; a `testsite` fixture asserts both names render
    byte-identically.
- **CORRECTED 2026-08-05 — an installed PLUGIN's shortcode BEATS the theme's.**
  The original claim here ("leftmost theme wins, so ours shadows the plugin
  before it is uninstalled, no transition window") was extrapolated from a local
  0.158 test with a throwaway second theme. Production disproves it: with the
  bookshelf plugin uninstalled OUR bookshelf renders, while with plugin-bookgoals
  still installed ITS shortcode renders (`class=cover` and `width="100"
  height="120"` in the live HTML, no `bookgoals-cover`, no `loading="lazy"`) —
  both shortcodes deployed on origin/main at the time. So micro.blog does not
  order `--theme` the way the local repro assumed.
  - **Consequence: absorbing a shortcode does nothing until the plugin is
    uninstalled**, and there IS a transition window — during it the theme's CSS
    no longer targets the plugin's class names (deliberately renamed to avoid
    tie-losses), so the plugin's output renders unstyled by us. Uninstall
    promptly rather than running both.
  - The same caution applies to the static-file ordering test in the robots.txt
    section: local `--theme` ordering results have now been wrong twice about
    production. Treat them as suggestive, not decisive.
  - Note what made this confusing to diagnose: the plugin kept re-installing
    itself, so "I uninstalled it and the plugin's markup is still rendering"
    looked like a stale build when it was actually a live, re-installed plugin.
- **Class names are `bookshelf-*` (single dash), NOT the plugin's `bookshelf__*`.**
  Deliberate: micro.blog loads plugin CSS AFTER `main.css`, so any rule sharing
  the plugin's selectors loses every specificity tie — that is exactly why this
  theme's previous `bookshelf__*` overrides never applied (see the dead-code
  audit). Different names sidestep the ordering problem entirely. Don't
  reintroduce the BEM names.
- **The visible defect that prompted this:** the plugin's titles are `<h3>`, so
  `.post-content h2, h3 { border-bottom }` drew a full-width rule through every
  book title, running past the text and colliding with the covers. `.post-content
  .bookshelf-title` (0,2,0, beats the 0,1,1 heading rule) resets border/margin —
  a book title is a row label, not a section break. Headings stay `h3` so the
  page outline is unchanged: verified `/reading/` renders `h1,h2,h3,h3,h2,h3,…`
  with **no level skips**.
- Other fixes over the original: dropped `title="<title> by <author>"` from each
  row (a tooltip duplicating visible text; `title` is not an accessibility
  feature — it is what shows in the screenshot that prompted this); covers get
  `alt=""` + an `aria-label` on the link, since cover and title point at the SAME
  URL and would otherwise announce twice; a book with no ISBN renders with no
  cover instead of `<a href="">` (same rule `index.html` already applies);
  `loading="lazy"` on every cover but the first (the shelf is top-of-page, so the
  first is an LCP candidate); an unknown `variant` **warns and falls back** where
  the original called `errorf`, which is FATAL — a typo in a post would have
  failed the whole build.
- **Two columns at >=45em (2026-08-05).** A row is cover + meta, so one column
  left a lot of empty measure right of the author line; pairing them halves the
  vertical run of a 4-6 book shelf without shrinking covers. The `:last-child`
  closing rule is dropped in two-column mode on purpose — the last item is only
  ever half of the final row, so it would underline one column and not the other.
- **Regression fixtures:** `testsite/content/reading.md` exercises all three
  paths (default list, `variant="grid"`, invalid variant), and
  `testsite/data/bookshelves.json` gained a second `currentlyreading` entry with
  an empty ISBN plus a `read2026` shelf. Verified in the build: correct markup for
  all three, the no-ISBN book renders coverless with a plain (unlinked) title, and
  the bad variant logs the warning and renders as a list. **CI will print
  `WARN bookshelf: unknown variant "nonsense"` on every run — that is the
  assertion, not a problem.** It does not fail the build (build-check.yml only
  fails on fatal errors and leaked error text); the fixture carries a comment
  saying so.

### `/reading/` Currently Reading: divergence from the homepage accepted, not fixed (2026-08-06)
The homepage's Currently Reading merges started-reading POSTS with the
Micro.blog shelf (see the "Currently Reading" homepage section above);
`bookshelf.html` on `/reading/` only ever read the shelf. That gap surfaced
when an RSS-imported `Started reading:` post (not on the backend shelf) showed
on the homepage but not on `/reading/`. Porting the post-merge logic into
`bookshelf.html` was offered and **declined** — assessed as an added breakage
point not worth it for this page. Instead: **the `{{< bookshelf >}}` /
`{{< readinggoals >}}` call is being removed from the `/reading/` post content
in the Micro.blog backend** (not tracked in this repo), leaving that page as a
static historical record.
- **The `.bookshelf-*` CSS block in `main.css` was removed the same day**
  (~130 lines, was at `main.css:366-497`) since `/reading/` was its only
  caller anywhere in this repo (`testsite/content/reading.md` was the only
  fixture invoking the shortcode). Recoverable from git history.
- **`layouts/shortcodes/bookshelf.html` itself was deliberately NOT deleted**
  — kept available for any future page that wants a shelf embed. If it's ever
  called again, it will render unstyled until the CSS comes back.
- **`testsite/content/reading.md`'s bookshelf-shortcode coverage was left
  in place** (not part of this change) — it still exercises the shortcode
  template directly, independent of whatever the live `/reading/` post says.

## plugin-search-page absorbed into the theme (2026-08-05)
**The reason is the landmine, not the feature.** That plugin also shipped
`layouts/list.archivejson.json` using `.Site.Author.avatar` (removed in Hugo
0.156) — the exact template that killed the home node (page + RSS + JSON) on a
full rebuild in June 2026, still unfixed upstream two months after we reported
it. Uninstalling removes it from the build entirely, which is a stronger
guarantee than shadowing it — and see the CORRECTION above: our shadowing was
probably never winning anyway.

**Reviewed the other four plugins at the same time; all four stay external.**
YouTube No-Cookie (731-line shortcode, actively maintained) and Wayback Link
Preserver (486 lines of JS doing live Wayback API calls) are real software.
Book reading goals is only 27 lines, but its `bookcalendar` shortcode pulls
`micro.blog/css/calendar.css?v=20260710.5` and `js/calendar.js?v=20260711.1` —
version strings micro.blog bumps, which we would then hand-track. Bookshelf
shortcode is 27 lines over `.Site.Data.bookshelves`, data `index.html` already
reads, so it is the easy one — but absorbing adds another `.Site.Data` call site
to the deprecation landmine for no user-visible gain. Reconsider only if you want
the cover-grid layout on `/reading/` that we deleted; owning the shortcode is the
clean way to get it, instead of losing specificity ties to the plugin's CSS.

**What was absorbed, and what changed:**
- `content/search.md` — the page, its `/search/` URL and its `menu: main` nav
  entry. See the "Removed content/ directory" note above: a theme's `content/` IS
  merged, so this works the same way the plugin's did.
- `static/js/search.js` — the logic, moved out of an inline `<script>` in the
  markdown and into the theme's only owned JS file. `static/css/main.css` gained a
  Search page section, replacing the plugin's inline `<style>` (hardcoded `#eee`
  borders, px sizes, a fixed 270px field).
- **KEEP `layouts/list.archivejson.json`.** Search fetches `/archive/index.json`
  and needs the full-text `.Plain` body; that template is now load-bearing for a
  feature, not just a shadow of the plugin's broken copy.
- Fixes over the original: a real `<label>` (it had none — placeholder-only, which
  fails WCAG 1.3.1/4.1.2); rows built with DOM nodes instead of `innerHTML`
  (post text was being re-parsed as markup); `input` listeners instead of inline
  `onChange`, so it searches as you type rather than only on blur/Enter; a `catch`
  on the fetch (a failure previously left "Loading posts..." on screen forever);
  untitled posts fall back to their date for link text instead of rendering an
  empty anchor; `?q=` uses `replaceState` so search doesn't spam history; a
  `<noscript>` pointing at `/archive/`.
- `_default/single.html` now drops the whole `.post-meta` line when `.Date.IsZero`
  rather than half-rendering it. `/search/` has no date, so the old code showed a
  bare "1 min read"; the live plugin page showed **"January 1, 0001"** — a real,
  currently-visible defect that the zero-date fix in the bug sweep resolves.
- **Verified functionally, not just built:** 15 assertions against the rendered
  page in a real DOM (jsdom) — label association, AND-matching across title+body,
  status counts, `?q=` write and restore-on-load, empty/no-match states, invalid
  dates, snippet truncation, failed-fetch error path, and that hostile markup in
  post text is escaped rather than parsed. All pass. The harness was scratch, not
  committed; CI has no JS test infra.

## plugin-cc absorbed into the theme (2026-08-05)
`microdotblog/plugin-cc`'s entire payload was one partial —
`<link rel="license" href="{{ .Site.Params.cc_license_url }}">` — injected into
`<head>` via its `plugin.json` `"includes"`, with a single backend field and a
CC BY 4.0 default. All of that now lives here:
- `head.html` emits the tag next to `rel="canonical"` / `rel="author"`.
- `config.json` carries the same default; `plugin.json` exposes the same
  `params.cc_license_url` field, so **a value already set in plugin-cc's backend
  field carries over to ours** — same param name, no migration.
- **UNINSTALL plugin-cc.** With both installed the page emits `rel="license"`
  twice. Live value was the CC BY 4.0 default on every page (checked before the
  change), so behavior is identical after removal.
- **Two deliberate improvements over the plugin:**
  1. Wrapped in `{{ with }}` — the plugin was not, so blanking its field emitted
     `href=""`. Blank now omits the tag. Verified both ways in the build.
  2. `license` added to the JSON-LD `WebSite` and `BlogPosting` nodes from the
     same param (also `with`-guarded, so a blank field omits the key rather than
     publishing an empty string). This goes BEYOND plugin-cc, which only ever
     emitted the link tag — delete those two merges if exact parity is wanted.
- Also corrected `plugin.json`'s `description`, which still read "A clean
  Solarized Light theme" — stale since the Northeaster palette port, and
  user-visible in micro.blog's plugin listing.

## robots.txt + security.txt now served from the theme (2026-08-05)

### PLATFORM RULE: static/ fills a gap, layouts/ overrides a default
Learned the hard way on 2026-08-05 — `robots.txt` shipped in `static/` first and
served **nothing** in production:
- **micro.blog serves a theme/plugin `static/` file only where the platform has
  NO default for that path.** `css/main.css`, `fonts/`, `humans.txt` and
  `.well-known/security.txt` all work this way (security.txt confirmed 200 live,
  which also settles that dot-paths are served).
- **Where the platform DOES ship a default — `robots.txt` — a `static/` copy
  never wins.** The default keeps being served. Only `layouts/robots.txt`
  overrides it, because micro.blog has Hugo's robots.txt generation enabled and
  that template is what renders the file. This is also why the AI-blocking
  plugin worked where our static file didn't: it used `layouts/`.
- **A local Hugo test is NOT sufficient evidence for this class of question.**
  Locally, a theme's `static/robots.txt` DOES beat Hugo's generated one (verified
  on pinned 0.158 with `enableRobotsTXT = true`) — the exact opposite of what the
  platform does. The local result was real and still misleading. Treat
  "which file wins at a path the platform also owns" as answerable only in
  production.
- `testsite/config.toml` now sets `enableRobotsTXT = true` so CI actually renders
  `layouts/robots.txt`; without it the template silently produced nothing and a
  move back to `static/` would have been invisible.
- `layouts/robots.txt` is a Hugo TEMPLATE, so Go delimiters are live even inside
  its `#` comment lines. Writing a literal pair of double braces there fails the
  build with "missing value for command" (done, once, while documenting this).

### layouts/robots.txt — replaces the AI-blocking plugin
- Among themes, **the leftmost `--theme` entry wins** (tested both orderings with
  a throwaway second theme; the winner flipped with the order). micro.blog loads
  this theme first, then plugins, then theme-blank — so this file wins over a
  plugin's copy.
- Content: the old plugin blocked only `GPTBot` + `ChatGPT-User`. The replacement
  keeps that intent and extends it to ~28 agents across OpenAI, Anthropic,
  Perplexity, Meta, Common Crawl, Amazon, ByteDance, Cohere, Diffbot, You.com and
  the image-scraper bots, plus the `Google-Extended` / `Applebot-Extended`
  training opt-outs (which do NOT affect Googlebot/Applebot search indexing).
  Ordinary crawlers stay fully allowed and a `Sitemap:` line was added — the
  plugin's file had none.
- **Training vs. retrieval is deliberately NOT split.** `OAI-SearchBot`,
  `Claude-SearchBot`, `Perplexity-User`, `DuckAssistBot` etc. are user-initiated
  retrieval, and blocking them removes the site from AI search answers where it
  would otherwise be cited. Both categories are blocked here because the plugin
  being replaced already blocked `ChatGPT-User` (retrieval) alongside `GPTBot`
  (training). Unblock individual agents if that trade isn't wanted.
- **Deploy order:** push the theme, confirm `/robots.txt` serves this content,
  THEN uninstall the AI-blocking plugin, then re-check. No unprotected window in
  either outcome. **Confirmed working in production from `layouts/` (2026-08-05)
  after the static/ version served nothing.**
- llms.txt is intentionally NOT added: the point of llms.txt is to help LLM
  crawlers, which this file blocks.

### static/.well-known/security.txt
Based on `~/git/website`'s copy. Hugo does copy the dot-directory into `public/`
(verified). **Differences from the original, both deliberate:**
- Adds `Canonical: https://eberle.blog/.well-known/security.txt` ahead of the
  jaredeberle.org one. RFC 9116 allows multiple Canonical fields, and a file whose
  Canonical doesn't include where it was retrieved from "should not be trusted"
  (§2.5.2) — so a verbatim copy would have been self-invalidating here.
- **Not PGP-signed.** The original is clearsigned; the signature covers exact
  bytes, so adding the Canonical line necessarily breaks it. The file carries the
  `gpg --clearsign` command to re-sign in place — that needs the key, so it is the
  user's step, not something to fake.
- `Expires: 2027-05-26` is carried over unchanged so both copies expire together.
  **An expired security.txt is treated as invalid** — refresh both at once.
- Whether micro.blog serves a dot-path at all is UNVERIFIED until deployed. Check
  `https://eberle.blog/.well-known/security.txt` after the push.

## "Currently reading:" posts now reach Currently Reading (fixed 2026-08-05)
A real live post, `currently-reading-the-night-manager.html`, is tagged **only**
`['Books']` and opens `Currently reading: The Night Manager by John le Carré 📚`.
The started-reading detection accepted only the `Started Reading` category or
`(?i)^Started reading:`, so it matched **neither** and a book actively being read
never appeared in the Currently Reading section.
- **Two edits, and they MUST stay in sync**: the detector is now
  `(?i)^(Started|Currently) reading:`, and the `$label` prefix strip is now
  `(?i)^(started|currently|finished) reading:`. Widening only the detector would
  add the row but leave "Currently reading:" in the visible label AND produce a
  `$key` no "Finished reading:" post can match — so it would never retire.
  Comments at both sites point at each other.
- **Regression fixtures added** to `testsite/content/post/`: `currently-active.md`
  (Books-only, "Currently reading:" — the previously invisible shape),
  `currently-done.md` + `currently-done-finished.md` (proves the pair still
  retires through the normalized title/author key). Verified in the build: the new
  row renders as "Night Manager Fixture by Fixture Author" with no verb prefix,
  and the retired one is absent.

## Final bug sweep (2026-08-05)
Ran after the four audits below. Method: pinned-0.158 build of `testsite/`, then
every generated page parsed with html5lib (structure, duplicate ids, heading
order), every `application/ld+json` block parsed as JSON, and a scan for
template-artifact strings (`error calling`, `executing "`, `<no value>`,
`ZgotmplZ`, `&lt;nil&gt;`, empty `href`/`src`/`aria-label`, `0001`). Added a
throwaway title-less, date-less page fixture to probe the edge case, then removed
it.

**Three bugs found and fixed:**
1. **Zero-date leak, mine.** The new untitled-page `<h1>` fallback used
   `.Date.Format` unguarded, so a page with no date in front matter rendered
   `<h1>January 1, 0001</h1>` — and the same zero time in `_default/single.html`'s
   `<time datetime>` and the `<article aria-label>`. All date-derived strings in
   that template are now gated on `.Date.IsZero`, with `.Site.Title` as the
   last-resort label. Posts are unaffected (micro.blog permalinks are
   date-derived), but the same guard was added to `post/single.html` for safety.
2. **Zero-date leak, pre-existing.** `head.html` emitted
   `article:published_time` / `article:modified_time` as
   `content="0001-01-01T00:00:00Z"` on any dateless page — worse than omitting
   them, since consumers read it as a real date. Now gated on
   `and .IsPage (not .Date.IsZero)`.
3. **`{{ else if }}` is not valid after `{{ with }}`** on this Go/Hugo version —
   `unexpected <if> in input`, a FATAL build error, caught by the pinned-0.158
   build. Rewritten with a `$label` variable. Worth remembering: this is exactly
   the class of fault that kills the whole home node in production.

**Clean:** zero html5lib parse errors, zero duplicate ids, **zero heading-level
skips**, and every page has an `<h1>` except Hugo's own `page/1/` pagination
alias stubs (meta-refresh redirects, not theme output). JSON-LD parses on every
page. All 19 spot-checks of this session's changes verified in rendered output.

**Known consequence recorded, not a bug:** the measure cap exempts paragraphs
containing an image, and micro.blog puts the caption in the SAME `<p>` as the
image (verified on the live 2026-02-16 post: `<p><img ...>\ncaption`), so those
captions run the full column instead of 60ch. Accepted trade — the alternative
is every photo losing a quarter of its width. Noted in `main.css`.

**Content-side finding (not theme-fixable):** **13 of 14 photo posts on the live
site have no alt text** on their body image (`<img src=... alt>`). The 22 book
covers in the recent feed are platform-injected and decorative, so their empty
alt is correct — this is specifically the user-authored photos. micro.blog's
editor supports alt text; nothing in the theme can supply it.

## Dead code audit (2026-08-05)
Method: extracted every class/id selector in `main.css` and diffed against (a) the
classes the templates emit and (b) the classes actually present in **live**
eberle.blog HTML (home, archive, photos, replies, a post, a category page,
/about/, /reading/, /search/) — the live side matters because micro.blog injects
markup and plugins render their own. Also diffed template `.Site.Params.*` reads
against `config.json` + `plugin.json`. CSS classes went 98 → 87.

**Removed (verified dead, zero visual change):**
- `.page-header`, `.post-kicker`, `.post-kicker-sep` (+ `.post-kicker` in the
  shared meta-typography selector list) — emitted by no template and present in no
  live page.
- `.list` in the print block — my own import error from `~/git/website`'s
  `99-print.css`, where `.list` is a body class. This theme has no such class.
- **The entire `.bookshelf*` block.** See below — none of it had ever applied.

**Not firing — the significant finding.** micro.blog loads plugin stylesheets
**after** `main.css` (verified in live `<head>` order: `main.css`, `custom.css`,
`bookgoals.css`, `bookshelf.css`, `wayback-link-preserver.css`). At equal
specificity the plugin therefore wins. Consequences on `/reading/`, which does use
the bookshelf shortcode live:
- Our `ul.bookshelf.bookshelf`, its `li`, `h3.bookshelf__title`, and both
  `--variant-grid` rules were **byte-identical duplicates** of plugin-bookshelf's
  own — pure redundancy.
- Our three `--variant-list` rules **conflicted** and silently lost: the theme
  asked for a `repeat(auto-fill, minmax(5rem,8rem))` cover grid with vertical-flex
  items and `width:100%` covers; the plugin's vertical list with `5rem 1fr` item
  grids is what has always rendered. Removed at the user's direction (2026-08-05)
  rather than out-specified, so `/reading/` is unchanged.
- `.bookgoals img.cover` DID win (0,2,1 vs the plugin's 0,2,0) — but the plugin's
  `max-width: 100px` was still capping it, which would have silently swallowed the
  units-audit rem conversion at the 106.25% root. Added `max-width: none`.
- **If you ever restyle a plugin's markup, out-specify it deliberately** (e.g.
  prefix `ul.bookshelf`) instead of matching its selectors — a comment in the
  Plugins section of `main.css` now says so.

**Not firing — reported, left alone by the user's choice:**
- **Archive photo thumbnails have never rendered in production.** Posts carrying
  `.Params.photos` (they appear on `/photos/`) render in `/archive/` with no
  `<img class="archive-entry-thumb">`, so `.Site.Params.archive_months_photos` is
  falsy live despite `config.json` defaulting it to `true`. Our
  `list.archivehtml.html` IS winning the lookup (the live page carries our
  `archive-entry`/`archive-month`/`archive-cats` classes), so the condition itself
  is false — the `plugin.json` boolean field was sitting unchecked in the
  micro.blog backend and overriding the config default. Note the earlier
  verification of this feature was done in the LOCAL repro, where `config.json`'s
  `true` applies.
  - **RESOLVED 2026-08-05: the user enabled the setting and thumbnails render.**
    The template and CSS were correct all along; only the backend checkbox was off.
    **Takeaway for any future boolean setting: a `plugin.json` boolean field left
    unchecked OVERRIDES a `true` default in `config.json`, silently disabling the
    feature in production while the local repro still shows it working.** That
    combination is why this went unnoticed. Don't treat a `config.json` boolean
    default as the effective production value once the same key is exposed as a
    backend field.
  - **Consequence now that it is on:** the `aspect-ratio: 1` added to
    `.archive-entry-thumb` in the units audit is live-visible for the first time —
    archive thumbnails crop to square (matching `/photos/`). Drop that one line if
    uncropped thumbs are wanted.

**Dead but deliberate — keep:**
- `#site-header` / `#site-footer` / `#main` — live HTML confirms micro.blog renders
  OUR `baseof`/partials (`class="site-header"`, `class=page-content`,
  `<main class=wrapper id=main-content>`, `class=site-footer`), so these ID
  selectors never match today. They are the documented fallback for micro.blog's
  default base template (see "How micro.blog renders this theme") and cost nothing.
- `custom_footer.html` (one comment line) — an intentional blank override that
  shadows any theme-blank/plugin `custom_footer.html`. Functional, not dead.
- `.microblog_reply_form` in the print block — injected at runtime by
  conversation.js, so it can never appear in fetched HTML; class name verified
  against the live script source.

**Removed at the user's direction (2026-08-05): all goldmark footnote styling** —
`.footnotes`, `.footnote-ref`, `.footnote-backref`, the `[id^="fn:"]` /
`[id^="fnref:"]` scroll-margin and `:target` highlight. **Zero footnotes across
all 187 posts in `/archive/index.json`**, and micro.blog posting doesn't lend
itself to them. If a post ever uses `[^1]`, goldmark's default markup renders
unstyled but perfectly readable. The generic `.post-content sup` rule was KEPT —
it is superscript styling, not footnote-specific. Side effect: the reduced-motion
block now covers only two transitions (link hover, social pills); its comment was
updated to match.

**Unstyled markup hooks** (harmless, noted so they aren't mistaken for bugs):
`.home-status`, `.home-feed`, `.footer-about` are structural grid children
positioned by their parents; `.media-entry--movie` is a BEM modifier that was
emitted but never given a rule.

**Params audit — clean.** Every `config.json` param is read by a template; every
`plugin.json` field is read. The `.Site.Params.*` reads with no local definition
are all platform-supplied (`about_me`, `author.*`, `plugins_js`, `theme_seconds`,
`include_conversation`), and the `social_*_url` fields having no `config.json`
default is the documented 2026-06-06 decision. One inconsistency:
**`home_cat_books` was the only `home_cat_*` with no `config.json` default** — its
only definition was the inline `| default "Books"` on `index.html:10`.
**FIXED 2026-08-05:** added `"home_cat_books": "Books"` to `config.json`, so all
six category names now live in one place. Backend-field exposure is still uneven
and deliberately left that way (only the two reading categories are tunable
without a push):

| param | config.json | backend field |
|---|---|---|
| `home_cat_status` | yes | no |
| `home_cat_books` | yes (added) | no |
| `home_cat_started_reading` | yes | yes |
| `home_cat_finished_reading` | yes | yes |
| `home_cat_movies` | yes | no |
| `home_cat_highlights` | yes | no |

### Category NAMES vs. SLUGS — do not confuse them (verified 2026-08-05)
The live URLs are `/categories/finished/` and `/categories/started/`, which reads
as though the categories were named "finished"/"started". **They are not.** Those
are micro.blog custom SLUGS; the category names carried on posts are the full
strings. Verified from `feed.json`'s per-item `tags` on the live site:
`'Movies'` (13), `'Books'` (9), `'Finished Reading'` (6), `'Started Reading'` (2),
`'Status'` (2), `'Highlights'` (1) — exactly the `config.json` values, which are
therefore correct and must NOT be changed to the slugs.
- What would break if they were: `where ... "Params.categories" "intersect"` would
  match nothing, so `$finishedTaggedPosts` would empty out, the Books fallback on
  `index.html:113` would fire and send "All books →" to `/categories/books/`, and
  the Finished/Started sections would silently fall back to text-pattern detection
  only.
- The slug/name split is exactly why `$categoryURLs` resolves each link by term
  TITLE → `.RelPermalink` (`index.html:27-34`) instead of `urlize`-ing the name:
  `urlize "Finished Reading"` yields `/categories/finished-reading/`, which **404s
  on this site**.

What `home_cat_books` actually drives: it names the BROAD "Books" archive used as
a **fallback destination** for the homepage's "All books →" link. Imported RSS
reading posts land on that category before micro.blog's narrower Started/Finished
Reading categories populate, so `index.html:113` retargets the link to the Books
archive when — and only when — the Finished Reading category has zero posts and
Books has some. It is a link-destination fallback only; it never selects which
posts a section shows.

**Currently dormant on eberle.blog** (verified 2026-08-05): "Finished Reading" is
populated, so the branch never fires and "All books →" points at
`/categories/finished/`. Failure mode if the "Books" category were ever renamed in
the backend: `$bookFallbackPosts` silently goes empty and the fallback simply
never triggers — no error, no broken link, the link just stays on Finished
Reading. That is why this is a tidiness issue, not a bug.

**Adjacent, and NOT hypothetical — micro.blog uses custom category slugs.** Live:
"Finished Reading" → `/categories/finished/`, "Started Reading" →
`/categories/started/`; the conventional `urlize` paths `/categories/finished-reading/`
and `/categories/started-reading/` both **404**. The `$categoryURLs` title →
`.RelPermalink` resolution (`index.html:27-34`) is what makes the homepage links
correct, and it is working live. But the `| default (printf "/categories/%s" ...
| urlize)` fallback on lines 103-108 would emit those 404 URLs if a term page were
ever unavailable at build time. Fine as a last resort, worth knowing it is not a
safe path on this site.

## Units audit (2026-08-05)
Full sweep of every length in `main.css`. The **unit policy is now written at the
top of the file** — read it before adding a px value. Summary of what changed and
what deliberately did not:

- **Converted px → rem** (component dimensions, which should track the reader's
  root text-size preference exactly like the layout tokens converted in the
  mobile-first pass): `.intro-avatar` `124px`/`136px` → `7.75rem`/`8.5rem`,
  `.media-cover` `72px` → `4.5rem`, `.media-list--reading .media-cover` `66px` →
  `4.125rem`, `.archive-entry-thumb` `72px`/`60px` → `4.5rem`/`3.75rem`,
  `.photos-grid` `gap: 12px` → `0.75rem`, `.bookgoals img.cover` `100px` →
  `6.25rem`. **These render 6.25% larger above the 35em breakpoint**, where the
  root is 106.25% — that is the intended effect (the whole reason for the unit
  change), and it is the same trade the `--gap`/`--nav-width`/`--main-width`
  conversion already accepted. Numbers are the old px ÷ 16.
- **Converted px → em** (belongs to its element, not the page): `.intro-social
  svg` `12px` → `1em`, so the icon tracks its own label's 0.74rem instead of the
  root. Resolves to ~11.8px — visually identical to the 12px it replaced.
- **Kept as px, deliberately** — 1px borders, `text-decoration-thickness`, the
  focus `outline: 2px` / `outline-offset: 3px`, small `border-radius` (2-4px) and
  the `999px` pill, `box-shadow` offsets/blurs, the blockquote's `3px` rule, and
  `.visually-hidden`'s 1px clip idiom. All are device-pixel-oriented ornament;
  scaling them produces fractional device pixels and blurry edges, and none is
  content sizing. Browser *page* zoom scales them anyway — only the text-size-only
  preference doesn't, which is the correct behavior for a hairline.
- **Already correct, verified**: no `pt`/`cm`/`mm`/`in`/`pc` anywhere; every
  `line-height` is unitless (inherits as a ratio, not a frozen length); every
  `letter-spacing` is `em`; `vw` appears only as the middle term of a `clamp()`
  with `rem` bounds, so a text-size preference still moves the floor and ceiling;
  `@media` breakpoints are all `em` (a different axis from the rem layout values —
  see the file-top policy); prose measures are `ch`; table/footnote/code padding
  and margins are `em`, correctly scaling with their own font-size.

**Found and deliberately NOT changed:**
- **`.post-content h2/h3` mixes `margin: 1.7rem` with `padding-bottom: 0.28em`.**
  `~/git/website` converted its equivalent heading margins to `em` on the argument
  that spacing should track the heading's own size. Here both margins are rem, so
  they at least scale together under root changes — the mismatch is only that they
  don't scale with the heading. Converting properly means splitting the shared
  h2/h3 rule per level (h2 is 1.5em, h3 1.17em, so one em value can't serve both)
  and re-tuning the vertical rhythm, which is a typographic redesign with no
  browser here to check it against. Worth doing in a pass that is about heading
  rhythm specifically.

**Adjacent fix made while measuring:** `.archive-entry-thumb` declared
`width: auto` while its HTML carries `width="60" height="60"`, so the reserved box
was square before the lazy image loaded and the photo's true ratio after — the
archive row shifted sideways on every thumbnail load. Added `aspect-ratio: 1`, so
the box matches the declared attributes and the existing `object-fit: cover`
(previously inert — with an auto width the box always took the image's own ratio)
finally does something. **Visual consequence: archive thumbnails now crop to
square**, matching how `.photos-grid` already treats photos. Revert the
`aspect-ratio` line if uncropped thumbs were wanted.

Verified: pinned-0.158 build clean, tinycss2 re-parse 0 errors. No browser
in-session — the 6.25% growth above 35em and the square thumbs are reasoned, not
screenshot-diffed.

## Readability audit (2026-08-05)
Measured, not eyeballed: character-per-line counts were derived from
`static/fonts/charter-400-latin.woff2`'s own `hmtx` advance widths (fontTools),
frequency-weighted over English letter distribution plus spaces — an effective
average of **0.4395em per character** (vs. the conventional 0.5em rule of thumb,
which undercounts by ~14%). `1ch` in Charter = 0.5560em.

- **THE finding: the post body had no measure cap.** `.post-content` filled the
  whole `--main-width` column — a **43.75em measure, ~99 characters per line**
  against the 45-75 comfortable range. Every *other* prose block in the theme was
  already capped (`.intro-body` 60ch, `.post-entry-summary` 60ch,
  `.status-card-body` 58ch, `.footer-about-text` 32ch), so the primary reading
  surface was the one that got missed, not a deliberate exception.
  - Fixed with `max-width: 60ch` — **the theme's own existing number**, not a new
    one — which also lands on `~/git/website`'s settled measure (640px prose at
    1.2rem = 33.33em; see its `20-content.css`, which documents the reasoning).
    Result: **33.36em / ~76 chars**, identical at desktop root (17px), mobile root
    (16px), and for the 0.96rem `.post-entry .post-content` on list/replies pages,
    since `ch` resolves against each element's own font-size.
  - **Applied to text-level children, NOT to `.post-content` itself.** Capping the
    container would have shrunk every photo by a quarter on a blog where photo
    posts are a first-class type. Paragraphs holding only an image are exempted
    via `:has()` (micro.blog wraps post images in `<p>`), as are `figure`, and
    `table`/`pre` were left out of the capped list entirely — tabular data and
    code want the full column.
  - Note the two conventions disagree on the label: `~/git/website` calls the same
    33.33em measure "~66-67 characters" using the 0.5em heuristic; the font's real
    metrics make it 76. Same physical measure either way — don't "fix" one number
    to match the other.
- **`hyphenate-limit-chars: 6 3 3`** added alongside the existing `hyphens: auto`
  (only break 6+ letter words, never strand fewer than 3 either side) — same
  values as the main site, which tuned them for exactly this narrow-measure case.
- **`text-wrap: pretty`** extended to the other prose surfaces (intro bio, status
  card, list/archive summaries, colophon). It was already on `.post-content p/li`.
- **Print stylesheet added** — the theme had none, so a printed post carried the
  header, footer colophon, pagination, post-nav, micro.blog's reply *form*, and a
  light-on-dark code block. Mirrors `~/git/website`'s `99-print.css` reduced to
  the components that exist here. The conversation itself is kept (printed replies
  are part of the post's record); only `.microblog_reply_form` is hidden. `pre`
  needs its own dark `color` in print because the screen rule hardcodes
  `#edf3f6` light-on-dark.

**Found, deliberately NOT changed** (both are documented boundaries, not oversights):
- **Prose is 1rem = 17px** at the desktop root vs. the main site's 19.2px. Capping
  the measure makes the two identical in *ems* and character count; only the
  physical size differs. Changing the base is what "Self-hosted Charter body font"
  explicitly rules out as a side effect — every component rem-value in this file is
  tuned around 106.25%.
- **Smallest meta text is 0.74rem (~12.6px)** (`.home-section-*`, footer headings).
  On the small side, but it is furniture, it already carries the darkened
  AA-cleared `--secondary`, and moving it cascades through the same tuned scale.
- `.archive-entry-summary` and `.media-entry-review` are uncapped but structurally
  constrained (a flex row beside a date/thumb; a half-width grid column), and both
  render truncated blurbs — no cap needed.

Verified: pinned-0.158 build clean, `main.css` re-parsed with tinycss2 (0 parse
errors, top-level and nested). **No browser available in-session** — the measure
math and CSS validity are checked, the visual result is not screenshot-diffed.

## Web-standards audit (2026-08-05)
Audited against **The Website Specification** (`https://specification.website`,
36 `required` + 81 `recommended` items) plus general practice. The spec is
exposed as an MCP server at `https://mcp.specification.website/mcp` — note it is
registered in `~/.claude.json` under the **`~/git/website` project only**, so in
THIS repo's sessions its tools aren't loaded; it was queried directly over
JSON-RPC with `curl` (`tools/call` → `get_checklist`). Register it for this
project too if you want the tools natively.

**Fixed in this pass:**
- **Untitled posts had no `<h1>` at all** (heading-hierarchy, `required`) — the
  most common page type on a micro.blog. `post/single.html` only emitted the h1
  `{{ with .Title }}`, and `header.html` deliberately renders the masthead as a
  `<span>` off the home node (see "Accessibility pass"), so such a page's first
  heading was the *footer's* `<h2>`. Verified in the `testsite/` build before and
  after. Now falls back to a `.visually-hidden` h1 carrying the post date — the
  same label the archive and `<title>` already use. Not tagged `p-name`: in
  microformats an h-entry without one takes its name from the content, which is
  the correct reading for a note. Same fix in `_default/single.html`.
- **`prefers-reduced-motion` block** (`required`) — the theme had three
  decorative transitions (link hover, social pills, footnote `:target` fade) and
  no block. Uses `0.01ms`, not `0s`, so `transitionend` handlers still fire.
- **Generic link text** (`required`) — `Read more →` / `Permalink →` repeat once
  per entry in `_default/list.html` and `index.html`'s highlights, so they're
  indistinguishable in a screen reader's link list. Added `aria-label`s naming
  the destination, with the visible text as a prefix (WCAG 2.5.3 label-in-name).
- **`<meta name="color-scheme">` + `<meta name="theme-color">`** (`recommended`)
  — both were missing. Single-valued (no `media` variants) since this theme is
  light-only. `color-scheme` in the head, not just `main.css`'s `:root`, is what
  actually prevents the pre-stylesheet white flash for dark-OS readers.
- **`forced-colors: active` block** (`recommended`) — every boundary in this
  theme is a `color-mix()` border or a `box-shadow`, both of which forced-colors
  discards; the social pills, covers, photo grid and avatar would have lost their
  shapes entirely. Re-expressed with system color keywords (`ButtonBorder`,
  `Highlight`/`HighlightText`).
- **`100vh` → `100dvh`** on the main column's `min-height` (`recommended`), vh
  retained as the preceding fallback declaration.
- **`overflow-y: scroll` → `scrollbar-gutter: stable`** (`recommended`), with an
  `@supports not` fallback to the old declaration. Same anti-shift effect without
  forcing a permanently visible track on overlay-scrollbar platforms.
- **`decoding="async"` on every `<img>`**; avatar got `fetchpriority="high"` (it
  is the only image in the homepage's initial viewport and the LCP candidate) and
  its `width`/`height` corrected `80` → `124` to match the CSS box.
- **Avatar `alt` → `""`** — it sits directly beside `.intro-title`, an `<h2>` with
  the identical name, so the alt text was a duplicate announcement. Decorative,
  not unlabelled; `u-photo` is unaffected (it reads `src`).

**Checked and already correct** (don't "fix" these): CLS is handled by
`aspect-ratio` on `.media-cover`/`.photos-grid a img` rather than width/height
attributes, so those images need none; `:focus-visible` (not `:focus`) throughout;
skip link; landmarks; `text-wrap: balance`/`pretty`; self-hosted subset WOFF2 +
`font-display: swap` + preload; `loading="lazy"` on everything below the fold and
on nothing above it; canonical, OG, JSON-LD, `rel=me`; `<html lang=en>` renders
correctly in production (unlike `.Site.LanguageCode` — see "Future landmines").

- **`conversation.js` MUST NOT get `defer`/`async`.** It builds the reply form
  with `document.write()` (verified by fetching it live, 2026-08-05), which
  destroys the document if it runs after parse. This is the obvious-looking
  "render-blocking script" fix and it would break every post page; a comment in
  `post/single.html` now says so. The legacy `type="text/javascript"` was dropped
  (inert either way).

**Platform-side, NOT theme-fixable** (probed live on eberle.blog, 2026-08-05):
- **No compression at all.** `Accept-Encoding: gzip, br, zstd` returns no
  `content-encoding` for either HTML or CSS — `main.css` ships ~30 KB
  uncompressed where gzip would be ~6 KB. `required` tier. Worth reporting to
  micro.blog; nothing a theme can do.
- **No security response headers** (HSTS, `nosniff`, `Referrer-Policy`,
  `Permissions-Policy`, CSP-as-header) and **no `Cache-Control`** on HTML or CSS
  — consistent with the head.html note that per-blog headers are impossible.
  `ETag` + `Last-Modified` ARE sent, so conditional requests work. Server is
  Caddy, HTTP/2 with h3 advertised.
- Good already: `/humans.txt` (the footer link) returns 200, `/robots.txt` and
  `/sitemap.xml` are served by the platform, and an unknown path returns a real
  `404` status.
- **`/.well-known/security.txt` and `/llms.txt` 404.** Both are theme-shippable
  in principle (`static/` lands at the site root, as `css/` and `fonts/` prove),
  but both were left alone deliberately: security.txt needs a contact address
  that's the user's call and an RFC 9116 `Expires` under a year out, which a
  hardcoded file in a theme silently outlives; llms.txt needs curation and
  micro.blog already serves feeds plus a full archive. Ask before adding either.

## Palette hue sync (2026-08-05)
Mirrors `~/git/website` commit `fc13a1a` ("Tune palette hues against the Homer
paintings"), which retuned four light-mode tokens on the **hue axis only**:
- `--tide` `#24566a` → `#1c5863`, `--tide-deep` `#173f50` → `#0e414a` — the accent
  is now pinned to the hue of the *sea* in Northeaster (LCH hue ~220) rather than
  its sky/foam band (was 238.8). L and C held fixed, so contrast is essentially
  unchanged: link on `--theme` 6.98→6.95, on `--entry` 6.16→6.13; accent 9.79→9.73
  / 8.64→8.59. Re-derived here with the relative-luminance formula, not assumed
  from the upstream commit message. Keep future accent tuning on the hue axis.
- `--fog-haze` `#9da5a5` → `#9ba5ab`, `--fog-pale-haze` `#c7cac6` → `#c5c9cd` —
  the hairlines were green-peaked; corrected toward the painting's blue-dominant
  slate. Relative luminance unchanged (0.3679→0.3682, 0.5846→0.5805), so the
  `color-mix()`-composited rules/borders that derive from them hold too.
- **Deliberately NOT synced:** `--fog-driftgray`. The main site is at `#585f65`;
  this theme keeps `#4c545a` because it uses that color at smaller meta-text sizes
  (see "Contrast pass" below — this is the second AA-driven divergence on that one
  token, not drift).
- **Dark mode still NOT ported.** `~/git/website` re-gained a
  `prefers-color-scheme: dark` palette in `c976527` (before this commit), so the
  "the main site has no dark theme" rationale in "Dark theme removal" below is now
  STALE as a fact about the main site — but the removal here was not reverted: this
  pass was a color sync, and re-adding a dark palette means re-auditing every
  component in this theme (composited `color-mix()` backgrounds, the intro-social
  pill, book covers), which is its own piece of work. If you do it, the upstream
  dark tokens + the `prefers-color-scheme: dark and prefers-contrast: more` block
  in `01-tokens.css` are the source to copy.
- Verified: pinned-0.158 build against `testsite/` clean, `main.css` served with
  the new values.

## Structured data: JSON-LD (2026-08-03)
Added schema.org markup via `<script type="application/ld+json">` in
`head.html` — `Person` + `WebSite` on every page, plus `BlogPosting` on post
pages (`.IsPage` and `.Type == "post"`, matching the `where ... "Type" "post"`
convention `index.html`'s homepage sections already use).
- **Built with `dict`/`jsonify`, not hand-written JSON strings.** Bios and
  post bodies are free text that can contain quotes or literal
  `</script>`-shaped substrings; `jsonify` goes through Go's
  `encoding/json.Marshal`, which HTML-escapes `<`/`>`/`&` by default, so this
  is safe against both malformed JSON and script-injection from user-authored
  content without any manual escaping.
- **`Person` and `WebSite` are `@id`-referenced, not duplicated inline**
  (`"publisher": {"@id": "...#person"}` etc.) — the standard schema.org
  pattern for an entity that's shared across every page on the site.
- **Hit and fixed a real Go `html/template` gotcha**: `jsonify`'s output,
  interpolated directly into a `<script>` body, came out DOUBLE-encoded — the
  whole JSON document wrapped in an extra pair of quotes with every internal
  quote/newline backslash-escaped. Go's contextual autoescaper treats any
  `<script>` element's content as a JS expression context regardless of its
  `type` attribute, and re-escapes an untyped string as a quoted JS string
  literal. Fixed by piping through `| safeJS`, which marks the value as
  pre-escaped and embeds it verbatim. Caught by actually parsing the
  rendered output as JSON in the verification step below, not just checking
  the build exit code — a build succeeds either way, since the malformed
  output was still valid *inside* its accidental outer string, just not
  valid JSON-LD once unwrapped.
- **`BlogPosting.image` prefers `.Params.photos[0]` over the site avatar**
  when present (mirrors the OG-image fallback logic already in this file) —
  verified against the `photo-post.md` fixture, which has its own photo and
  correctly does NOT fall back to the avatar.
- **`headline` falls back to a truncated `.Summary`** for posts with no
  `.Title` (native Micro.blog posts routinely have none) — same
  `$fallbackTitle` pattern already used for `twitter:title`/`og:title`
  higher up in this file, reused rather than reinvented.
- Verified against the `testsite/` fixture with the pinned-0.158 build:
  parsed the rendered `<script type="application/ld+json">` block as actual
  JSON (not just checked it renders) on the homepage, four different post
  fixtures (untitled, photo, both reading-flow shapes), and `/about/` (a
  `Type: page`, not `Type: post`) — confirmed `BlogPosting` appears only on
  the post pages, headline fallback and image-source selection both resolve
  correctly, and the `/about/` page correctly gets `Person`+`WebSite` only.

## What was fixed in the June 2026 session
- Removed `opengraph.html` (was breaking feed generation on 0.158)
- Fixed `list.archivehtml.html` Date.Format syntax for 0.158
- Removed `content/` directory (was injecting unwanted bio text)
  **SUPERSEDED 2026-08-05:** a `content/` dir exists again, holding exactly one
  file — `content/search.md`, absorbed from plugin-search-page. The June removal
  was about that directory's *contents*, not the mechanism; a theme's `content/`
  IS merged by micro.blog, which is what made the stray bio text appear in the
  first place and is what makes the search page work now. Don't delete the
  directory on the strength of this line.
- Removed `theme.json` (potential conflict with plugin.json)
- Reverted `microblog_head.html` to direct call (no templates.Exists guard)
- Fixed `.Site.Author.avatar` → `.Site.Params.author.avatar`
- Reverted `hugo.Data` → `.Site.Data` for 0.117 compatibility
- Fixed CSS selectors: added `#site-header`, `#site-footer`, `#main` alongside
  class-based selectors so styling works with micro.blog's default base template
- Fixed avatar 404: changed username from `jaredeberle` to `eberle` in config.json
- Added `:has(.intro)` CSS rule to hide header avatar on homepage
- Pushed all changes to the deploy branch (NOTE: as of 2026-06-10 the remote
  default — and the branch micro.blog pulls — is **main**; earlier "master" notes
  here were stale)
- Diagnosed manual full rebuild failure as micro.blog platform bug (Hugo 0.158
  PR #14601 template lookup change), reported to micro.blog support
