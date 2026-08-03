# micro-claude theme — Claude session notes
Last updated: 2026-08-03 (Structured data: JSON-LD Person/WebSite/BlogPosting)

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
  `Params.author.avatar` icon. The live file is full-text, so our override IS
  winning the lookup — confirmed.
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
layouts/
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
  two columns diverge in height. `.media-columns .media-cover { width: 56px }` shrinks the
  book covers in that grid only (currently-reading keeps 80px) to bring row heights closer;
  the movie count is also backend-tunable to fill remaining space.

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
  --theme=micro-theme,plugin-cc,wayback-link-preserver,plugin-bookgoals,\
microdotblog-bookshelf-shortcode,plugin-search-page,mbplugin-youtube-nocookie,\
theme-blank
```
- Installed plugins (clone each into themes/): plugin-cc, wayback-link-preserver,
  plugin-bookgoals, kottkrig/microdotblog-bookshelf-shortcode, plugin-search-page,
  flschr/mbplugin-youtube-nocookie. (plugin-archive-months and plugin-photos-months
  were uninstalled 2026-06-10 — superseded by this theme's root-level templates.)
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
