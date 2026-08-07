---
title: "Search"
url: "/search/"
menu: "main"
weight: 100
---

<form class="search-form" role="search" action="/search/" method="get">
  <label class="search-label" for="search-input">Search this blog</label>
  <input class="search-input" id="search-input" type="search" name="q"
         placeholder="Search posts…" autocomplete="off" spellcheck="false"
         enterkeyhint="search" autocapitalize="none">
</form>

<p class="search-status" id="search-status" role="status" aria-live="polite"></p>

<ol class="search-results" id="search-results"></ol>

<noscript>
  <p>Search needs JavaScript. You can browse the <a href="/archive/">full archive</a> instead.</p>
</noscript>

<!-- Bump ?v= whenever static/js/search.js changes. micro.blog sends ETag and
     Last-Modified but no Cache-Control (probed live), so revalidation is at the
     browser's discretion and an edit can otherwise serve stale. main.css gets
     the same treatment via ?{{ .Site.Params.theme_seconds }} in head.html; this
     is a content file, not a template, so the bump is manual. -->
<script src="/js/search.js?v=2" defer></script>
