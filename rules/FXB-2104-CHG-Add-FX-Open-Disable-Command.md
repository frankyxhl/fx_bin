# CHG-2104: Add FX Open Disable Command

**Applies to:** FXB project
**Last updated:** 2026-05-05
**Last reviewed:** 2026-05-05
**Status:** Completed
**Related:** COR-1101, COR-1500, FXB-2100, FXB-2101, FXB-2103
**Date:** 2026-05-05
**Requested by:** Frank Xu
**Priority:** Medium
**Change Type:** Normal

---

## What

Add an `fx open disable` command that temporarily disables saved launcher
records so they do not appear in normal list output and cannot be selected by
normal index/slug operations.

Proposed command shape:

```bash
fx open disable <slug-or-index>
fx open disable <slug-or-index> --yes
fx open --tag usage disable 2
fx open disable cc-usage --config ./open.toml
```

To make disable useful, this change should also define the complementary
visibility behavior and recovery path:

```bash
fx open --all
fx open --disabled
fx open enable <slug-or-index>
fx open enable <slug-or-index> --yes
```

These command names are part of the CHG contract. Disabled records are hidden by
default and can be restored without recreating the entry.

## Why

Some saved links are temporarily irrelevant but should not be permanently
deleted. Examples include:

- test URLs only needed during a release cycle
- account-specific links used occasionally
- local files that are temporarily unavailable
- URLs kept for later but not wanted in the normal launcher list

Manual removal loses metadata such as name, slug, order, tags, browser, and app.
A disable flag preserves the record while keeping everyday `fx open` output
small and useful.

## Impact Analysis

- **Systems affected:**
  - `fx_bin/open_launcher.py` TOML schema, filtering, selection, and mutation
  - `fx_bin/cli.py` routing for `disable`, likely `enable`, and visibility flags
  - README and command help
  - Unit, integration, and security tests
- **User-facing behavior:** Normal `fx open` listing and selection should hide
  disabled entries. Users need an explicit way to inspect and re-enable them.
- **Config schema:** Add an optional boolean field such as
  `disabled = true`. Missing field means enabled.
- **Compatibility risk:** `disable` is not currently in the reserved slug set.
  Adding a `disable` subcommand should add `disable` and likely `enable` to
  reserved slugs. Existing configs with slug `disable` or `enable` should fail
  with a clear migration error naming the conflicting slug and instructing the
  user to rename it before using this version, instead of surfacing only a
  generic reserved-slug error.
- **Formatting risk:** Full TOML rewrites may not preserve user-authored
  comments, blank-line choices, or formatting around `[[items]]` blocks. The
  disable/enable workflow should document this behavior before implementation.
- **Rollback plan:** Revert the command and schema handling. Existing
  `disabled = true` fields would become unknown item keys under the old parser,
  so rollback requires removing those fields from user-local configs.

## Implementation Plan

1. Extend the item schema with an optional boolean field:

   ```toml
   disabled = true
   ```

   Missing `disabled` defaults to `false`.
2. Add `disable` and `enable` to reserved slug names before exposing those
   subcommands. Do not reserve `disabled`; it is a TOML field name and field
   names live in a separate namespace from slug values.
3. Add a compatibility error path for pre-existing `slug = "disable"` and
   `slug = "enable"` configs:
   - identify the reserved-subcommand collision during config parsing
   - report the exact slug and a manual rename instruction
   - leave the config file unchanged
4. Update normal list/open filtering:
   - default `fx open` excludes disabled entries
   - default index selection excludes disabled entries
   - default slug selection should not open disabled entries
5. Add explicit list-only visibility flags:
   - `fx open --all` lists enabled and disabled entries
   - `fx open --disabled` lists only disabled entries
   - `--all` and `--disabled` are invalid with normal open dispatch selectors
     in v1, so disabled entries cannot be opened by passing a visibility flag
   - `--tag` composes with both visibility flags by filtering within the chosen
     visibility set; indices always refer to the final rendered view
6. Add `fx open disable <slug-or-index>`:
   - selector resolution uses the visible enabled list by default
   - `--tag` filters before resolving the selector
   - `--all` and `--disabled` are invalid with `disable`
   - set `disabled = true`
   - preserve all other fields and order values
7. Add `fx open enable <slug-or-index>` as the recovery path:
   - selector resolution uses the disabled-only list by default
   - `--tag` filters disabled entries before resolving the selector
   - numeric indices match the `fx open --disabled` rendered list
   - `--all` and `--disabled` are invalid with `enable`
   - remove the `disabled` field when enabling an item, rather than writing
     `disabled = false`, for cleaner TOML
8. Restructure the current add-only option guard in `fx_bin/cli.py` so `--yes`
   is valid for `add`, `delete`, `disable`, and `enable`, while `--name`,
   `--slug`, `--entry-tag`, and `--ai` remain add-only.
9. Use the shared full-registry TOML rewrite infrastructure introduced by
   FXB-2103:
   - preserve all supported fields
   - round-trip through `tomllib` and full schema validation before replace
   - document that comments and custom formatting are not preserved by mutation
     commands in v1
10. Use the same lock and atomic rewrite strategy as add/delete.
11. Require confirmation for interactive mutation and `--yes` for
   non-interactive mutation.
12. Make disabled rows visually clear when shown via `--all` or `--disabled` by
    using the FXB-2101 table `State` column with value `disabled`.
13. Update documentation and examples.
14. Apply COR-1500 TDD overlay during implementation.

## Acceptance Criteria

- `fx open disable <slug> --yes` marks the matching entry disabled without
  deleting it.
- Disabled entries do not appear in default `fx open` output.
- Disabled entries cannot be opened by normal index or slug selection.
- Users can list disabled entries explicitly.
- Users can re-enable disabled entries without recreating them.
- `--tag` filtering composes with `--all`, `--disabled`, `disable`, and
  `enable` by filtering within the applicable visibility set.
- `fx open enable <index> --yes` uses indices from the disabled-only view.
- `fx open --all <selector>` and `fx open --disabled <selector>` are rejected in
  v1 rather than opening disabled entries.
- The TOML mutation is lock-protected and atomic.
- Existing configs without `disabled` continue to behave as enabled.
- Existing configs with slug `disable` or `enable` fail with clear rename
  guidance after those words become reserved.
- Existing configs with unknown typo fields still fail fast.
- The docs note that mutation commands may remove comments and custom formatting
  from the config file in v1.
- The docs explain when to use `disable` instead of `delete`.

## Testing / Verification

- Unit tests cover schema parsing, default enabled behavior, disabled filtering,
  selector behavior, and TOML rewrite.
- Integration tests cover `disable`, disabled list visibility, and re-enable
  recovery.
- Security tests cover lock contention, malformed TOML no-change behavior, and
  no shell execution.
- Regression checks include focused `tests/unit/test_open_launcher.py` and
  `tests/integration/test_open_cli.py`.

Implementation completed on 2026-05-05. `fx open disable` and `fx open enable`
now toggle an optional `disabled = true` field, default list/open hides disabled
items, `--all` and `--disabled` expose visibility-specific list views, and
enabled/disabled numeric selectors resolve against the documented visible view.

COR-1602/COR-1610 implementation review completed on 2026-05-05 with DeepSeek
PASS and GLM PASS. Additional CLI integration tests were added after review for
slug-based enable and visibility-flag mutual exclusion. GitHub Codex review
feedback was addressed by preserving non-item TOML config during mutation
rewrites and using the confirmed slug for index-based mutation writes.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-05-05 | Initial version | af CLI |
| 2026-05-05 | Filled change request for temporary disable workflow | Codex |
| 2026-05-05 | Addressed Trinity review: resolve visibility contract, enable selector semantics, reserved-slug migration, and table state integration | Codex |
| 2026-05-05 | Implemented disable/enable workflow and related tests | Codex |
| 2026-05-05 | Completed implementation review with DeepSeek and GLM PASS | Codex |
| 2026-05-05 | Addressed GitHub Codex review: preserve non-item config and use confirmed slug for mutation | Codex |
