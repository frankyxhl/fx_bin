# PRP-2119: Add FX Pwd Command

**Applies to:** FXB project
**Last updated:** 2026-11-09
**Last reviewed:** 2026-11-09
**Status:** Draft

---

## What Is It?

Add an `fx pwd` command that prints the current working directory, like the system `pwd`. By default it copies the printed text to the clipboard, using the same helper and the same TTY gating as `fx rp`. `--no-copy` turns the copy off. `--host` (`-H`) prefixes the machine host name, giving `host:/path`.

---

## Problem

Sharing the current directory with another machine or a chat means running `pwd`, then typing the host name by hand, then copying. `fx rp .` already copies a resolved path, but it resolves symlinks, needs an argument for the current directory, and never adds the host name. A one-word command that prints and copies `host:/path` removes the manual steps.

## Proposed Solution

### Behavior

| Command | Output | Clipboard |
|---|---|---|
| `fx pwd` | `/Users/frank/projects/demo` | copied when stdout is a TTY |
| `fx pwd --no-copy` | same | never |
| `fx pwd --host` / `-H` | `WuKong-Macmini:/Users/frank/projects/demo` | the same line, when stdout is a TTY |
| `fx pwd ... \| cat` | same text | never (piped output never touches the clipboard, same as `fx rp`) |

- Path source: the logical path, like the shell `pwd` (`pwd -L`): `$PWD` when it is absolute and names the same directory as `.` (checked with `os.path.samefile`), otherwise `os.getcwd()`. A symlinked directory therefore prints the path the user typed, not the resolved one.
- Host source: `socket.gethostname()`, used as returned. No `.local` stripping and no domain added.
- Host format: `host:/path`, the scp/rsync style. The path is appended unchanged.
- Clipboard: `clipboard.copy_to_clipboard`, called from the same TTY gate as `_run_realpath` in `fx_bin/cli.py`. A `ClipboardError` prints `Warning: could not copy to clipboard: <reason>` on stderr and the exit code stays 0.
- Exit code 0 on success. The whole path step (reading `$PWD`, `os.path.samefile`, `os.getcwd()`) is wrapped in one `OSError` catch. If the current directory was deleted, even with `$PWD` still set to it, print `Error: Cannot determine current directory (<reason>)` on stderr and exit 1.

### Platforms

- macOS and Linux: output is directly usable with `scp host:/path`.
- macOS without a configured HostName: `socket.gethostname()` can return `name.local`. `README.md` says so; the value is used as returned.
- Windows: the path keeps its drive letter and backslashes, so `--host` prints something like `DESKTOP-AB12CD3:C:\Users\frank\demo`. This is not a valid scp address. Known limit of the first version; no path conversion (Frank's ruling).

### Files

- `fx_bin/cli.py`: the `pwd` command and its row in the command list.
- `fx_bin/pwd_cmd.py` (new, small): builds the output line from cwd and optional host.
- `tests/test_pwd.py` (new): CLI and unit tests.
- `README.md`: command documentation. `CHANGELOG.md`: one entry.
- `rules/`: this PRP and the index row.

### Tests (written first, failing on `2800c22`)

1. `fx pwd` prints the current directory.
2. `fx pwd --host` prints `<gethostname()>:<cwd>`; `-H` is the same.
3. On a TTY the clipboard helper receives exactly the printed line, with and without `--host`; with `--no-copy` it is never called; with piped output it is never called.
4. A clipboard failure prints the warning on stderr and exits 0.
5. A deleted current directory exits 1 with the error line, both with `$PWD` unset and with `$PWD` still set to the deleted path.
6. The command appears in `fx list`.
7. With `$PWD` set to a symlink that points at the current directory, the symlink path is printed; with a stale or wrong `$PWD`, `os.getcwd()` is printed.
8. Host name is taken from `socket.gethostname()` (patched in the test), not from the environment.

### Out of scope

No Windows path conversion, no `.local` handling, no `ssh://` or `file://` formats, no path argument (`fx rp` covers that).

### Code rule

New code and tests carry no comments and no docstrings (Frank, 2026-10-20, fleet rule).

## Open Questions

- None open. Decided by Frank: `--host`/`-H`, `host:/path`, `socket.gethostname()`, no Windows path conversion.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-11-09 | Initial version | fx-bin |
