# micro-claude theme — session notes

Operational knowledge for working on this repo: platform rules that are
counterintuitive, landmines that cost real debugging time, and the verification
habits that catch them.

**What belongs here:** a fact a future session would otherwise get wrong or spend
hours re-deriving — especially where the obvious answer is the wrong one.

**What does NOT:** per-change rationale (put it in a code comment next to the
code), what a file does (README.md), or a log of what an audit changed (git
history). This file reached 1,810 lines because every pass appended its own
changelog; it was cut to ~370 on 2026-08-07. **Adding a section should be rare.
If you are about to append "## <Something> pass (<date>)", you almost certainly
want a code comment and a commit message instead.**

## What this repo is

A custom Hugo theme for Jared Eberle's micro.blog at **eberle.blog**.

- GitHub `github.com/jleberle/micro-claude`; micro.blog pulls **`main`**. Always
  `git push origin main`. (Older notes said "master" — stale, and a stray remote
  `master` was deleted 2026-06-10.)
- Hugo: micro.blog production runs **0.158**; Homebrew local is newer.
- micro.blog username **eberle** (avatar URL uses this); personal site / Bluesky /
  LibraryThing handle is **jaredeberle**. `jaredeberle/avatar.jpg` is a 404.
- README.md covers structure and features for a reader. This file is for the
  things that will bite you.

### Installed as a PLUGIN, not a Theme

`opengraph.html` is **only loaded for plugins** — as the active Theme, micro.blog
never renders the OG card. As a plugin it overlays the active theme and the card
works. Consequence: `plugin.json` `fields` become backend settings.

## Platform rules that are not guessable

These were each learned the expensive way. Do not re-derive them from a local
test — see "Verification discipline" for why local tests have lied here twice.

### static/ fills a gap; layouts/ overrides a default

- micro.blog serves a theme/plugin `static/` file only at paths the platform has
  **no default** for: `fonts/`, `js/`, `humans.txt`, `.well-known/security.txt`
  (all confirmed 200 live — dot-paths do get served).
- Where the platform **does** ship a default — `robots.txt` — a `static/` copy
  never wins. Only `layouts/robots.txt` overrides it, because micro.blog has
  Hugo's robots.txt generation enabled. This file spent its first day in
  `static/` and served nothing.
- `testsite/config.toml` sets `enableRobotsTXT = true` so CI actually renders it;
  without that, a move back to `static/` would be invisible.
- `layouts/robots.txt` is a Hugo **template** — Go delimiters are live even inside
  its `#` comments. Writing a literal pair of double braces there breaks the
  build ("missing value for command"). Describe them, don't type them.

### CSS goes through Hugo Pipes, from assets/ (moved 2026-08-07)

`static/` is copied **verbatim** — micro.blog minifies HTML output but never
touches static files, and the platform sends no compression, so a static
stylesheet costs its full authored size on the wire. `main.css` therefore lives
in `assets/css/` and `head.html` builds it with
`resources.Get | minify | fingerprint "sha256"`: **43.5 KB → 23.4 KB (46%)**, with
the content hash replacing the old `?theme_seconds` query-string cache-bust.
Verified byte-for-byte feature parity after minification (every `@media`,
`color-mix()`, `:has()`, `var()` and `@font-face` `unicode-range` preserved;
tinycss2 reports 0 parse errors) and the hash is deterministic across rebuilds
and across Hugo versions.

**The `<link>` is wrapped in `with` on purpose.** `head.html` runs on EVERY page,
so an unguarded nil there is worse than a home-node fault — it takes the entire
site down rather than just the homepage and feeds. Guarded, a missing resource
degrades to an unstyled but serving site (verified by deleting the asset and
confirming the build still completes and renders every page).

No SRI: an integrity hash is computed against our build, so if micro.blog ever
re-encoded the file the browser would block the stylesheet outright — an
all-or-nothing failure mode for no real gain on a same-origin asset.

`static/js/search.js` is deliberately NOT piped: it is referenced from
`content/search.md`, a content file rather than a template, so Pipes isn't
reachable without moving that `<script>` into a shortcode. ~2 KB at stake.

### Home-node outputs must live at ROOT layouts/, not _default/

`/archive/` and `/photos/` are **not** section lists — they are the *home node's*
`ArchiveHTML` / `PhotosHTML` output formats, same node family as the HTML page,
RSS and JSON feeds. For the home kind Hugo checks `layouts/list.archivehtml.html`
**before** `layouts/_default/`. micro.blog's default `theme-blank` ships the
root-level copies, so a `_default/` template from a theme *or* plugin never wins.

That is why `plugin-archive-months` / `plugin-photos-months` silently did nothing
(both shipped only `_default/` templates) and why they were uninstalled. Applies
to any home-node output override — feeds, RSD, ArchiveJSON.

**Blast radius:** everything in the home node fails together. A fault in
`index.html`, `list.archivejson.json`, or any home output takes down the homepage
**and both feeds** while every other page renders fine. This is the single most
expensive failure mode in this repo — treat home-node templates as critical.

### Plugin precedence

- **Plugin CSS loads AFTER `main.css`**, so at equal specificity the plugin wins.
  Never restyle a plugin's markup by matching its selectors; either out-specify
  it deliberately or use different class names (this theme does the latter —
  `bookshelf-*`, `bookgoals-cover`).
- **An installed plugin's shortcode BEATS the theme's**, verified in production.
  (An earlier note claimed the opposite, extrapolated from a local test with a
  throwaway second theme — it was wrong.) Absorbing a shortcode does nothing
  until the plugin is uninstalled, and during that window the theme's CSS no
  longer matches the plugin's class names, so its output renders unstyled.
  Uninstall promptly rather than running both.
- **micro.blog RE-INSTALLS a plugin whose shortcode name your content calls.**
  An unknown shortcode is a fatal Hugo error, so the platform reinstates the
  provider. Uninstalling `plugin-bookgoals` while `/reading/` still called
  `{{</* bookgoals */>}}` put it straight back, repeatedly. **Fix: rename, don't
  fight** — hence `shortcodes/readinggoals.html`, a name nothing owns.

### A plugin.json boolean left unchecked overrides a `true` config.json default

Silently disables the feature in production while the local repro still shows it
working. This is how archive photo thumbnails were dead for months. Don't treat a
`config.json` boolean as the effective production value once the same key is also
a backend field.

### Other platform behavior

- **`<style>` tags are stripped** from theme template output. Use `main.css` with
  `:has()` for page-specific rules.
- **`microblog_head.html` is injected by the platform** — not in this repo,
  gitignored as a local dev stub. **Never commit the stub.** Do not guard it with
  `templates.Exists` (platform partials return false and break the feed).
- **micro.blog renders OUR `baseof`/header/footer partials** (verified live), but
  CSS still targets both `#site-header`/`.site-header` (and footer/main) as a
  fallback for the platform's default base template.
- **micro.blog overrides `og:image` on POST pages** with the generated card PNG.
  The theme's avatar fallback therefore only shows on non-post pages.
- **`/archive/index.json` lags builds.** micro.blog copies a previously-rendered
  ArchiveJSON artifact into new builds, so its content can be a generation behind
  while its last-modified is current. **Never diagnose this file from a single
  fetch** — force a rebuild, then re-check.
- **"Raw HTML omitted" WARNs come from micro.blog's GitHub-archiving job**, not
  the site build. That job renders with `unsafe=false`; the real build uses
  `unsafe=true`, which is why live pages are fine. Cosmetic. For book posts the
  raw cover `<img>` is **injected by micro.blog**, not in your markdown, so it
  cannot be edited away. No config fix exists (a theme's `config.json` cannot
  suppress it — see below).
- **Only `params`/`menus`/`outputFormats`/`mediaTypes` merge from a theme's
  `config.json`.** Top-level `markup`/`ignoreLogs`/`minify`/`pluralizeListTitles`
  keys do nothing — confirmed in production, not just locally. Set them in the
  site-root export's own config for local testing.

## Hugo version compatibility

**Target 0.158 — micro.blog's production version. The 0.91 floor was DROPPED
2026-08-07; do not reinstate it.** micro.blog's docs recommend 0.91 as a
compatibility floor for *distributable* themes. This is a single-site personal
theme (see README's disclaimer), micro.blog runs 0.158, 0.158 builds measurably
faster, and there is no scenario in which this site reverts. Holding the floor
was costing a deprecated API in the home node to insure against a ~67-version
downgrade that will never happen.

Still true and still the main hazard: an API **removed** between the version a
template was written for and the one production runs is a latent landmine that
surfaces **only on a full rebuild** (fastpublish serves cache). That is how a
stale `.Site.Author.avatar` in `plugin-search-page` took down the home node in
June 2026.

- **`.Site.Author.*` was removed in 0.156** — use `.Site.Params.author.*`. This
  is the exact bug above.
- **`opengraph.html` is the exception**: Hugo never renders it (it is not a valid
  layout name for any output format). micro.blog's separate, non-Hugo card
  renderer consumes it, where `.Site.Author.avatar` is the *documented, correct*
  variable. Documented vars: `.Site.Author.avatar/.name/.header`,
  `.Site.Title/.BaseURL/.Hostname/.Params`, and post
  `.Title/.Content/.Plain/.Summary/.Permalink/.Date/.Params.photos`. Put colors
  in both the inline `style` and the matching `data-*` attribute.
- **Do NOT migrate to the 0.146+ template layout structure.** The 0.91 floor used
  to be the blocker (new-style root `layouts/single.html`/`list.html` are
  invisible to it); with that gone the reason is now simply risk-without-benefit.
  The old-style tree works on 0.158 via the legacy compat layer, which micro.blog
  cannot drop without breaking theme-blank and every plugin, and the archive/
  photos fix depends on template *lookup order* that a migration would disturb.
  Revisit only if micro.blog migrates theme-blank itself — and re-verify the
  shadowing then.
- `{{ .Title | default .Date.Format "..." }}` is invalid on 0.158 — use an
  explicit `if/else`.
- `{{ else if }}` is **not valid after `{{ with }}`** ("unexpected <if> in
  input") — a fatal build error. Use a variable.
- `.Site.LanguageCode` returns the literal `-` on micro.blog's 0.158, which is
  why `og:locale` is hardcoded `en_US`.

### Data access: use `hugo.Data`, not `.Site.Data` (resolved 2026-08-07)

Formerly the repo's top landmine. `.Site.Data` is deprecated and sat in the home
node, so its eventual removal would have taken the page and both feeds together;
it was held only for 0.91, where `hugo.Data` is fatal. A version gate was **not**
an escape — `ge hugo.Version "0.155.0"` returns **TRUE on 0.91.2** (verified), so
the guarded branch runs anyway and still faults.

With the floor dropped, all four call sites moved to `hugo.Data` (0.155+):
`index.html`, `shortcodes/bookshelf.html`, `shortcodes/{readinggoals,bookgoals}
.html`. Verified byte-identical homepage and `/reading/` output on pinned 0.158.
**Do not "restore compatibility" by reverting these.**

**As of 2026-08-07 this theme has ZERO deprecation warnings**, verified by
building `testsite/` against Hugo 0.164 (six versions ahead of production) — see
the sweep below. Earlier notes listed `.Site.LanguageCode` and the config keys
`languageCode` / `paginate` as pending landmines *here*; that was misleading.
None of the three appear anywhere in this repo's templates or `config.json`
(which ships only `params`). `.Site.LanguageCode` went away when `og:locale` was
hardcoded to `en_US`, and site-level config keys belong to micro.blog's export,
not to us.

### Deprecation sweep — run this on any micro.blog Hugo bump

```bash
hugo -s testsite --gc --logLevel warn 2>&1 | grep -i deprecat
```

Build with a **newer** Hugo than production; deprecations warn for several
versions before removal, so this is the cheap early warning. **Validate the sweep
before trusting a clean result** — temporarily reintroduce a known-deprecated
call (e.g. `.Site.Data`) and confirm it is reported. Done 2026-08-07: the control
fired correctly, so the clean result is real and not a blind test.

## Active landmines

### Deleted RSS-import posts come back

**Micro.blog re-creates any feed item it cannot find a post for.** Deleting an
imported post does not tell the importer to forget it — on the next poll the item
is still in the feed, no post matches, so it imports again. A deletion sticks only
once the item has aged out of the feed window.

**Dedup is on `<link>`, NOT `<guid>`.** So **a published `<link>` must be treated
as immutable.** Any change — URL scheme, a folder rename for a source with no
isbn/doi/access_url, adding or removing a `#started`/`#finished` suffix — creates
a new post for every affected item then in the window.

**Before deleting any duplicate, check whether its item is inside the current
20-item window** (`jaredeberle.org/reading/index.xml`). If it is, deletion will
not stick. Keep the title-slug copy where one exists — it is the newest import.

The guid was fixed source-side (2026-07-27) to key on isbn/doi/access_url, which
stopped *new* duplicates; it does nothing for ones already imported. Theme-side,
`index.html`'s Finished Reading de-dup hides them on the homepage only —
`/archive/`, `/search/` and the feeds still show every copy.

### Duplicate book records in the bookgoals grid

The same *work* appears twice with two **different but adjacent ISBNs** — two
Micro.blog book records, not RSS-import residue (deleting posts and rebuilding
changes nothing). Root cause: the ledger's reading feed emits
`https://micro.blog/books/<isbn>`, and when that ISBN names a different edition
than the record Micro.blog already holds, a second record is created and both
land in the year's goal.

**Durable fix is source-side:** set each `content/sources/*` `isbn` to the edition
Micro.blog already tracks. Correcting an ISBN afterwards is safe — it changes the
guid, but dedup is on `<link>`, and the ISBN is not part of the link.

`partials/reading-goals.html` de-dups by normalized title as a display-level
safety net (author is a tie-breaker, not part of the key — see its comments).

### conversation.js must not get `defer`/`async`

It builds the reply form with `document.write()`, which destroys the document if
it runs after parse. This is the obvious-looking "render-blocking script" fix and
it would break every post page.

### wayback-link-preserver breaks flex layouts

It inserts its badge as a **sibling** of the flagged link, making it a flex item
in `.bookgoals` and knocking the row off its column pitch. Hidden via
`.bookgoals .wlp-broken-badge` (0,2,0 — needed because plugin CSS loads after
`main.css`). Scoped to `.bookgoals` deliberately: in prose the badge is inline and
useful. It also **false-positives** (no-cors fetch, 8s timeout, cached a day) and
is **invisible to `curl`** — injected at runtime, so fetched HTML looks perfect.
Assume the same hazard for any future flex/grid container holding links.

### Category NAMES vs SLUGS

Live URLs are `/categories/finished/` and `/categories/started/`, but those are
**custom slugs**. The category names on posts are the full strings
(`Finished Reading`, `Started Reading`) — verified from `feed.json` tags. The
`config.json` values are the *names* and must not be changed to the slugs.

This is why `index.html` resolves category links by term **title →
`.RelPermalink`** rather than `urlize`-ing the name: `urlize "Finished Reading"`
yields `/categories/finished-reading/`, which **404s on this site**. The
`| default (printf "/categories/%s" ... | urlize)` fallback would emit those 404
URLs; fine as a last resort, but it is not a safe path here.

## Homepage (layouts/index.html)

Sections: intro → status → currently reading → finished reading | movies →
highlights. Structure and behavior are documented in README.md; the logic is
commented inline. Only the non-obvious contracts are here.

- **Never cast a backend field with `int`** — it is FATAL on a malformed value,
  even `"5 "` with a trailing space, and a fault here kills the home node. Use
  `partials/int-param.html`, which accepts digits-only and otherwise keeps a
  hardcoded fallback. It also rejects leading zeros because Go parses `"010"` as
  **octal**.
- **Cross-repo contract with `~/git/website`'s `layouts/reading.rss.xml`:**
  - The `Started reading:` / `Finished reading:` prefixes are generated there,
    and Micro.blog's autotagging keys off the same strings. A rewording silently
    empties these sections with **no error on either side**. That repo's
    `scripts/checks/feed-lint.py` asserts the prefixes to catch it.
  - **`📚` is a delimiter, not decoration.** The feed packs headline + notes into
    one `<p>`; native Micro.blog posts put the review on its own line. The split
    tries the newline first, then `📚`. Moving it runs notes into the title link.
  - **Pairing key:** ISBN first, else the normalized `<title> by <author>`
    segment, which must stay byte-identical between a source's started and
    finished items or the started entry never leaves Currently Reading.
- **"Currently reading:" counts as started.** The detector accepts
  `(?i)^(Started|Currently) reading:`. **Two edits must stay in sync** — widening
  the detector without widening the `$label` prefix strip leaves the verb in the
  row *and* produces a key no finished post can match, so it never retires.
- Currently Reading merges started-reading **posts** with the Micro.blog
  **bookshelf** (so a shelf book with no post still appears). Shelf books carry
  no date, so they append after dated entries. Cap applies **after** merging.

## Local testing

### Faithful 0.158 reproduction (matches a micro.blog full rebuild)

This is what found the full-rebuild bug. Far closer to production than
`hugo server` because it includes the real platform theme and all plugins.

**The test folder is NOT persisted — recreate it before each run.** Get a fresh
micro.blog export for the site root, add the gitignored `microblog_head.html`
stub, and clone each installed plugin into `themes/`.

```bash
# The pinned binary keeps disappearing (macOS ships only a .pkg now); re-fetch:
curl -sL -o h158.pkg https://github.com/gohugoio/hugo/releases/download/v0.158.0/hugo_extended_0.158.0_darwin-universal.pkg
pkgutil --expand h158.pkg h158exp && cd h158exp && cat Payload | gunzip -dc | cpio -i   # → ./hugo

~/.local/bin/hugo-0.158 -s <siteroot> --themesDir=<siteroot>/themes --gc \
  --theme=micro-theme,wayback-link-preserver,mbplugin-youtube-nocookie,theme-blank
```

**0.158 is the only version worth testing against** — the 0.91 leg of the old
test matrix is retired with the floor (see "Hugo version compatibility"). If you
ever need a second version, make it a *newer* one, to catch the next round of
removals before micro.blog upgrades into them.

Load YOUR theme first, then every installed plugin, then **theme-blank last** —
it is micro.blog's real default/fallback theme (baseof, microblog_head, rss.xml,
and all home output-format templates).

Two remaining installed plugins: **wayback-link-preserver** and
**flschr/mbplugin-youtube-nocookie**. Both are real software this theme has no
intention of reproducing. Four others were **absorbed** into the theme
(plugin-search-page, plugin-bookgoals, plugin-cc, bookshelf-shortcode — see
THIRD-PARTY-NOTICES.md) and three **superseded** and uninstalled outright
(plugin-archive-months, plugin-photos-months, and an AI-blocking robots.txt
plugin replaced by `layouts/robots.txt`).

Note: the local CLI aborts the whole build on the first render error (public/
ends up empty); micro.blog tolerates per-node failures and ships the rest, which
is why production showed only home+feeds gone.

### CI build check

`.github/workflows/build-check.yml` builds this theme standalone against
`testsite/` on every push/PR to `main`, using the checksum-pinned production Hugo,
and fails on fatal template errors or leaked error text.

**It is a smoke test, not the faithful repro** — no plugins, no theme-blank, so it
cannot catch a cross-plugin conflict (the actual cause of the June incident). What
it does catch cheaply is a template fatally broken on its own — same blast radius,
different trigger.

`testsite/`'s `outputFormats` are a **reconstruction** from the path/baseName
facts recorded here, not micro.blog's real export config — enough to route the
home-node build through the archive/photos/archivejson templates, which is the
point. Its `layouts/partials/microblog_head.html` stub is fine (a separate fixture
site, unlike a stub inside the theme's own `layouts/`). CI prints
`WARN bookshelf: unknown variant "nonsense"` every run — that is a fixture
assertion, not a problem.

## Verification discipline

Habits that caught real errors here. Each of these produced a confidently wrong
conclusion at least once.

- **Build WITHOUT `--minify` when checking HTML escaping.** Hugo's minifier
  rewrites `&amp;` to a bare `&` in attribute values (legal), and production is
  minified too — so a minified build makes correct and broken escaping look
  identical. This produced a wrong diagnosis in the 2026-08-07 audit.
- **A local Hugo test is not evidence for "which file wins" questions.** Locally a
  theme's `static/robots.txt` beats Hugo's generated one — the *opposite* of the
  platform. Local `--theme` ordering results have now been wrong about production
  **twice** (robots.txt, and shortcode precedence). Treat them as suggestive only.
- **Don't diagnose `/archive/index.json` from one fetch** — see "lags builds".
- **Parse the output, don't just check the exit code.** The JSON-LD
  double-encoding bug (fixed with `safeJS`) built cleanly and produced malformed
  output; only parsing the rendered block as JSON caught it. Same for the entity
  bugs found in 2026-08-07.
- **Runtime-injected markup is invisible to `curl`** (wayback badges,
  `.microblog_reply_form`). A screenshot is the only evidence.
- Verify accessibility contrast with the relative-luminance formula, not by eye.

## Accepted divergences and open items

Deliberate — don't "fix" these without reading why:

- **No dark mode.** Removed 2026-07-07. `~/git/website` has since re-gained a dark
  palette, so the original "the main site has no dark theme" rationale is stale as
  a fact — but re-adding one means re-auditing every composited `color-mix()`
  surface here. That is its own piece of work.
- **`--fog-driftgray` diverges from the main site** (`#4c545a` vs `#585f65`). This
  theme uses that color at smaller meta-text sizes, where AA needs 4.5:1, not the
  3:1 large-text minimum. Second AA-driven divergence on this token, not drift.
- **`/reading/` Currently Reading is shelf-only** and does not merge started-
  reading posts like the homepage does. Porting the merge was offered and
  declined. `shortcodes/bookshelf.html` is kept but **currently uncalled and
  unstyled** — its CSS was removed 2026-08-06; restore from git history first.
- **Base prose is 1rem = 17px** vs the main site's 19.2px, and heading margins mix
  rem with em padding. Both are documented boundaries — changing the base cascades
  through every rem value in `main.css`.
- **Archive thumbnails crop square** (`aspect-ratio: 1`), matching `/photos/`.
  Drop that line if uncropped thumbs are wanted.
- **Image-bearing paragraphs are exempt from the 60ch measure cap**, and
  micro.blog puts captions in the same `<p>` as the image — so those captions run
  the full column. Accepted; the alternative is every photo losing a quarter of
  its width.

Open, not theme-fixable:

- **13 of 14 photo posts have no alt text** on their body image. micro.blog's
  editor supports it; nothing in the theme can supply it.
- **No compression, no `Cache-Control`, no security response headers** from the
  platform (`main.css` ships ~43 KB uncompressed where gzip would be ~6 KB).
  Per-blog headers are impossible on micro.blog, which is why the CSP is delivered
  via `<meta>` and why HSTS/nosniff/Permissions-Policy/frame-ancestors are
  unavailable. `ETag`/`Last-Modified` are sent.
- Full rebuilds are **safe** — the June 2026 landmine is gone at the source
  (plugin-search-page uninstalled), not merely shadowed. **Keep
  `layouts/list.archivejson.json`**: `/search/` depends on its full-text index.
