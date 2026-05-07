# CHG-2106: Move FX Open Slug Column After Index

**Applies to:** FXB project
**Last updated:** 2026-05-07
**Last reviewed:** 2026-05-07
**Status:** Completed
**Related:** COR-1101, COR-1500, COR-1615, COR-1612, FXB-2101, FXB-2105, PR #61
**Date:** 2026-05-05
**Requested by:** Frank Xu
**Priority:** Medium
**Change Type:** Normal

---

## What

Change the `fx open` ASCII table column order so `Slug` appears immediately
after the index column.

Current normal list order:

```text
| # | Name | Slug | Tags | Target |
```

Desired normal list order:

```text
| # | Slug | Name | Tags | Target |
```

For list views that include disabled entries, `Slug` must still remain column 2:

Current disabled/all order:

```text
| # | State | Name | Slug | Tags | Target |
```

Desired disabled/all order:

```text
| # | Slug | State | Name | Tags | Target |
```

This applies consistently to normal list output, tag-filtered list output,
search output, `--all`, and `--disabled`.

## Why

The user intentionally keeps `fx open` slugs very short, often 2-3 characters,
so they can be typed quickly. Moving the slug near the index makes the table
more scannable for the main workflow:

1. list or search saved targets
2. identify the short slug
3. type `fx open <slug>`

In the current layout, `Name` can be much wider than `Slug`, making the short
selector less prominent even though it is one of the most important fields.

## Impact Analysis

- **Systems affected:**
  - `fx_bin/open_launcher.py` table formatter
  - Unit tests for table formatting
  - Integration tests that assert list/search output
  - README and command docs if examples describe or imply column order
- **User-facing behavior:** Only display order changes. Saved config schema,
  item sorting, selector resolution, index numbering, search behavior, and open
  dispatch remain unchanged.
- **Compatibility risk:** Low. Scripts that parse `fx open` table output by
  column position may need to adjust, but the table is a human-facing display.
- **Documentation note:** FXB-2101 established the responsive ASCII table and
  contains wording from the previous column order. FXB-2106 supersedes only the
  display order; FXB-2101's responsiveness and readability requirements remain
  active.
- **Responsive formatting risk:** Because `Slug` becomes earlier, the column
  width fitting algorithm should still keep long `Target` truncation working
  and preserve one row per item.
- **Rollback plan:** Restore the previous formatter column order and related
  tests/docs. No config migration is required.

## Implementation Plan

1. Apply COR-1500 TDD overlay for the implementation PR.
2. Add/adjust tests that assert normal table headers begin with:

   ```text
   | # | Slug | Name |
   ```
3. Add/adjust tests that assert disabled/all table headers keep `Slug` in column
   2 even when `State` is present.
4. Add/adjust search output tests if they inspect table column order.
5. Update `fx_bin/open_launcher.py` formatter column construction to emit
   columns in this order:
   - `#`
   - `Slug`
   - optional `State`
   - `Name`
   - `Tags`
   - `Target`
6. Keep existing responsive width caps/min-width behavior unless tests show a
   layout regression.
7. Update README/docs examples if they show table output or mention column
   order.
8. Run focused `fx open` unit/integration tests, formatting, lint, and AF
   validation.

## Acceptance Criteria

- `fx open` list output displays `Slug` as the second column after `#`.
- `fx open --tag <tag>` list output uses the same column order.
- `fx open search <query>` output uses the same column order.
- `fx open --all` and `fx open --disabled` keep `Slug` as column 2 even when a
  `State` column appears.
- Existing 1-based indices, preserved search indices, slug dispatch, tag
  filtering, and responsive target truncation behavior remain unchanged.
- Tests cover normal, search, and disabled/all output column order.
- Documentation/help remain consistent with the display behavior.

## Testing / Verification

- Focused unit/integration tests:

  ```bash
  poetry run pytest tests/unit/test_open_launcher.py tests/integration/test_open_cli.py -q --no-cov
  ```
- Formatting and lint:

  ```bash
  poetry run black --check fx_bin/open_launcher.py tests/unit/test_open_launcher.py tests/integration/test_open_cli.py
  poetry run flake8 fx_bin/ --statistics
  python3 -m ruff check fx_bin/open_launcher.py tests/unit/test_open_launcher.py tests/integration/test_open_cli.py
  af validate
  ```

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-05-05 | Initial version | af CLI |
| 2026-05-05 | Filled change request for moving Slug to column 2 | Codex |
| 2026-05-05 | Addressed Trinity fast-review advisories | Codex |
| 2026-05-05 | Added FXB-2101 supersession note and Flake8 verification | Codex |
| 2026-05-07 | Implemented + merged (PR #61, v2.10.0) | Claude Code |
