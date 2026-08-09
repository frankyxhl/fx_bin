# CHG-2116: Copy FX Realpath Result to Clipboard by Default

**Applies to:** FXB project
**Last updated:** 2026-08-09
**Last reviewed:** 2026-08-09
**Status:** Proposed
**Date:** 2026-08-09
**Requested by:** Frank Xu
**Priority:** Medium
**Change Type:** Normal

---

## What

`fx realpath` / `fx rp` copy the resolved absolute path to the clipboard by
default when stdout is a TTY; a `--no-copy` flag opts out. Same semantics as
`fx ff` (CHG-2115): piped/scripted output never touches the clipboard, and a
clipboard failure warns on stderr without changing the exit code. Reuses the
shared `fx_bin.clipboard` module.

## Why

The output of `fx rp` is exactly one path whose purpose is to be pasted
somewhere else — the archetypal copy-on-run command. This was the original
motivation behind extracting `fx_bin/clipboard.py` for reuse.

## Impact Analysis

- **Systems affected:** `fx_bin/cli.py` (`_run_realpath` + `realpath`/`rp`
  commands gain default copy + `--no-copy`). No other modules change.
- **Behavior note:** `open "$(fx rp x)"`-style substitution is non-TTY, so
  scripts are unaffected.
- **Rollback plan:** revert the commit; realpath/rp return to print-only.

## Implementation Plan

1. TDD: tests for copy-by-default on TTY, `--no-copy`, non-TTY skip,
   error-path (nonexistent path → no copy), clipboard-failure-warns.
2. Wire `_run_realpath` through `clipboard.copy_to_clipboard` guarded by
   the existing `_stdout_is_tty` helper.
3. Update command help text, README, and docs site realpath page.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-08-09 | Initial version | Claude Code |
