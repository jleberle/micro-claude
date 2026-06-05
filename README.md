# Eberle — micro.blog theme

A micro.blog theme that mirrors the style of [jaredeberle.org](https://jaredeberle.org): Solarized Light palette, clean sans-serif typography, dark mode via `prefers-color-scheme`.

## Installing

1. In micro.blog go to **Posts → Design → Edit Custom Themes → New Theme**.
2. Connect this repo via the GitHub integration.
3. Set the theme as active.
4. Set Hugo version to **0.158** in micro.blog settings.

## File structure

```
assets/
  css/
    main.css                      — All styles (minified + fingerprinted at build time)
layouts/
  _default/
    baseof.html                   — Base HTML shell (includes skip-to-content link)
    list.html                     — Category / taxonomy list pages
    single.html                   — Individual post
  index.html                      — Homepage
  partials/
    head.html                     — <head> tag, CSS pipeline, lite-youtube hook
    header.html                   — Site nav bar (text-only title, no avatar)
    footer.html                   — Site footer with RSS, Micro.blog, and theme links
    intro.html                    — Homepage bio/social section
    custom_footer.html            — Empty hook (used by plugin-cc and others)
    microblog_head.html           — Overrides micro.blog default; provides feed links,
                                    canonical URL, fediverse creator meta
    microblog_syndication.html    — Syndication links on posts
```

## Customization

Colors are all CSS custom properties in `assets/css/main.css` under `:root`. Swap them to adjust the palette without touching layout code.

### Homepage intro

The intro section at the top of the homepage pulls from:
- **Avatar** — `https://micro.blog/{username}/avatar.jpg` (automatic)
- **Bio** — `.Site.Params.bio` → `.Site.Params.itunes_description` → page `.Content` (first non-empty wins)
- **Social links** — **hardcoded** in `layouts/partials/intro.html`

> ⚠️ If you fork or reuse this theme, update the social links in `layouts/partials/intro.html` — they are set to Jared Eberle's personal accounts and will not update automatically.

The section only renders if a bio is present.

### Homepage sections

The homepage displays in order:
1. **Intro** — bio and social links
2. **Status** — latest post from the `Status` category
3. **Currently Reading** — from bookshelf plugin data (`Site.Data.bookshelves.currentlyreading`)
4. **Books | Movies** — two columns; books shows 5 most recent `Books` category posts with cover thumbnail and truncated summary; movies shows 6 most recent `Movies` category posts with date and review snippet
5. **Highlights** — up to 10 most recent posts from the `Highlights` category

---

## Dependencies

### Required plugins

These plugins must be installed and active for full functionality:

| Plugin | Purpose | What breaks without it |
|---|---|---|
| [microdotblog-bookshelf-shortcode](https://github.com/kottkrig/microdotblog-bookshelf-shortcode) | Provides `Site.Data.bookshelves` | Currently reading section disappears silently (build warns via `warnf`) |

### Compatible plugins

These plugins are installed and work with the theme without any changes:

- **[plugin-opengraph-basics](https://github.com/microdotblog/plugin-opengraph-basics)** — injects via `microblog_head.html`
- **[plugin-cc](https://github.com/microdotblog/plugin-cc)** — injects via `custom_footer.html`
- **[plugin-barefoot](https://github.com/microdotblog/plugin-barefoot)** — self-contained footnote JS
- **[plugin-osm-embeds](https://github.com/flschr/mbplugin-osm-embeds)** — shortcode only
- **[micro-blog-lite-youtube](https://github.com/rknightuk/micro-blog-lite-youtube)** — loaded via conditional `partial "lite-youtube.html"` in `head.html`; targets `.post-content` class which this theme uses
- **[plugin-archive-months](https://github.com/microdotblog/plugin-archive-months)** — provides `list.archivehtml.html`; theme intentionally has no competing version
- **[plugin-photos-months](https://github.com/microdotblog/plugin-photos-months)** — provides `list.photoshtml.html`; theme intentionally has no competing version
- **[plugin-search-page](https://github.com/microdotblog/plugin-search-page)** — self-contained
- **[plugin-nocgpt](https://github.com/jmillerv/plugin-nocgpt)** — adds `robots.txt` only
- **[wayback-link-preserver](https://github.com/gunnarr/wayback-link-preserver)** — injects via `microblog_head.html`
- **[plugin-bookgoals](https://github.com/microdotblog/plugin-bookgoals)** — shortcode only; CSS for `.bookgoals` layout is embedded in `main.css`

### Embedded plugin CSS

The following plugin stylesheets are embedded directly in `main.css` to guarantee they load regardless of micro.blog's static file serving:

| Plugin | Classes | Note |
|---|---|---|
| microdotblog-bookshelf-shortcode | `.bookshelf`, `.bookshelf__cover`, etc. | Both list and grid variants; list variant forced to grid layout |
| plugin-bookgoals | `.bookgoals`, `.cover` | Fixed 100×120px covers in flex-wrap grid |

If either plugin updates its CSS, `main.css` should be updated to match.

---

## Known maintenance areas

### Hugo version

The theme targets **Hugo 0.158** and uses features not available in older versions:

- `resources.Get | minify | fingerprint` (Hugo Pipes) — if micro.blog drops Hugo Pipes support, revert `head.html` to a plain `<link>` tag and move `assets/css/main.css` back to `static/css/main.css`
- `partialCached` — safe across all modern Hugo versions
- `.Truncated` — available since Hugo 0.45
- `warnf` — available since Hugo 0.62

### CSS pipeline

`assets/css/main.css` is processed through Hugo Pipes at build time. If `resources.Get` stops working, the site will fail to build. Fallback:

```html
<link rel="stylesheet" href="{{ "css/main.css" | relURL }}?{{ .Site.Params.theme_seconds }}">
```

Move `assets/css/main.css` to `static/css/main.css` alongside this change.

### Homepage category filtering

The homepage filters posts by category name (exact string match): `"Status"`, `"Books"`, `"Movies"`, `"Highlights"`. If any of these category names change in micro.blog, the corresponding section will silently show no posts. Category names are case-sensitive.

### Homepage intro bio

The bio text is pulled from `.Site.Params.bio` first, then `.Site.Params.itunes_description`, then page `.Content`. micro.blog's exact param name for the About Me field is not publicly documented and may change. If the intro disappears, check which param micro.blog is currently using for the user bio.

### Books section — bookshelf data

The currently reading section reads from `.Site.Data.bookshelves.currentlyreading`. This data file is generated by micro.blog when the bookshelf plugin is active. If the plugin is deactivated, the section disappears. If a book is added to the shelf but the site hasn't rebuilt, it won't appear — publishing any post triggers a rebuild.

### Books section — cover thumbnails

Cover images in the books column are extracted from post content using `findRE` to pull the first `<img>` tag. If micro.blog changes how the Watched/bookshelf plugin formats post content (e.g. stops embedding a cover image in the post body), thumbnails will disappear but the rest of the entry will continue to work.

### Movie entry formatting

Movie post content is run through `plainify | htmlUnescape` to strip HTML and decode entities. This works because micro.blog's Watched plugin generates plain-text-style content. If the plugin changes its output format, the movie entries may display incorrectly.

### `microblog_head.html` override

The theme provides its own `microblog_head.html` partial (replacing micro.blog's default) to avoid the deprecated `.Site.Author` variable. This partial provides:

- RSS and JSON feed `<link>` tags
- Canonical URL
- Fediverse creator meta (if `fediverse_creator` param is set)

If micro.blog adds new required tags to their default `microblog_head.html` in the future, this theme's override will not pick them up automatically. Check micro.blog release notes when upgrading Hugo versions.

### Plugin injection points

Plugins that inject into the `<head>` via `microblog_head.html` (e.g. opengraph-basics, wayback-link-preserver) rely on micro.blog's plugin merging system. Since the theme overrides `microblog_head.html`, those plugins must be compatible with micro.blog's multi-source partial resolution. If a plugin stops working in the head, check whether it depends on overriding `microblog_head.html` directly.

### Accessibility

- Skip-to-content link is present but visually hidden until focused — test with keyboard navigation if modifying the header
- `aria-label` attributes on all `<nav>` elements — update if nav structure changes
- `aria-label` on "Read more" and "Permalink" links includes post title/date for screen reader context
- `:focus-visible` outline uses `var(--link)` color — verify contrast if changing the color palette
- Solarized Light secondary text (`#6c6c6c` on `#fffcf2`) is borderline at WCAG 2.1 AA for small text sizes
