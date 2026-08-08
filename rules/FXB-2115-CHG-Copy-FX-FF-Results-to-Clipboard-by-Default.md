# CHG-2115: Copy FX FF Results to Clipboard by Default

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

1. Extract the clipboard logic from `open_launcher.py`
   (`build_clipboard_plan`, `copy_to_clipboard`, the Wayland/X11 constants)
   into a new shared module `fx_bin/clipboard.py`, with a dedicated
   `ClipboardError(FxBinError)`. `open_launcher` re-exports the names so its
   public surface and existing tests are unchanged.
2. `fx ff` / `fx fff` copy their printed results (newline-joined) to the
   clipboard **by default**; a `--no-copy` flag opts out. No matches → the
   clipboard is left untouched. A clipboard failure (headless box, missing
   tool) warns on stderr but does not fail the search.

## Why

The output of `fx ff` *is* the deliverable — the user runs it to get an
absolute path to paste somewhere else, so copying is the main flow, not an
extra step. This is the opposite of `fx open`, whose deliverable is the
launched app/URL and where `copy` is the explicit exception (FXB-2110).
Extracting the clipboard helper lets any future subcommand reuse it instead
of importing from `open_launcher`.

## Impact Analysis

- **Systems affected:** new `fx_bin/clipboard.py`; `fx_bin/open_launcher.py`
  (imports only, behavior identical); `fx_bin/find_files.py` and
  `fx_bin/cli.py` (`ff`/`fff` gain default copy + `--no-copy`);
  `fx_bin/errors.py` (`ClipboardError`).
- **Behavior note:** `fx ff` in scripts/pipes now also writes the clipboard;
  scripts that must not touch it should pass `--no-copy`. Exit code is
  unaffected by clipboard failures.
- **Rollback plan:** revert the commit; clipboard code returns to
  `open_launcher` and `ff` stops copying.

## Implementation Plan

1. TDD: tests for `clipboard.py` (plan per platform, error type), for
   `open_launcher` re-export compatibility, and for `ff` copy-by-default /
   `--no-copy` / empty-result / clipboard-failure-warns paths.
2. Move clipboard functions into `fx_bin/clipboard.py`; add
   `ClipboardError`; keep `open_launcher` thin re-exports (`OpenError`
   handling there preserved via subclassing or wrapping).
3. Wire `ff`/`fff`: collect printed paths, copy unless `--no-copy`.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-08-08 | Initial version | Claude Code |
