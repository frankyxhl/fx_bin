# CHG-2118: Add FX Repo Command

**Applies to:** FXB project
**Last updated:** 2026-08-13
**Last reviewed:** 2026-08-13
**Status:** In Progress
**Date:** 2026-08-13
**Requested by:** Frank Xu
**Priority:** Medium
**Change Type:** Normal
**Related:** FXB-2117 D1, COR-1101, COR-1500, COR-1508

---

## What

Add an `fx repo` command that finds the Git repository containing the current
working directory, selects a configured Git remote, converts a supported
GitHub.com remote URL to its HTTPS repository page, and opens that page in the
operating system's default browser. Add `--remote NAME` for explicit remote
selection.

## Why

Opening the web page for the repository currently being worked on requires
manually inspecting Git configuration, converting SSH URLs, and pasting the
result into a browser. `fx repo` makes this common navigation action a single,
predictable command.

## Impact Analysis

- **Systems affected:** unified CLI registration and command listing, Git
  repository/remote inspection, GitHub URL normalization, focused unit and CLI
  tests, README command documentation.
- **Platforms affected:** macOS, Linux, and Windows through the existing
  `fx open` dispatch planner.
- **Downtime required:** No.
- **Dependencies:** No new runtime or development dependencies.
- **Security:** Git commands and browser dispatch must use argument vectors with
  `shell=False`; remote content is parsed as data and never executed.
- **Rollback plan:** revert the implementation commit to remove the `repo`
  registration and supporting code. The command writes no repository or user
  configuration, so no data migration or cleanup is required.

## Command Contract

```bash
fx repo
fx repo --remote NAME
```

### Repository Discovery

- Start from the current working directory and locate its containing Git
  repository, including when invoked from a nested directory.
- Reuse the existing Git-root behavior where practical.
- If no containing Git repository or no remote is found, print exactly one line
  to stderr and exit non-zero:

  ```text
  No Git remote found for the current directory.
  ```

### Remote Selection

1. When `--remote NAME` is present, select that remote or report that it does
   not exist and list available remote names.
2. Otherwise prefer `origin` when it exists.
3. When there is no `origin` and exactly one remote exists, select it.
4. When there is no `origin` and multiple remotes exist, exit non-zero and list
   the available names with guidance to use `--remote NAME`.

### Supported URLs

Version 1 supports GitHub.com repositories only. The following common forms
normalize to `https://github.com/OWNER/REPOSITORY` with one trailing `.git`
suffix removed:

```text
https://github.com/OWNER/REPOSITORY.git
git@github.com:OWNER/REPOSITORY.git
ssh://git@github.com/OWNER/REPOSITORY.git
```

Other hosts, GitHub Enterprise hosts, local paths, `file://` URLs, malformed
URLs, and URLs that do not identify exactly an owner and repository are rejected
with a concise non-zero error. The error must not echo embedded credentials.

### Successful Dispatch

- Print `Opening https://github.com/OWNER/REPOSITORY`.
- Reuse the existing `fx open` dispatch planning and execution behavior to open
  the normalized URL in the operating system's default browser.
- Propagate a concise non-zero error when no supported browser opener is
  available or dispatch fails.

## Implementation Plan

1. RED: add focused tests for HTTPS, scp-style SSH, and `ssh://` GitHub URL
   normalization, including `.git` removal and malformed/non-GitHub rejection.
2. GREEN: implement the minimum pure URL-normalization behavior using the
   standard library.
3. RED: add repository and remote-selection tests for `origin`, an explicit
   `--remote`, a single fallback remote, ambiguous remotes, missing remotes, and
   invocation from a nested directory.
4. GREEN: implement Git inspection without a shell and register `fx repo` in the
   unified Click CLI and command listing.
5. RED/GREEN: add CLI tests proving success output, default-browser dispatch,
   exact missing-remote text, non-zero failures, and no dispatch on errors.
6. REFACTOR: reuse existing `root` and `open_launcher` seams where that reduces
   duplication without coupling the new command to saved-target configuration.
7. Update README command documentation and examples.
8. Run focused tests, the full suite with coverage, formatting, lint, type
   checking, security tests, and Alfred document validation.

## Testing / Verification

- Focused unit and CLI tests must demonstrate each RED failure before its GREEN
  implementation.
- Full test suite must pass with the configured 80% coverage gate.
- `black --check`, Flake8, strict mypy, security tests, and Bandit must pass.
- A manual dry verification may normalize the current repository's remote, but
  automated tests must mock browser execution so the test suite never opens a
  real browser.

## Approval

- [x] Reviewed by: Frank Xu
- [x] Approved on: 2026-08-13

## Execution Log

| Date | Action | Result |
|------|--------|--------|
| 2026-08-13 | Baseline `.venv/bin/pytest --no-cov` | 730 passed, 1 skipped |
| 2026-08-13 | TDD URL normalization and remote selection | RED observed; 16 unit tests GREEN |
| 2026-08-13 | TDD CLI and browser dispatch behavior | RED observed; 23 focused tests GREEN after refactor |
| 2026-08-13 | Full verification | 753 passed, 1 skipped; 86.76% coverage; Black, Flake8, mypy, Bandit, security tests, and `af validate` passed |
| 2026-08-13 | COR-1610 / FXB-2109 self-review | 9.8/10 PASS; no blocking findings |

## Post-Change Review

- Implementation and local verification are complete. PR review and merge are
  pending. Safety reported nine pre-existing environment dependency findings;
  this change adds or updates no dependencies.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-08-13 | Defined `fx repo` command contract and TDD plan | Codex |
| 2026-08-13 | Approved for implementation | Frank Xu |
| 2026-08-13 | Implemented and verified; awaiting PR review | Codex |
