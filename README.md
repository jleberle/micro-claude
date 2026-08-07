<!-- ⚠️ ⚠️ ⚠️ -->

> # ⚠️ Personal theme — no support, no external revisions
>
> **This is a personal theme built for my own site, [eberle.blog](https://eberle.blog).**
> It was **written by Claude** (Anthropic's AI assistant) together with Jared Eberle,
> for my own use, it's heavily tailored and opinionated for what I want.
>
> It is published **as-is, for reference only.** I **cannot provide support**,
> answer setup questions, or troubleshoot your installation, and **will not make
> revisions, accept feature requests, or review/merge pull requests** for other users.
>
> You are welcome to fork it under the MIT License and adapt it yourself, but just know,
> **you are entirely on your own.** It is tightly coupled to my specific
> micro.blog configuration, installed plugins, and content categories, and is not
> intended to be a general-purpose, reusable theme.

<!-- ⚠️ ⚠️ ⚠️ -->

# Micro Claude, a micro.blog theme

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A custom Hugo theme for [eberle.blog](https://eberle.blog) that mirrors the style of
[jaredeberle.org](https://jaredeberle.org): the "Northeaster" palette, self-hosted Charter
(body) and Fraunces (headings), light-only (no dark mode).

- **Repo:** `github.com/jleberle/micro-claude` — micro.blog pulls from the **`main`** branch.
- **Hugo:** targets **0.158**, micro.blog's production version. Older versions are not
  supported (see [Hugo compatibility](#hugo-compatibility)).

## Installing (as a plugin, not a theme)

This repo is installed under micro.blog's **Plugins**, **not** selected as the active Theme.

The reason: `layouts/opengraph.html` (the custom Open Graph card template) is **only loaded
when installed as a plugin.** Installed as the active Theme, micro.blog never renders the OG
card. As a plugin, it overlays the active/default theme and the card works. Installing as a
plugin also turns `plugin.json` `fields` into editable settings in the micro.blog backend.

To install: add it as a custom plugin pointing at this GitHub repo, and ensure micro.blog's
Hugo version is **0.158**.

## File structure

```
layouts/
  robots.txt                 site robots.txt — MUST be layouts/, not static/, because
                             micro.blog ships a default robots.txt that only a layout
                             template overrides (see "Theme overrides" below)
  list.archivehtml.html      /archive/ — ROOT level (not _default/), themed + month-grouped;
                             home-node ArchiveHTML output, so it must live at root to win
                             the template lookup ahead of micro.blog's theme-blank
  list.photoshtml.html       /photos/ — ROOT level for the same reason; themed photo grid
  list.archivejson.json      home-node ArchiveJSON — overrides plugin-search-page's
                             broken copy and backs /search/'s full-text index
  opengraph.html             OG card template (rendered by micro.blog's non-Hugo card renderer)
  shortcodes/
    readinggoals.html        preferred name for per-year finished-books grids in content —
                             see "Installed plugins" below for why it isn't called `bookgoals`
    bookgoals.html           fallback shortcode under the absorbed plugin's original name
    bookshelf.html           bookshelf embed — kept available but CURRENTLY UNCALLED and
                             unstyled (its `.bookshelf-*` CSS was removed 2026-08-06 when
                             /reading/ stopped calling it; restore from git history first)
  _default/
    baseof.html              page skeleton (micro.blog may override with its own base)
    list.html                category / section list pages
    single.html              generic single page
  post/
    single.html              post pages (microformats + categories)
  section/
    replies.html             /replies/ page
  partials/
    head.html                <head>: meta/OG/Twitter tags, JSON-LD, CSS link, microblog_head call
    header.html              site header (avatar hidden on homepage via CSS)
    footer.html              custom footer: RSS · Micro.blog · Theme · Codeberg
    intro.html               homepage bio card: avatar + bio + social links
    custom_footer.html       intentionally blank override hook (used by plugins)
    reading-goals.html       shared logic behind both goals shortcodes
    int-param.html           validated non-negative int from a backend field, with a
                             fallback — never cast a settings-form value with `int`
  index.html                 homepage
content/
  search.md                  /search/ page + nav entry, absorbed from plugin-search-page
assets/
  css/main.css                all styling — Northeaster palette (light-only). In assets/,
                              not static/: built via Hugo Pipes (minify + fingerprint),
                              see "Colors" below
static/
  js/search.js                /search/ page logic — the only JS this theme owns
  fonts/                      self-hosted Charter (body) + Fraunces (headings) WOFF2 + licenses
  .well-known/
    security.txt              RFC 9116 contact info; static/ works here because micro.blog
                              has no platform default at this path (contrast robots.txt above)
testsite/                     fixture site used by the CI build check (see below)
config.json                   Hugo config + local-dev params
plugin.json                   micro.blog plugin metadata + editable settings fields
theme.toml                    theme metadata
```

## Homepage sections

`layouts/index.html` renders, in order:

1. **Intro card** — avatar + bio + social links (`partials/intro.html`).
2. **Status** — most recent post in the `Status` category.
3. **Currently Reading** — two sources merged into one list: imported `Started reading:`
   posts with no matching finished entry (dated, newest first), followed by Micro.blog's
   own **Currently Reading bookshelf** (`hugo.Data.bookshelves`, undated, in shelf order)
   so a book moved onto the shelf in the Micro.blog backend appears **without needing a
   post**. A book present in both is shown once — the post wins, since it carries a date,
   a permalink and notes — and anything already finished is dropped from the shelf side.
   Rows read `Title by Author` regardless of source. The shelf is selected by
   `home_shelf_currently_reading` (a backend field; the shelf name lowercased with spaces
   removed, e.g. `currentlyreading`), and the merged list is capped by
   `home_reading_count` (default 8, backend field) — the one homepage section that was
   previously unbounded.
4. **Finished Reading | Movies** — two columns of recent `Finished reading:` / `Movies`
   posts. Finished Reading is de-duplicated by ISBN/title+author before the count cap
   applies, so a re-imported duplicate post never displaces a distinct book from the list.
5. **Highlights** — up to 10 recent posts in the `Highlights` category.

Reading sections are driven primarily by the imported post text pattern (`Started reading:`
and `Finished reading:`) so they keep working even if category labels drift. The matching
reading categories are still configurable and used for category-page links.

**Cross-repo contract:** those two prefixes are generated by
`jaredeberle.org`'s `layouts/reading.rss.xml` (the `$action` / `$plainBody`
variables), not by anything in this repo. Micro.blog imports that RSS feed as
posts on eberle.blog; this homepage's detection (`layouts/index.html`) matches
the imported text directly, and Micro.blog's own "Started/Finished Reading"
autotagging category fallback is itself configured to key off the same
prefixes — so both signals trace back to the one string. A rewording on the
website side silently empties these sections here with no error on either
side. The website repo's `scripts/checks/feed-lint.py` asserts the exact
prefixes as part of its preflight gate specifically to catch that before it
ships.

Two more details of that contract, both load-bearing for merging the ledger and
Micro.blog's own book posts into one list:

- **`📚` is a delimiter, not decoration.** The feed emits one `<p>` containing
  `<action>: <title> by <author>. 📚 <notes>`, while native Micro.blog book posts
  put the review on a following line. The homepage splits title from review at the
  newline and, failing that, at `📚` — so dropping or moving that emoji in
  `reading.rss.xml` would run the notes into the title link.
- **Started/finished pairing needs a key.** ISBN books pair by ISBN (via the
  `https://micro.blog/books/<isbn>` link the feed emits for them). Sources with
  only a `doi`/`access_url` have no ISBN, so they pair on the normalized
  `<title> by <author>` segment instead. That segment must stay byte-identical
  between a source's started and finished items — the notes may differ, the
  headline may not — or the started entry never leaves "Currently Reading."
- **The item guid is keyed on the work's own identifier, not the source folder name**
  (fixed 2026-07-27, `reading.rss.xml`) — `isbn`/`doi`/`access_url`, in that order, with
  the folder slug as a last resort for the few sources with none of the three. This is
  what makes renaming a `content/sources/<key>/` folder safe: guids used to be built from
  that folder name, so a rename rewrote every guid the source had ever emitted and
  Micro.blog would re-import any event still inside the 20-item feed window as a
  duplicate post. This repo's homepage still de-dups Finished Reading independently as a
  second line of defense, since a fix at the source doesn't retroactively clean up posts
  already duplicated.

## Customization

### Colors

All colors are CSS custom properties at the top of `assets/css/main.css`. Swap them to
re-palette without touching layout code.

`main.css` lives in `assets/` and is built through **Hugo Pipes** (`resources.Get | minify |
fingerprint`), which micro.blog's Hugo runs at build time. It moved there from `static/` on
2026-08-07: micro.blog copies `static/` verbatim and only minifies HTML, so the stylesheet
was shipping at full authored size with no compression from the platform either. Minifying
takes it 43.5 KB → 23.4 KB, and the content hash in the filename replaces the old
`?{{ .Site.Params.theme_seconds }}` query-string cache-bust. The `<link>` is wrapped in
`with` so a nil resource degrades to an unstyled page rather than failing the build — that
call sits in `head.html`, which every page uses.

### Social links — edited in the micro.blog backend

The five social links are exposed as **editable plugin settings** (`plugin.json` `fields`),
so they are managed in the micro.blog backend (Plugins → this plugin), not in code:

`social_website_url`, `social_bluesky_url`, `social_letterboxd_url`,
`social_librarything_url`, `social_discogs_url`

`intro.html` reads each via `.Site.Params.social_*_url` and guards it with `{{ with }}`, so a
**blank field simply hides that link** — there is no in-repo fallback. (Because plugin fields
are a backend-only concept, `hugo server` locally will not show the social links unless you
re-add them to `config.json` `params` as defaults.)

### Bio / avatar

- **Avatar** — `https://micro.blog/{username}/avatar.jpg`, built from `.Site.Params.author.username`.
- **Bio** — `.Site.Params.about_me`. The intro card only renders when a bio is present.

## Theme overrides & platform notes

- **`opengraph.html`** is consumed by micro.blog's **separate, non-Hugo OG card renderer**
  (a ~2010-era renderer, *not* Hugo), which generates the 600×315 social card. Hugo itself
  never renders this file. It uses the documented `.Site.Author.avatar` variable — correct
  here precisely because this is not Hugo.
- **`list.archivejson.json`** is a deliberate override of `plugin-search-page`'s template,
  which shipped a stale `.Site.Author.avatar` (removed in Hugo 0.156). On a micro.blog **full
  rebuild** that fault took down the home page + RSS/JSON feeds. This override uses the
  correct `.Site.Params.author.avatar` and shadows the plugin's copy.
- **`list.archivehtml.html` / `list.photoshtml.html`** are ROOT-level (not `_default/`)
  because `/archive/` and `/photos/` are the **home node's** ArchiveHTML/PhotosHTML outputs,
  and for the home kind Hugo checks `layouts/list.*html` before `_default/`. micro.blog's
  default theme-blank ships root-level copies, so a `_default/` template (from any theme or
  plugin) never wins. These provide the themed, month-grouped archive and photo grid, and
  **supersede `plugin-archive-months` / `plugin-photos-months`** (whose templates live in
  `_default/` and therefore never took effect). The `archive_months_photos` toggle is a
  field in this repo's `plugin.json`.
- **`microblog_head.html`** is injected by micro.blog at the platform level — it is *not* in
  this repo (and is `.gitignore`d as a local-dev stub). Do not commit a stub.
- **CSS targets both `#site-header`/`.site-header`** (and footer/main equivalents) because
  micro.blog's base template uses id-based hooks while this theme's partials use classes.
- **`layouts/robots.txt` vs. `static/`:** micro.blog serves a theme/plugin `static/` file only
  at paths the platform has no default for (`css/`, `fonts/`, `.well-known/security.txt`). At
  `robots.txt`, the platform *does* ship a default, so only a `layouts/robots.txt` **template**
  overrides it — a `static/robots.txt` copy is silently ignored in production (this was tested
  and got it backwards once; see `CLAUDE.md` for the full story).
- **`content/search.md` + `static/js/search.js`** power `/search/`, absorbed from
  `plugin-search-page`. `list.archivejson.json` above is load-bearing for it — search fetches
  `/archive/index.json` for its full-text index, not just providing a landmine-safe fallback.
- **`layouts/shortcodes/readinggoals.html` is the name to call in content**, not `bookgoals` —
  micro.blog re-installs `plugin-bookgoals` automatically whenever any content calls the
  `bookgoals` shortcode name, and an installed plugin's shortcode always wins over this theme's
  own copy of the same name. `bookgoals.html` is kept only as a fallback for if the plugin is
  ever fully retired.

## Testing

Two layers:

- **CI** (`.github/workflows/build-check.yml`) builds this theme standalone against the
  `testsite/` fixture on every push/PR to `main`, using the checksum-pinned production Hugo
  (0.158), and fails on any fatal template error or leaked error text. It is a smoke test —
  no plugins, no theme-blank.
- **`scripts/repro.sh`** is the faithful reproduction: 187 real posts (synthesized from the
  micro.blog content backup) against the real theme stack — this theme, both installed
  plugins, and micro.blog's `theme-blank` fallback. It asserts that all nine contested
  template paths resolve to this theme, and includes controls proving theme-blank is
  genuinely loaded and the deprecation sweep isn't blind. Run it before anything touching
  `head.html`, `baseof.html` or a home-node output. See `CLAUDE.md`.

  It builds into `.repro/` — inside the repo and gitignored, the same convention as Hugo's
  `public/` and `resources/` — so the output is inspectable when an assertion fails and
  `rm -rf .repro` is a full reset. Clones are cached there (~68 MB, mostly the content
  backup); `--fresh` re-fetches. Override the location with `WORK=`.

See `CLAUDE.md` for the full platform-behavior notes and the local 0.158 reproduction setup.

## Installed plugins

Two micro.blog plugins are installed alongside the theme:

| Plugin | Role |
|---|---|
| [wayback-link-preserver](https://github.com/gunnarr/wayback-link-preserver) | Wayback fallbacks for broken links |
| [mbplugin-youtube-nocookie](https://github.com/flschr/mbplugin-youtube-nocookie) | Privacy-friendly YouTube embeds |

Four others were **absorbed into the theme and uninstalled** on 2026-08-05 — the
search page, the reading-goals and bookshelf shortcodes, and the Creative
Commons license tag. See [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) for
what each contributed and its license. A fifth, an AI-blocking robots.txt
plugin, was replaced by this theme's own `layouts/robots.txt`.

## Hugo compatibility

**This theme targets Hugo 0.158 — micro.blog's production version — and nothing older.**
micro.blog's docs suggest a 0.91 compatibility floor for distributable themes; this one is
single-site and personal (see the disclaimer at the top), so that floor was **dropped on
2026-08-07**. It was buying insurance against a downgrade that will never happen while
costing a deprecated API in the home page's template, where a fault takes down the homepage
and both feeds together. If you fork this, assume 0.158+.

The real hazard is unchanged: an API **removed** between the version a template was written
for and the one production runs is a latent landmine that surfaces only on a **full rebuild**
(fast-publish serves cached output). `.Site.Author.*` was removed in 0.156 — use
`.Site.Params.author.*`.

Known current-version notes:
- The bookshelf/bookgoals data merge uses **`hugo.Data`** (0.155+), not the deprecated
  `.Site.Data`. Don't revert it for compatibility — see `CLAUDE.md`.
- `og:locale` is hardcoded to `en_US` because micro.blog's 0.158 returns the literal `-` for
  the deprecated `.Site.LanguageCode`.
- **No deprecation warnings** as of 2026-08-07, verified by building the `testsite/` fixture
  against Hugo 0.164 (six versions ahead of production). `CLAUDE.md` has the one-line sweep
  command to re-run on any micro.blog Hugo bump.

Full details, root-cause history, and the pinned-`hugo-0.158` local reproduction live in `CLAUDE.md`.

---

## Credits

- **Fonts (bundled):** [Charter](https://practicaltypography.com/charter.html) by Matthew
  Carter, via Michael Sharpe's XCharter, under the Bitstream Charter license —
  BITSTREAM CHARTER is a registered trademark of Bitstream Inc. And
  [Fraunces](https://github.com/undercasetype/Fraunces) by the Fraunces Project Authors,
  under the SIL Open Font License 1.1. Full texts ship beside the font files in
  `static/fonts/`.
- **Color palette:** "Northeaster," shared with [jaredeberle.org](https://jaredeberle.org)
  and tuned against the Homer paintings it is named for. (This theme began on
  [Solarized](https://ethanschoonover.com/solarized/) by Ethan Schoonover; no Solarized
  values remain.)
- **Absorbed plugins:** the search page, reading-goals and bookshelf shortcodes, and the
  Creative Commons license tag began as micro.blog plugins — see
  [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
- **Authorship:** Written by Claude (Anthropic's AI assistant) in collaboration with Jared Eberle.
- Building micro.blog locally pulled from [Chasen's Web Blog](https://web.chasen.dev/2025/06/14/testing-microblog-theme-changes-locally.html)

## License

This theme is released under the [MIT License](LICENSE) — see the disclaimer at the top
regarding support and reuse. Bundled fonts and absorbed plugin code carry their own
licenses; see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
