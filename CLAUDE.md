# micro-claude theme — Claude session notes
Last updated: 2026-06-22 (accessibility pass: main landmark + WCAG AA contrast)

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
- NOTE for LOCAL builds: vanilla Hugo ignores `markup`/`ignoreLogs` from a
  THEME's config.json (only params/menus/outputFormats/mediaTypes merge —
  verified empirically; even our `pluralizeListTitles: false` doesn't merge), so
  add `markup.goldmark.renderer.unsafe: true` to the site-root export config.

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
static/css/main.css          # all styling — Solarized Light palette
config.json                  # Hugo config + local dev params
plugin.json                  # micro.blog theme metadata + settings fields
.gitignore                   # excludes public/, resources/, microblog_head.html
```

## Homepage sections (layouts/index.html)
1. **Intro card** — avatar + bio + social links (from `intro.html`)
2. **Status card** — most recent post in "Status" category
3. **Currently Reading** — imported `Started reading:` posts that do not yet have a matching
   finished entry
4. **Finished Reading | Movies** — two-column, recent `Finished reading:`/Movies posts
5. **Highlights** — recent posts in "Highlights" category

- **Sourcing:** one base slice — `(where .Site.RegularPages "Type" "post").ByDate.Reverse`
  — then per-section `where ... "Params.categories" "intersect" (slice <name>)`. `where`
  preserves order, so derived slices are NOT re-sorted.
- **Category names + counts are params.** Names (`home_cat_status/started_reading/
  finished_reading/movies/highlights`) live in `config.json`. Counts (`home_books_count`/`home_movies_count`/
  `home_highlights_count`) are `config.json` defaults AND exposed as **backend fields** in
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
  `Finished Reading` / `Finished reading:`. Started-reading posts are shown until a
  finished-reading post with the same ISBN exists. The ISBN comes from `.Params.books` when
  present, else falls back to parsing a `https://micro.blog/books/<isbn>` link out of the
  post body. That lets imported RSS posts behave like native Micro.blog book entries
  without a brittle dependency on exact category labels.
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
- **0.91 compat VERIFIED with a real 0.91.2 binary (2026-06-11):** the whole theme
  builds clean on Hugo 0.91.2 with exactly ONE exception — `hugo.Data` in
  index.html:76 is fatal there ("can't evaluate field Data"); that's the known,
  deliberate trade-off documented below (prod is 0.158 and won't go backwards).
  Gotcha when testing: 0.91 only reads `config.toml`, not `hugo.toml`.
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
  config keys `languageCode` (→ `locale`) and `paginate`.
  (`.Site.Data` was also here but has been switched to `hugo.Data` in index.html.)
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
