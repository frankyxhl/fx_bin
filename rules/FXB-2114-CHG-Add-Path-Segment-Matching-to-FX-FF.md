# CHG-2114: Add Path Segment Matching to FX FF

**Applies to:** FXB project
**Last updated:** 2026-08-08
**Last reviewed:** 2026-08-08
**Status:** Proposed
**Date:** 2026-08-08
**Requested by:** Frank Xu
**Priority:** Medium
**Change Type:** Normal

---

## What

`fx ff` (and `fx fff`) currently match KEYWORD against the basename only
(`find_files.py`: `keyword in name`), so a keyword containing a path
separator — e.g. `fx ff frank_maintain/file-organizer.md` — can never match.

Change: when KEYWORD contains `os.sep`, match it against the path relative
to the search root instead of the basename. Keywords without a separator
keep the exact current behavior.

## Why

Users often know a fragment of the path, not just the filename
(`dir/file.md`). Today that query silently returns nothing, which reads as
"file does not exist" rather than "unsupported query shape".

## Impact Analysis

- **Systems affected:** `fx_bin/find_files.py` (match loop only). `fx ff`,
  `fx fff` CLI behavior for keywords containing `/`. No change for plain
  keywords; `--exclude` still filters basenames.
- **Rollback plan:** revert the commit; the match loop returns to
  basename-only.

## Implementation Plan

1. TDD: add tests — path-segment keyword matches; plain keyword behavior
   unchanged; `--first` works with path keywords.
2. In `find_files()`, compute the match target per entry: relative path when
   `os.sep in keyword`, else basename.
3. Update `fx ff` help text with a path-segment example.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-08-08 | Initial version | Claude Code |
