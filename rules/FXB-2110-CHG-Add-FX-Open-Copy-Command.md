# CHG-2110: Add FX Open Copy Command

**Applies to:** FXB project
**Last updated:** 2026-08-07
**Last reviewed:** 2026-08-07
**Status:** Completed
**Related:** COR-1101, COR-1500, FXB-2100, FXB-2103, FXB-2104, FXB-2105, GitHub PR #82
**Date:** 2026-08-07
**Requested by:** Frank Xu
**Priority:** Medium
**Change Type:** Normal

---

## What

Add an `fx open copy <selector>` command that writes a saved or direct target to
the system clipboard instead of opening it.

The selector accepts the same forms as `fx open`:

- slug
- 1-based index from the current visible list
- direct URL or local path

Proposed command shape:

```bash
fx open copy cc-usage
fx open copy 3
fx open copy https://example.com
fx open --tag usage copy 2
```

## Why

The saved launcher registry is already the place where a URL is recorded, but
the only thing `fx open` can do with a target is launch it. Sharing a link
(pasting into chat, a ticket, a commit message) currently means opening the
browser and copying from the address bar, or opening `open.toml` and copying by
hand. Copying is the second natural verb on the same registry, and it reuses
the selector resolution that already exists.

## Impact Analysis

- **Systems affected:**
  - `fx_bin/open_launcher.py` clipboard command construction and execution
  - `fx_bin/cli.py` manual `fx open` subcommand routing and help text
  - Unit and integration tests for `fx open`
  - `README.md` command documentation
- **User-facing behavior:** `fx open copy <selector>` prints
  `Copied <target>` and does not launch anything. `--tag` composes with the
  selector exactly as it does for `fx open`.
- **Compatibility risk:** `copy` is not currently a reserved slug. Adding a
  subcommand means saved configs with `slug = "copy"` must fail with the same
  clear reserved-slug rename guidance as `delete`, `disable`, `enable`, and
  `search`. Handled by adding `copy` to `NEWLY_RESERVED_SLUGS`.
- **Platform risk:** no clipboard primitive exists in the Python standard
  library, so the command shells out to the platform clipboard tool. Wayland
  and X11 maintain separate clipboards and each tool only talks to its own
  display server, so Linux selection is driven by `WAYLAND_DISPLAY` rather than
  by whichever binary is installed (`wl-clipboard` ships as a dependency on many
  X11 installs).
- **Out of scope:** reading from the clipboard, copying entry metadata other
  than the target, a `--copy` flag on plain `fx open`, and adding a
  third-party clipboard dependency such as `pyperclip`.
- **Rollback plan:** Revert the CLI route, the clipboard helpers, the reserved
  slug change, docs/help text, and tests. Existing configs are unaffected
  unless a user added a `copy` slug after this version.

## Implementation Plan

1. Add RED tests for clipboard command selection:
   - macOS uses `pbcopy`, Windows uses `clip`
   - Wayland session prefers `wl-copy`, X11 session prefers `xclip`
   - each session type falls back to the other tool when the preferred one is
     not installed
   - neither tool installed raises with install guidance
   - unsupported platform raises
2. Add `build_clipboard_plan()` returning the existing `DispatchPlan` dataclass,
   and `copy_to_clipboard()` writing on stdin with `shell=False`.
3. Reserve `copy` as an `fx open` subcommand slug and reuse the existing
   rename guidance for collisions.
4. Add `fx open copy <selector>` routing in `fx_bin/cli.py`, resolving the
   selector through the existing `resolve_launch_target`.
5. Reject `fx open copy` without a selector, and reject `--browser`, `--app`,
   `--all`, `--disabled`, and the add-only metadata flags.
6. Update `fx open --help` examples and README.
7. Run focused tests, then broader checks that are available locally.

## Acceptance Criteria

- `fx open copy <selector>` writes the resolved target to the system clipboard
  and prints `Copied <target>`.
- Selectors cover slug, 1-based index, and direct URL/path.
- `fx open copy` does not launch the target.
- `fx open copy` with no selector errors with a helpful usage message.
- `fx open --tag <tag> copy <index>` composes both filters.
- A saved entry with `slug = "copy"` fails at config load with rename guidance.
- Clipboard dispatch runs with `shell=False`.
- `--help` and README document the new command.

## Testing / Verification

- Unit tests: `tests/unit/test_open_launcher.py::TestClipboard`
- Integration tests: `tests/integration/test_open_cli.py::TestOpenCopy`
- Focused verification command:

  ```bash
  poetry run pytest tests/unit/test_open_launcher.py tests/integration/test_open_cli.py -q --no-cov
  ```

Implementation completed on 2026-08-07. `fx open copy SELECTOR` writes the
resolved target to the clipboard via `pbcopy` (macOS), `clip` (Windows), and
`wl-copy` / `xclip` selected by session type (Linux), reuses
`resolve_launch_target` for selector handling, reserves the `copy` slug, and
documents the workflow in `--help` and README.

Verification completed with:

- `.venv/bin/python -m pytest --no-cov -q` (702 passed, excluding
  `tests/integration/test_today_cli.py`, which replaces the pytest process
  mid-run on `main` as well)
- `.venv/bin/python -m black --check fx_bin/ tests/`
- `.venv/bin/python -m flake8 fx_bin`
- `.venv/bin/python -m mypy fx_bin/`
- End-to-end check against real `pbcopy` on macOS

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-08-07 | Initial version — recorded during PR #82 review response (COR-1612) after the AI reviewer flagged the missing AF artifact | Claude Code |
