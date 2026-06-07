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
> You are welcome to fork it under the MIT License and adapt it yourself — but if you
> do, **you are entirely on your own.** It is tightly coupled to my specific
> micro.blog configuration, installed plugins, and content categories, and is not
> intended to be a general-purpose, reusable theme.

<!-- ⚠️ ⚠️ ⚠️ -->

# Micro Claude, a micro.blog theme

A custom Hugo theme for [eberle.blog](https://eberle.blog) that mirrors the style of
[jaredeberle.org](https://jaredeberle.org): Solarized Light palette, clean sans-serif
typography, and dark mode via `prefers-color-scheme`.

- **Repo:** `github.com/jleberle/micro-claude` — micro.blog pulls from the **`master`** branch.
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
3. **Currently Reading** — from the bookshelf plugin's data (`.Site.Data.bookshelves`).
4. **Books | Movies** — two columns of recent posts in the `Books` / `Movies` categories.
5. **Highlights** — up to 10 recent posts in the `Highlights` category.

Category names are matched **exactly and case-sensitively** (`Status`, `Books`, `Movies`,
`Highlights`). Rename a category in micro.blog and its section silently goes empty.

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
- **`microblog_head.html`** is injected by micro.blog at the platform level — it is *not* in
  this repo (and is `.gitignore`d as a local-dev stub). Do not commit a stub.
- **CSS targets both `#site-header`/`.site-header`** (and footer/main equivalents) because
  micro.blog's base template uses id-based hooks while this theme's partials use classes.

See `CLAUDE.md` for the full platform-behavior notes and the local 0.158 reproduction setup.

## Installed plugins

These micro.blog plugins are installed alongside the theme:

| Plugin | Role |
|---|---|
| [microdotblog-bookshelf-shortcode](https://github.com/kottkrig/microdotblog-bookshelf-shortcode) | Provides `.Site.Data.bookshelves` — **required** for the Currently Reading section |
| [plugin-bookgoals](https://github.com/microdotblog/plugin-bookgoals) | Reading-goals shortcode |
| [plugin-search-page](https://github.com/microdotblog/plugin-search-page) | Search page (see the `list.archivejson.json` override above) |
| [plugin-archive-months](https://github.com/microdotblog/plugin-archive-months) | Groups the archive by year/month |
| [plugin-photos-months](https://github.com/microdotblog/plugin-photos-months) | Groups the photos archive by year/month |
| [plugin-cc](https://github.com/microdotblog/plugin-cc) | Creative Commons license tag (injects via `custom_footer.html`) |
| [wayback-link-preserver](https://github.com/gunnarr/wayback-link-preserver) | Wayback fallbacks for broken links |
| [mbplugin-youtube-nocookie](https://github.com/flschr/mbplugin-youtube-nocookie) | Privacy-friendly YouTube embeds |

## Hugo compatibility

micro.blog recommends targeting **Hugo 0.91** for themes/plugins but runs **0.158** in
production. APIs removed between those versions are latent landmines that only surface on a
**full rebuild** (fast-publish serves cached output). Prefer APIs valid on **both** versions
(e.g. `.Site.Params.author.avatar`, not the removed `.Site.Author.avatar`).

Known current-version notes:
- `og:locale` is hardcoded to `en_US` because micro.blog's 0.158 returns the literal `-` for
  the deprecated `.Site.LanguageCode`.
- Future landmines (deprecated on 0.158, not yet removed): `.Site.LanguageCode`, `.Site.Data`,
  and the config keys `languageCode` / `paginate`.

Full details, root-cause history, and the pinned-`hugo-0.158` local reproduction live in `CLAUDE.md`.

---

## Credits

- **Color palette:** [Solarized](https://ethanschoonover.com/solarized/) by Ethan Schoonover,
  used under the [MIT License](https://github.com/altercation/solarized/blob/master/LICENSE).
  The Solarized hues are adapted here as CSS custom properties; no Solarized source files are bundled.
- **Authorship:** Written by Claude (Anthropic's AI assistant) in collaboration with Jared Eberle.

## License

This theme is released under the [MIT License](LICENSE) — see the disclaimer at the top
regarding support and reuse.
