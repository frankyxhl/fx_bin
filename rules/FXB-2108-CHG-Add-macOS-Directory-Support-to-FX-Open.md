# CHG-2108: Add macOS Directory Support to FX Open

**Applies to:** FXB project
**Last updated:** 2026-05-07
**Last reviewed:** 2026-05-07
**Status:** Proposed
**Related:** COR-1101, COR-1500, FXB-2100
**Date:** 2026-05-07
**Requested by:** Frank Xu
**Priority:** Medium
**Change Type:** Normal

---

## What

Allow `fx open` to open local directories on macOS. Currently `fx open` opens
URLs and local files; adding directories makes it a complete launcher.

```bash
fx open ~/Downloads      # Open directory in Finder
fx open ./src             # Open relative directory
fx open ~/Projects        # Open home-relative directory

fx open add ~/Downloads --name "Downloads" --slug dl --yes   # Save directory
fx open dl                 # Open saved directory by slug
fx open 1                  # Open directory by index
```

Behavior: on macOS, `open <directory>` opens Finder. No new flags, no new
subcommands — directories flow through the existing dispatch pipeline.

**Non-macOS:** attempting to open a directory target on Linux or Windows raises
a clear error: "Opening local directories is only supported on macOS."

## Why

`fx open` already handles URLs and files. Directories complete the triad.
On macOS the `open` command natively opens directories in Finder — no new
mechanism, no new dependency, no new subprocess arguments. The change is a
single guard relaxation in `_normalize_local_path`.

## Scope

### In scope
- `fx open <directory-path>` — direct open in Finder
- `fx open add <directory-path>` — save directory target to config
- `fx open <slug-or-index>` — open saved directory target
- `fx open search ...` — search across directory targets
- `fx open delete/disable/enable <selector>` — mutate directory entries
- `fx open --all/--disabled` — list includes directory targets
- Non-macOS error message: clear, actionable, exits non-zero

### Out of scope
- `--app` for directories (not considered, not tested)
- Linux/Windows directory support
- Directory content scanning or inode tracking
- Recursive opening or multi-path opening
- `file://` scheme targets (already rejected in UNSUPPORTED_TARGET_SCHEMES)

## Impact

### Files changed
- `fx_bin/open_launcher.py` — 3 functions, ~8 lines changed

### Changed functions
1. **`_normalize_local_path`**: `is_file()` → `is_file() or is_dir()`
2. **`normalize_add_target`**: error message includes "or directory"
3. **`build_dispatch_plan`**: non-macOS + directory → clear error

### Files added
- Tests: 4 unit tests, 3 integration tests

### Rollback
Revert `_normalize_local_path` guard, remove error message changes. No data
migration needed (config TOML format unchanged, directory targets stored as
path strings same as files).

### Security
- No new subprocess arguments — directories passed same as files
- No new scheme handling — directories are schemesless paths
- `open` is already sandboxed by macOS
- Path traversal protection unchanged (existing `Path.resolve` validation)
- No new NUL-byte or control-character surface

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-05-07 | Initial proposal | Claude Code |
