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
[jaredeberle.org](https://jaredeberle.org): Solarized Light palette, clean sans-serif
typography, and dark mode via `prefers-color-scheme`.

- **Repo:** `github.com/jleberle/micro-claude` — micro.blog pulls from the **`main`** branch.
- **Hugo:** micro.blog runs **0.158** in production. Templates are kept compatible with
  micro.blog's recommended **0.91** floor as well (see [Hugo compatibility](#hugo-compatibility)).

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
  _default/
    baseof.html              page skeleton (micro.blog may override with its own base)
    list.html                category / section list pages
    list.archivehtml.html    archive page (fixes Hugo 0.158 Date.Format syntax)
    list.archivejson.json    archive JSON output — overrides plugin-search-page's
                             broken copy (see "Theme overrides" below)
    single.html              generic single page
  post/
    single.html              post pages (microformats + categories)
  section/
    replies.html             /replies/ page
  partials/
    head.html                <head>: meta/OG/Twitter tags, CSS link, microblog_head call
    header.html              site header (avatar hidden on homepage via CSS)
    footer.html              custom footer: RSS · Micro.blog · Theme · Codeberg
    intro.html               homepage bio card: avatar + bio + social links
    custom_footer.html       intentionally blank override hook (used by plugins)
  index.html                 homepage
  opengraph.html             OG card template (rendered by micro.blog's card renderer)
static/
  css/main.css               all styling — Solarized Light palette
config.json                  Hugo config + local-dev params
plugin.json                  micro.blog plugin metadata + editable settings fields
theme.toml                   theme metadata
```

## Homepage sections

`layouts/index.html` renders, in order:

1. **Intro card** — avatar + bio + social links (`partials/intro.html`).
2. **Status** — most recent post in the `Status` category.
3. **Currently Reading** — two sources merged into one list: imported `Started reading:`
   posts with no matching finished entry (dated, newest first), followed by Micro.blog's
   own **Currently Reading bookshelf** (`.Site.Data.bookshelves`, undated, in shelf order)
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

All colors are CSS custom properties at the top of `static/css/main.css`. Swap them to
re-palette without touching layout code. (`main.css` lives in `static/`, not `assets/` — it
is served directly and cache-busted with `?{{ .Site.Params.theme_seconds }}`, no Hugo Pipes.)

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

micro.blog recommends targeting **Hugo 0.91** for themes/plugins but runs **0.158** in
production. APIs removed between those versions are latent landmines that only surface on a
**full rebuild** (fast-publish serves cached output). Prefer APIs valid on **both** versions
(e.g. `.Site.Params.author.avatar`, not the removed `.Site.Author.avatar`).

Known current-version notes:
- `.Site.Data` (the bookshelf merge in `index.html`) is **deprecated but deliberate**: it is
  the only accessor valid on both 0.91 and 0.158, since `hugo.Data` is fatal on 0.91. Note
  that gating it on `ge hugo.Version "0.155.0"` does **not** work — that comparison returns
  true on 0.91.2. Swap to `hugo.Data` if micro.blog ever ships a Hugo that removes it.
- `og:locale` is hardcoded to `en_US` because micro.blog's 0.158 returns the literal `-` for
  the deprecated `.Site.LanguageCode`.
- Future landmines (deprecated on 0.158, not yet removed): `.Site.LanguageCode`, `.Site.Data`,
  and the config keys `languageCode` / `paginate`.

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
