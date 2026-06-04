# Eberle — micro.blog theme

A micro.blog theme that mirrors the style of [jaredeberle.org](https://jaredeberle.org): Solarized Light palette, clean sans-serif typography, dark mode via `prefers-color-scheme`.

## Installing

1. In micro.blog go to **Posts → Design → Edit Custom Themes → New Theme**.
2. Upload all files preserving the folder structure, or connect this repo via the GitHub integration.
3. Set the theme as active.

## File structure

```
custom.css                        — All styles (import via microblog_head.html)
layouts/
  _default/
    baseof.html                   — Base HTML shell
    list.html                     — Post list / home feed
    single.html                   — Individual post
  list.archivehtml.html           — /archive page
  list.photoshtml.html            — /photos grid
  partials/
    head.html                     — <head> tag
    header.html                   — Site nav bar
    footer.html                   — Site footer
    custom_footer.html            — Empty hook for overrides
    microblog_head.html           — micro.blog required meta/links
    microblog_syndication.html    — Syndication links on posts
```

## Customization

Colors are all CSS custom properties in `custom.css` under `:root`. Swap them to adjust the palette without touching layout code.

The header shows your micro.blog avatar automatically via `https://micro.blog/{username}/avatar.jpg`.
