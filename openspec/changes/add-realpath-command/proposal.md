# Change: Add fx realpath command

## Why

macOS lacks the GNU `realpath` command by default. Users need a cross-platform way to resolve file paths to their absolute canonical form, especially when working with relative paths, symlinks, or `~` expansion in shell scripts.

## What Changes

- Add new `fx realpath` CLI command
- Create `fx_bin/realpath.py` module with core `resolve_path()` function
- Register command in `fx_bin/cli.py` and `COMMANDS_INFO`
- Add unit tests in `tests/unit/test_realpath.py`
- Add integration tests in `tests/integration/test_realpath_cli.py`

## Impact

- Affected specs: `cli` (new command added)
- Affected code:
  - `fx_bin/realpath.py` (new file)
  - `fx_bin/cli.py` (add command registration)
  - `tests/unit/test_realpath.py` (new file)
  - `tests/integration/test_realpath_cli.py` (new file)

## Design Reference

See `docs/plans/2026-01-02-fx-realpath-design.md` for technical design details.

## Workflow Mode

Using **Coordination Mode** with Sisyphus as orchestrator:
- `oracle` handles planning (Stage 2) and review (Stage 5)
- `coder` handles implementation (Stage 3, 4)
- Sisyphus coordinates and approves at each checkpoint
