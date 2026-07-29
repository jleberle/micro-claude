---
date: 2026-01-06T00:00:00Z
categories: ["Movies"]
---
Fixture Movie

A short review line, to exercise the movie title/review split and the
TMDB-link-not-found fallback (this post has no poster `<img>` or TMDB link).
The blank line above is load-bearing: `plainify` collapses a same-paragraph
soft line break to a space, so only an actual paragraph break (blank line, two
separate `<p>` tags) reproduces the "review on its own line" shape the split
in index.html depends on.
