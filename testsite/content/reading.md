---
title: "Reading"
date: 2026-01-12T00:00:00Z
---

## Currently Reading

{{< bookshelf >}}

## Grid variant

{{< bookshelf shelf="read2026" variant="grid" >}}

## Bad variant falls back

<!-- INTENTIONAL: this emits `WARN bookshelf: unknown variant "nonsense" …` on
     every build, including CI. That warning is the assertion — the shortcode
     must warn and fall back to "list" rather than call errorf, which is fatal
     and would fail the whole build over a typo in a post. Don't "fix" it. -->
{{< bookshelf variant="nonsense" >}}

## 2026

{{< bookgoals 2026 >}}

## 2025

{{< bookgoals 2025 >}}

## Progress

Read {{< bookgoals progress >}} this year.

## Empty year falls through silently

{{< bookgoals 1999 >}}
