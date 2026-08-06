# Third-party notices

This theme is MIT-licensed (see `LICENSE`). It also bundles fonts and code
derived from other projects, listed here with their own terms.

---

## Fonts

Both are bundled as subsetted WOFF2 files in `static/fonts/`, with their full
license texts beside them.

### Charter — `charter-400-latin.woff2`, `charter-400i-latin.woff2`

Designed by Matthew Carter. Built from Michael Sharpe's **XCharter**, an
extension of Bitstream Charter, and used under the original Bitstream Charter
license (`static/fonts/charter-LICENSE.txt`).

That license grants permission to use, copy, modify, sublicense, sell and
redistribute the fonts, on the condition that the notice is left intact on all
copies and that Bitstream's trademark is acknowledged:

> BITSTREAM CHARTER is a registered trademark of Bitstream Inc.

### Fraunces — `fraunces-600-latin.woff2`

Copyright 2018 The Fraunces Project Authors
(<https://github.com/undercasetype/Fraunces>), licensed under the SIL Open Font
License, Version 1.1 (`static/fonts/OFL.txt`).

---

## Absorbed micro.blog plugins

Four plugins were reimplemented inside the theme and uninstalled on 2026-08-05,
so their behavior survives without the plugin. What each contributed:

| Origin | Now lives in |
|---|---|
| [plugin-search-page](https://github.com/microdotblog/plugin-search-page) | `content/search.md`, `static/js/search.js`, `layouts/list.archivejson.json` |
| [plugin-bookgoals](https://github.com/microdotblog/plugin-bookgoals) | `layouts/shortcodes/readinggoals.html`, `layouts/shortcodes/bookgoals.html`, `layouts/partials/reading-goals.html` |
| [plugin-cc](https://github.com/microdotblog/plugin-cc) | `layouts/partials/head.html` (the `rel="license"` tag) |
| [microdotblog-bookshelf-shortcode](https://github.com/kottkrig/microdotblog-bookshelf-shortcode) | `layouts/shortcodes/bookshelf.html` |

The three Micro.blog plugins are MIT-licensed. Their notices are reproduced
below as that license requires.

### plugin-search-page

> MIT License
>
> Copyright (c) 2020 Micro.blog

### plugin-bookgoals

> MIT License
>
> Copyright (c) 2022 Micro.blog

### plugin-cc

> MIT License
>
> Copyright (c) 2023 Micro.blog

All three carry the standard MIT terms:

> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.

### microdotblog-bookshelf-shortcode — NO LICENSE

`kottkrig/microdotblog-bookshelf-shortcode` publishes **no license file and no
license statement**, which under default copyright means all rights reserved —
it grants no permission to copy, modify or redistribute, and crediting it here
does not substitute for one.

`layouts/shortcodes/bookshelf.html` is an independent reimplementation, not a
copy. What it shares with the original is interface rather than expression: the
call signature (`shelf` / `variant`, defaulting to `currentlyreading` and
`list`), deliberately preserved so existing content kept working, and the shape
of the data it reads, which is defined by Micro.blog rather than by the plugin.
The markup, class names, accessibility handling, lazy-loading, ISBN guarding and
error behavior are all written here and differ throughout.

Recorded plainly so the position is documented rather than assumed. If the
upstream author would prefer this not exist, or adds a license we can rely on,
that is worth honoring either way.
