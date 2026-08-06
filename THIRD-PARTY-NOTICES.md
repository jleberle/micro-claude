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

Four plugins were reimplemented within the theme and uninstalled on 2026-08-05.
Their functionality now originates in the following files:

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

### microdotblog-bookshelf-shortcode

`kottkrig/microdotblog-bookshelf-shortcode` publishes no license file and no
license statement. No rights in that work are claimed or relied upon here.

`layouts/shortcodes/bookshelf.html` is an independent implementation. It shares
with the plugin only its interface: the call signature (`shelf` and `variant`,
defaulting to `currentlyreading` and `list`), retained for compatibility with
existing content, and the structure of the `.Site.Data.bookshelves` data, which
is defined by Micro.blog. Markup, class names, accessibility handling,
lazy-loading, ISBN handling and error behavior are original to this theme.
