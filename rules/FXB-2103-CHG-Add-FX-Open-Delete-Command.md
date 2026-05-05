# CHG-2103: Add FX Open Delete Command

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

Add an `fx open delete` command that permanently removes an existing saved
target from the local `fx open` TOML registry.

Proposed command shape:

```bash
fx open delete <slug-or-index>
fx open delete <slug-or-index> --yes
fx open --tag usage delete 2
fx open delete cc-usage --config ./open.toml
```

Selector behavior should match the existing list/open model:

- Slug selectors delete the matching saved item.
- Numeric selectors delete the 1-based item in the current visible list.
- When `--tag` is provided, numeric selectors are resolved against the filtered
  list, and slug selectors must match the filtered view.
- Direct URL/path tokens are not valid delete selectors.

Deletion is permanent. Use `fx open disable` for temporary hiding instead.

## Why

The user needs a first-class way to remove stale, incorrect, or no-longer-needed
saved launcher entries without manually editing `open.toml`. Manual edits are
error-prone because the config file is TOML and the current implementation
validates slugs, target type, browser/app compatibility, and ordering.

## Impact Analysis

- **Systems affected:**
  - `fx_bin/cli.py` routing for the flat `fx open` command
  - `fx_bin/open_launcher.py` config mutation helpers
  - Unit, integration, and security tests for config mutation
  - README and command help examples
- **User-facing behavior:** Adds a destructive command that removes an item from
  the config file. Existing list/open/add behavior should remain unchanged.
- **Compatibility:** Existing configs remain valid. `delete` is already a
  reserved slug in FXB-2100, so this subcommand should not create a new slug
  compatibility conflict.
- **Risk:** Accidental deletion. Mitigate with confirmation prompts and
  `--yes` only for explicit non-interactive deletion.
- **Formatting risk:** Full TOML rewrites may not preserve user-authored
  comments, blank-line choices, or formatting around `[[items]]` blocks. The
  delete workflow should document this behavior before implementation.
- **Rollback plan:** Revert the CLI command and delete helper. User-local config
  files that were already modified cannot be automatically restored unless the
  user has backups or VCS history.

## Implementation Plan

1. Extend `fx open` flat-token routing so first token `delete` enters the delete
   workflow.
2. Restructure the current add-only option guard in `fx_bin/cli.py` so `--yes`
   is valid for `add`, `delete`, `disable`, and `enable`, while `--name`,
   `--slug`, `--entry-tag`, and `--ai` remain add-only.
3. Keep option ownership clear:
   - `--tag` filters the visible delete selection view.
   - `--config` selects the config file.
   - `--browser`, `--app`, `--name`, `--slug`, `--entry-tag`, and `--ai` are
     invalid with `delete`.
4. Resolve delete selectors through the same filtered saved-item semantics used
   by list/open. Do not allow direct URL/path deletion by value in v1.
5. Show a concise confirmation preview in interactive mode:

   ```text
   Delete cc-usage: Claude Code usage
   Target: https://example.com/usage
   Proceed?
   ```

6. Require `--yes` in non-interactive mode, matching `fx open add`.
7. Implement shared full-registry TOML rewrite infrastructure that can also be
   reused by FXB-2104:
   - write all remaining schema-valid items in deterministic order
   - preserve all supported fields
   - round-trip through `tomllib` and full schema validation before replace
   - document that comments and custom formatting are not preserved by mutation
     commands in v1
8. Mutate the TOML registry under the same lock strategy as add:
   - acquire config lock
   - read locked snapshot
   - parse and validate
   - remove the selected item
   - serialize a complete valid TOML candidate
   - parse and validate candidate
   - atomically replace with `os.replace`
9. Preserve remaining items' fields and order values. Do not renumber orders
   automatically.
10. Return clear errors for:
   - missing selector
   - unknown slug
   - out-of-range index
   - selector exists outside the active `--tag` filter
   - active config lock
   - malformed TOML
11. Update docs and `--help` examples.
12. Apply COR-1500 TDD overlay during implementation.

## Acceptance Criteria

- `fx open delete <slug> --yes` removes the matching entry from the config.
- `fx open delete <index> --yes` removes the item at that visible 1-based
  index.
- `fx open --tag usage delete 2 --yes` deletes index 2 in the filtered list.
- Interactive deletion asks for confirmation.
- Non-interactive deletion requires `--yes`.
- Other entries remain intact and keep their existing order values.
- Supported fields on other entries remain intact after the full TOML rewrite.
- The docs note that mutation commands may remove comments and custom formatting
  from the config file in v1.
- Deleting a missing selector exits with a clear error and does not change the
  file.
- The operation is lock-protected and atomic.
- Documentation and help clearly distinguish delete from disable.

## Testing / Verification

- Unit tests cover selector resolution, filtered deletion, TOML rewrite,
  confirmation-independent helper behavior, and malformed config safety.
- Integration tests cover CLI success and failure paths.
- Security tests cover lock contention, unsupported direct target deletion, and
  no shell execution.
- Regression checks include focused `tests/unit/test_open_launcher.py` and
  `tests/integration/test_open_cli.py`.

Implementation completed on 2026-05-05. `fx open delete` now supports slug and
visible-index selectors, `--tag` filtered selection, non-interactive `--yes`,
interactive confirmation, lock-protected atomic TOML rewrite, and direct
URL/path selector rejection.

COR-1602/COR-1610 implementation review completed on 2026-05-05 with DeepSeek
PASS and GLM PASS. Additional CLI integration tests were added after review for
tag-filtered delete and disabled-view delete.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-05-05 | Initial version | af CLI |
| 2026-05-05 | Filled change request for permanent delete workflow | Codex |
| 2026-05-05 | Addressed Trinity review: add option-guard change, shared TOML rewrite, and comment-loss impact | Codex |
| 2026-05-05 | Implemented delete workflow and related tests | Codex |
| 2026-05-05 | Completed implementation review with DeepSeek and GLM PASS | Codex |
