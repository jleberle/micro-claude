#!/usr/bin/env python3
"""
Synthesize a Hugo content tree from a micro.blog feed.json backup.

The GitHub backup at github.com/jleberle/microblog is NOT a Hugo export — it
holds feed.json, a rendered index.html and uploads/. There is no content/ tree
and no config. This reconstructs the former from feed.json so the faithful local
repro can run against real posts instead of the 13-post CI fixture.

Derivations, and why each one matters to a template here:

  slug/date   from the item url (/YYYY/MM/DD/slug.html) and date_published.
              Reproduces micro.blog's permalink shape, which archive/index.json
              and index.html's permalink-keyed de-dup both depend on.
  categories  from tags. These are the full NAMES ("Finished Reading"), not the
              URL slugs — see CLAUDE.md, this is the distinction that makes
              urlize-ing them produce 404s.
  books       ISBNs scraped from micro.blog/books/<isbn> links. micro.blog
              supplies this as structured front matter; deriving it exercises
              index.html's primary path rather than its content-scraping
              fallback.
  photos      uploads.micro.blog image sources. Drives /photos/, the archive
              thumbnails and the og:image branch in head.html.

Body is content_text verbatim — the original markdown INCLUDING micro.blog's
injected cover <img>. That injection is not in the authored source, but it is
present in what the platform renders, and index.html's movie-poster extraction
parses it. Keeping it makes the local render match production.

NOT derivable from the backup, and therefore still fixtures or absent:
data/bookshelves.json, data/bookgoals.json (micro.blog generates them at build
time) and every backend plugin field value.
"""
import html
import json
import os
import re
import shutil
import sys

IMG_SRC = re.compile(r'<img[^>]+src="([^"]+)"')
ISBN_LINK = re.compile(r'micro\.blog/books/(\d[\dXx]*)')
URL_PARTS = re.compile(r'/(\d{4})/(\d{2})/(\d{2})/([^/]+?)\.html')


def toml_str(s):
    return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"')


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: feed-to-content.py <feed.json> <site-dir>")
    feed, out = sys.argv[1], sys.argv[2]
    items = json.load(open(feed))["items"]

    postdir = os.path.join(out, "content", "post")
    shutil.rmtree(postdir, ignore_errors=True)
    os.makedirs(postdir)

    stats = dict(written=0, skipped=0, titled=0, tagged=0, books=0, photos=0)
    for it in items:
        m = URL_PARTS.search(it.get("url", ""))
        if not m:
            stats["skipped"] += 1
            continue
        year, month, day, slug = m.groups()

        fm = ["---", "date: %s" % it["date_published"], "slug: %s" % toml_str(slug)]
        if it.get("title"):
            # feed.json HTML-escapes titles (1 of 49 here carries &#39;), but Hugo
            # front matter is plain text. Decoding keeps the reconstruction honest
            # — without it the synthesized title leaks an entity into JSON-LD and
            # <title>, which looks like a theme bug and is not one.
            fm.append("title: %s" % toml_str(html.unescape(it["title"])))
            stats["titled"] += 1
        if it.get("tags"):
            fm.append("categories: [%s]" % ", ".join(toml_str(t) for t in it["tags"]))
            stats["tagged"] += 1

        chtml = it.get("content_html", "")
        photos = [u for u in IMG_SRC.findall(chtml) if "uploads.micro.blog" in u]
        if photos:
            fm.append("photos: [%s]" % ", ".join(toml_str(u) for u in photos))
            stats["photos"] += 1
        # dict.fromkeys preserves order while de-duplicating
        isbns = list(dict.fromkeys(ISBN_LINK.findall(chtml)))
        if isbns:
            fm.append("books: [%s]" % ", ".join(toml_str(i) for i in isbns))
            stats["books"] += 1
        fm.append("---")

        path = os.path.join(postdir, "%s-%s-%s-%s.md" % (year, month, day, slug))
        with open(path, "w") as fh:
            fh.write("\n".join(fm) + "\n\n" + it.get("content_text", ""))
        stats["written"] += 1

    print("  synthesized %(written)d posts "
          "(%(titled)d titled, %(tagged)d tagged, %(books)d with ISBN, "
          "%(photos)d with photos, %(skipped)d skipped)" % stats)


if __name__ == "__main__":
    main()
