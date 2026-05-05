# CHG-2105: Add FX Open Search Command

**Applies to:** FXB project
**Last updated:** 2026-05-05
**Last reviewed:** 2026-05-05
**Status:** Completed
**Related:** COR-1101, COR-1500, FXB-2100, GitHub issue #59
**Date:** 2026-05-05
**Requested by:** Frank Xu
**Priority:** Medium
**Change Type:** Normal

---

## What

Add an `fx open search <query>` command that lists saved launcher entries whose
metadata contains the query.

Search should inspect these fields:

- `name`
- `slug`
- `tags`
- `target`

The command should use the same responsive ASCII table as normal `fx open`
listing so users can quickly inspect the matching entry and open it by slug.

Proposed command shape:

```bash
fx open search snooker
fx open search usage
fx open search --tag live snooker
```

## Why

As the local launcher registry grows, users may remember only part of a saved
entry, such as `snooker`, `usage`, a provider name, or a target URL fragment.
The current `--tag` filter is useful only when the exact tag is known. Keyword
search provides a low-friction discovery path without adding fuzzy or regex
matching complexity.

## Impact Analysis

- **Systems affected:**
  - `fx_bin/open_launcher.py` filtering helpers
  - `fx_bin/cli.py` manual `fx open` subcommand routing and help text
  - Unit and integration tests for `fx open`
- **User-facing behavior:** `fx open search <query>` lists enabled matching
  entries by default. `--tag` composes with search as an AND filter.
- **Compatibility risk:** `search` is not currently a reserved slug. Adding a
  subcommand means saved configs with `slug = "search"` should fail with the
  same clear reserved-slug rename guidance as other `fx open` subcommands.
- **Out of scope:** fuzzy matching, regex, mutation commands, and direct
  dispatch through the search command.
- **Rollback plan:** Revert the CLI route, search helper, reserved slug change,
  docs/help text, and tests. Existing configs are unaffected unless a user added
  a `search` slug after this version.

## Implementation Plan

1. Add RED tests for keyword search matching:
   - substring match
   - case-insensitive match
   - name / slug / tags / target fields
   - tag composition
   - no-match output
2. Add `search_items()` or equivalent helper in `fx_bin/open_launcher.py`.
3. Reserve `search` as an `fx open` subcommand slug and reuse the existing
   rename guidance for collisions.
4. Add `fx open search <query>` routing in `fx_bin/cli.py`.
5. Reject `fx open search` without a query with a helpful Click error.
6. Keep `--all`, `--disabled`, and `--tag` visibility behavior consistent with
   list filtering where practical; default search excludes disabled entries.
7. Update `fx open --help` examples.
8. Run focused tests, then broader checks that are available locally.

## Acceptance Criteria

- `fx open search <query>` lists saved entries matching `<query>` using
  case-insensitive substring matching.
- Search fields include `name`, `slug`, `tags`, and `target`.
- `fx open search` with no query errors with a helpful usage message.
- `fx open search <query> --tag <tag>` composes both filters as AND.
- `--help` documents the new command.
- Tests cover substring match, case-insensitivity, multi-field matching, tag
  composition, and no-match output.

## Testing / Verification

- Unit tests: `tests/unit/test_open_launcher.py`
- Integration tests: `tests/integration/test_open_cli.py`
- Focused verification command:

  ```bash
  uv run pytest tests/unit/test_open_launcher.py tests/integration/test_open_cli.py -q --no-cov
  ```

Implementation completed on 2026-05-05. `fx open search QUERY` now lists enabled
matching targets by default, searches name/slug/tags/target with
case-insensitive substring matching, composes with `--tag`, supports explicit
`--all` and `--disabled` visibility modes, preserves indices from the current
visible list, and documents the workflow in `--help`, README, and command docs.

Verification completed with:

- `uv run pytest tests/unit/test_open_launcher.py tests/integration/test_open_cli.py -q --no-cov`
- `uv run black --check fx_bin/open_launcher.py fx_bin/cli.py tests/unit/test_open_launcher.py tests/integration/test_open_cli.py`
- `python3 -m ruff check fx_bin/open_launcher.py fx_bin/cli.py tests/unit/test_open_launcher.py tests/integration/test_open_cli.py`
- `af validate`

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-05-05 | Initial version | af CLI |
| 2026-05-05 | Filled change request from GitHub issue #59 | Codex |
| 2026-05-05 | Implemented search command and verified focused tests | Codex |
