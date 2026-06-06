# micro-claude theme — Claude session notes
Last updated: 2026-06-06

## What this repo is
A custom Hugo theme for Jared Eberle's micro.blog at **eberle.blog**.
- GitHub: `github.com/jleberle/micro-claude`
- micro.blog pulls from the **master** branch (only branch — push to master)
- Local dev: `hugo server` from `/Users/jaredeberle/git/microblog-theme/`
- Hugo locally: 0.162 | micro.blog production: **0.158**

## Identities to keep straight
- micro.blog username: **eberle** (hosts eberle.blog, avatar URL uses this)
- Personal site / Bluesky / LibraryThing handle: **jaredeberle**
- Avatar: `https://micro.blog/eberle/avatar.jpg` (jaredeberle/avatar.jpg is 404)
- Always push: `git push origin master`

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
### Manual full rebuild (Hugo 0.158) — KNOWN BUG, reported to micro.blog
- Triggering "full rebuild" from micro.blog interface causes **Feed: Not found**
- Root cause: Hugo 0.158 PR #14601 changed template lookup precedence for media
  types, breaking resolution of micro.blog's platform-injected RSS template during
  non-segmented builds
- Fastpublish (normal posting) works fine — feed generates correctly
- Hugo 0.117 full rebuild also works fine
- **Do not trigger manual full rebuild** until micro.blog fixes this
- Reported to micro.blog support with full diagnosis

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
- `hugo.Data` introduced ~0.155 — **use `.Site.Data` instead** for 0.117 compat
  (generates a deprecation WARN on 0.158 but not an error)
- `.Site.Author.*` removed in 0.162 — use `.Site.Params.author.*`
- `{{ .Title | default .Date.Format "January 2, 2006" }}` invalid in 0.158
  — use `{{ if .Title }}{{ .Title }}{{ else }}{{ .Date.Format "..." }}{{ end }}`
- `opengraph.html` in layouts/ breaks feed output format generation in 0.158
  — keep it deleted

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

## Things still outstanding / to watch
- **footer.html** custom links (RSS · Micro.blog · Theme · Codeberg) — confirm
  these are rendering on the live site; if not, micro.blog's default footer is
  being used instead of ours
- **Highlights post not appearing on homepage** — suspected fastpublish timing
  issue; most recent Highlights post shows on category page but not homepage.
  Trigger a full publish cycle to test.
- **Manual full rebuild** — avoid until micro.blog fixes the 0.158 RSS bug

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
