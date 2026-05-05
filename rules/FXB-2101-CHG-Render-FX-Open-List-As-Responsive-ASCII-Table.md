# CHG-2101: Render FX Open List As Responsive ASCII Table

**Applies to:** FXB project
**Last updated:** 2026-05-05
**Last reviewed:** 2026-05-05
**Status:** Completed
**Related:** COR-1101, COR-1500, FXB-2100, FXB-2104
**Date:** 2026-05-05
**Requested by:** Frank Xu
**Priority:** Medium
**Change Type:** Normal

---

## What

Change `fx open` list output from the current multi-line-per-entry format to a
compact ASCII table where each saved target is rendered on exactly one data row.

The table should include these columns:

| Column | Purpose |
|--------|---------|
| `#` | 1-based index used by `fx open <index>` |
| `Name` | saved display name |
| `Slug` | saved selector |
| `Tags` | comma-separated metadata tags |
| `Target` | URL or local file target |

FXB-2101 does not introduce disabled entries, but the table formatter should be
compatible with FXB-2104. When disabled entries are later shown through
`fx open --all` or `fx open --disabled`, the formatter may add a compact
`State` column after `#`; enabled rows use an empty state and disabled rows show
`disabled`. This keeps every saved target on one data row while avoiding a
future table redesign.

The `Target` column should be the flexible final column. It should use remaining
terminal width and only truncate when the full row would exceed the current
screen width. Truncation must keep output to one physical terminal line per item
and should use ASCII `...`.

Display width should be based on the current terminal size via the standard
library. When no terminal width is available, use a stable fallback width for
CI, pipes, and tests. The implementation should account for East Asian wide
characters, including Chinese display text, without adding a runtime dependency.

## Why

The current output is verbose and hard to scan when the registry contains many
saved targets:

```text
1. Claude Code usage [cc-usage]
   target: https://example.com/very/long/url
   tags: usage, claude-code
```

The user wants the list view to behave more like a compact launcher index. A
single-row ASCII table makes it easier to compare entries, read index numbers,
and choose a saved target quickly without wrapping long URLs across multiple
lines.

## Impact Analysis

- **Systems affected:**
  - `fx_bin/open_launcher.py` list formatting behavior
  - `fx_bin/cli.py` help text or examples if needed
  - `README.md` `fx open` examples
  - Unit and integration tests for `fx open` list output
- **User-facing behavior:** `fx open` and `fx open --tag <tag>` list output
  changes from multi-line records to a compact table. Selection by index, slug,
  tag filtering, direct URL/path opening, and add behavior remain unchanged.
- **Compatibility:** Existing TOML config files remain valid. No config schema
  migration is required.
- **Runtime dependencies:** None. Use only Python standard library.
- **Rollback plan:** Revert the table formatter and restore the previous
  multi-line `format_items()` output. No user-local config files need changes.

## Implementation Plan

1. Keep selector semantics unchanged:
   - `fx open` lists all saved items.
   - `fx open --tag usage` lists the filtered view.
   - `fx open 3` and `fx open --tag usage 2` continue to use the visible
     1-based index from the rendered list.
2. Replace the current multi-line list formatter with an ASCII table formatter.
3. Add display-width helpers based on `unicodedata.east_asian_width()` so mixed
   English/Chinese text is padded and truncated by terminal display width rather
   than Python string length.
4. Use `shutil.get_terminal_size()` to determine the available width. The table
   should fit within the reported column count. Use a deterministic fallback
   width of 80 columns when output width cannot be detected, matching the
   standard library default and common CI log widths.
5. Use dynamic width for the `#` column based on the visible item count, so
   10+, 100+, and larger lists remain aligned. Use capped widths for `Name`,
   `Slug`, and `Tags`. Allocate the remaining width to the final `Target`
   column.
6. Truncate cells only when necessary to prevent line wrapping. Prefer preserving
   more of `Target` than decorative spacing because long URLs and paths are the
   most valuable field.
7. Render embedded newlines, carriage returns, tabs, or other display-breaking
   control characters in cell text safely so a saved item cannot create extra
   table rows.
8. Keep the optional future `State` column compatible with FXB-2104 while
   preserving the one-row-per-item invariant.
9. Keep the empty-list message concise and unchanged unless the new table helper
   needs a clearer no-data branch.
10. Update README and help/example text only where it references the old
   multi-line display shape.
11. Apply the COR-1500 TDD overlay during implementation:
    - RED: add focused unit/integration expectations for table output, width
      limits, truncation, filtered indices, and wide-character alignment.
    - GREEN: implement the formatter and width helpers.
    - REFACTOR: simplify formatter code without changing behavior.

## Acceptance Criteria

- `fx open` renders saved targets as an ASCII table.
- Each saved target occupies exactly one data row.
- The row width does not exceed the detected terminal width when that width is
  large enough to render a usable table.
- Long URLs and paths are shown as fully as possible and truncated only when
  needed to avoid wrapping.
- Truncation uses ASCII `...`.
- `Target` is the flexible final column.
- `#`, `Name`, `Slug`, and `Tags` remain readable with sensible capped widths.
- The `#` column width adapts to the number of visible rows.
- The table has a defined extension point for disabled row state from FXB-2104
  without breaking one-row-per-item output.
- `--tag` filtered list output uses the same table format and shows filtered
  1-based indices.
- Chinese and other East Asian wide characters do not obviously break column
  alignment.
- No new runtime dependency is introduced.
- Existing `fx open` selection, dispatch, add, browser/app, and AI metadata
  behavior remains unchanged.

## Testing / Verification

- Unit tests cover:
  - normal table rendering
  - long target truncation at a mocked terminal width
  - no wrapping or embedded newline leakage from cell text
  - wide-character display width handling
  - empty-list behavior
- Integration tests cover:
  - `fx open` list output includes a table header and one row per item
  - `fx open --tag <tag>` renders filtered rows with filtered indices
- Regression checks:
  - focused `tests/unit/test_open_launcher.py`
  - focused `tests/integration/test_open_cli.py`
  - broader formatting and test commands per project guidance when implementing

Implementation completed on 2026-05-05. The formatter now renders a compact
ASCII table, uses terminal width with an 80-column fallback, truncates with
ASCII `...`, sanitizes control characters, and accounts for East Asian display
width using the Python standard library.

COR-1602/COR-1610 implementation review completed on 2026-05-05 with DeepSeek
PASS and GLM PASS. Non-blocking formatter polish was addressed after review.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-05-05 | Initial version | af CLI |
| 2026-05-05 | Filled change request with responsive ASCII table requirements | Codex |
| 2026-05-05 | Addressed Trinity review: disabled-state extension point, dynamic index width, and 80-column fallback | Codex |
| 2026-05-05 | Implemented responsive table output and related tests | Codex |
| 2026-05-05 | Completed implementation review with DeepSeek and GLM PASS | Codex |
