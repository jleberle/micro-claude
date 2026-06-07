# micro-claude theme — Claude session notes
Last updated: 2026-06-06 (full-rebuild root cause found & fixed)

## What this repo is
A custom Hugo theme for Jared Eberle's micro.blog at **eberle.blog**.
- GitHub: `github.com/jleberle/micro-claude`
- micro.blog pulls from the **master** branch (only branch — push to master)
- Local dev: `hugo server` from `/Users/jaredeberle/git/microblog-theme/`
- Hugo locally: 0.162 | micro.blog production: **0.158**

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
- Always push: `git push origin master`

## Editable settings (plugin.json fields)
Because this is installed as a plugin, `plugin.json` `fields` render as form
inputs in the micro.blog backend (Plugins → this plugin). Real micro.blog schema
(confirmed from installed plugins like plugin-cc / wayback-link-preserver):
```json
{ "field": "params.social_bluesky_url", "label": "Bluesky URL",
  "placeholder": "https://...", "type": "string" }
```
- Key is `"field"` (dotted `params.<name>`), NOT `name`. Types: `string` / `boolean`.
- There is NO `default` mechanism — `placeholder` is only a hint. To ship working
  values, keep them in `config.json` `params` (low-precedence defaults); a value
  typed in the backend overrides the config.json default. **VERIFIED in production
  (2026-06-06):** edited a `social_*_url` field in the micro.blog backend and the
  live link updated accordingly, confirming backend > config.json precedence.
- Currently exposed: the 5 `social_*_url` links. Templates read `.Site.Params.
  social_*_url` and guard with `{{ with }}`, so an empty field just hides that link.
- Editing flow: leave a field blank → config.json default applies; type a URL →
  it overrides. Local `hugo server` only sees config.json (plugin.json fields are a
  backend concept), so config.json must keep the defaults for local dev to work.

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
- **TODO:** report upstream to github.com/microdotblog/plugin-search-page (line 4
  should be `.Site.Params.author.avatar`); once fixed there, our override can go.

### micro.blog strips `<style>` tags from theme template output
- Cannot inject page-scoped CSS via `<style>` tags in layout files
- Use `main.css` with `:has()` selectors instead for page-specific rules

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
    list.archivehtml.html    # archive page (fixes Hugo 0.158 Date.Format syntax)
    single.html              # generic single page
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
3. **Currently Reading** — from `hugo.Data` / `.Site.Data` bookshelves
4. **Books | Movies** — two-column, recent posts in Books/Movies categories
5. **Highlights** — up to 10 recent posts in "Highlights" category

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
- **Future landmines** (deprecated on 0.158, not yet removed — will break the same
  way when micro.blog next bumps Hugo): `.Site.LanguageCode` (→ `.Site.Language.Locale`),
  `.Site.Data` (→ `hugo.Data`), config keys `languageCode` (→ `locale`) and `paginate`.
  NOTE: `.Site.LanguageCode` already misbehaves on micro.blog's 0.158 — it returns
  the literal `-`, which is why `og:locale` was rendering `content="-"`. Fixed by
  hardcoding `og:locale` to `en_US` in head.html (single-locale English blog).
- **Early-warning tool:** the pinned `hugo-0.158` + full-plugin local repro (see
  "Faithful local 0.158 reproduction"). Re-run it against a newer pinned binary
  whenever micro.blog upgrades Hugo to catch the next round of removals before they
  ship. Watch installed PLUGINS too, not just this theme — they carry the same risk.

- `hugo.Data` introduced ~0.155 — **use `.Site.Data` instead** for 0.117 compat
  (generates a deprecation WARN on 0.158 but not an error)
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
plugin-archive-months,plugin-photos-months,theme-blank
```
- Installed plugins (clone each into themes/): plugin-cc, wayback-link-preserver,
  plugin-bookgoals, kottkrig/microdotblog-bookshelf-shortcode, plugin-search-page,
  flschr/mbplugin-youtube-nocookie, plugin-archive-months, plugin-photos-months.
- The local `hugo` CLI aborts the WHOLE build on the first render error (so
  public/ ends up empty); micro.blog tolerates per-node failures and ships the
  rest — which is why prod showed only home+feed gone. Plugins inject head partials
  via `.Site.Params.plugins_html`; missing ones = "partial X not found".

## Things still outstanding / to watch
- **footer.html** custom links (RSS · Micro.blog · Theme · Codeberg) — confirm
  these are rendering on the live site; if not, micro.blog's default footer is
  being used instead of ours
- **Highlights post not appearing on homepage** — suspected fastpublish timing
  issue; most recent Highlights post shows on category page but not homepage.
  Trigger a full publish cycle to test.
- **Manual full rebuild** — FIXED & verified in production (stale
  `.Site.Author.avatar` in plugin-search-page's archivejson template). Safe to use.

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
- Pushed all changes to **master** branch (micro.blog pulls from master, not main)
- Diagnosed manual full rebuild failure as micro.blog platform bug (Hugo 0.158
  PR #14601 template lookup change), reported to micro.blog support
