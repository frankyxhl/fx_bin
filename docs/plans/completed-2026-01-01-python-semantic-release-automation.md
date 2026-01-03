# Python Semantic Release Automation Plan

> **Status:** Completed  
> **Completed:** 2026-01-03

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Automatically bump versions (and optionally publish to PyPI) on merges to `main` using `python-semantic-release`, so humans don’t manually edit version numbers.

**Architecture:** Add `python-semantic-release` configuration in `pyproject.toml`, add a dedicated GitHub Actions workflow that runs semantic release on pushes to `main`, and adjust the existing PyPI deployment workflow to publish only when a release tag (e.g. `v1.6.0`) is created.

**Tech Stack:** Poetry (`pyproject.toml`), GitHub Actions, `python-semantic-release`.

---

## Preflight: Decide adoption point (important)

This repo currently publishes to PyPI on every push to `main` (`.github/workflows/main.yml`) and **does not have tags** for the current PyPI versions (only `v1.2.0`, `v1.3.1` exist). Semantic-release is tag-driven, so we should create a **baseline tag** matching the version currently on PyPI.

**Recommendation:**
1. Merge PR #19 first (it bumps `1.5.0 -> 1.6.0` for the pandas/json2excel removal)
2. Confirm `1.6.0` is published
3. Create and push tag `v1.6.0` on the exact commit that shipped
4. Then enable semantic-release automation

If you prefer enabling semantic-release before merging PR #19, use baseline `v1.5.0` instead.

---

### Task 1: Create a dedicated worktree for release automation

**Skill:** `superpowers:using-git-worktrees`

**Steps**
1. Create a worktree branch `chore/semantic-release`.
2. Ensure it is based on `origin/main` (or on `main` after PR #19 is merged).

**Commands**
- Run: `git fetch --all --tags`
- Run: `git worktree add ../fx_bin-semrel chore/semantic-release origin/main`

Expected: a clean worktree at `../fx_bin-semrel`.

---

### Task 2: Establish a baseline git tag that matches PyPI

**Files:** none

**Step 1: Verify which version is currently on PyPI**
- Run: `curl -s https://pypi.org/pypi/fx-bin/json | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])"`
Expected: prints the latest published version (currently `1.5.0`).

**Step 2: Verify `pyproject.toml` version on `main`**
- Run: `git show origin/main:pyproject.toml | grep '^version'`
Expected: matches the PyPI version.

**Step 3: Create baseline tag on the commit you’re treating as ‘released’**
Option A (after PR #19 merged): tag `v1.6.0`
- Run: `git tag -a v1.6.0 -m "release: v1.6.0"`
- Run: `git push origin v1.6.0`

Option B (before PR #19 merged): tag `v1.5.0`
- Run: `git tag -a v1.5.0 -m "release: v1.5.0"`
- Run: `git push origin v1.5.0`

Expected: `git tag -l | grep v1\.5\.0` (or v1.6.0) shows the baseline tag.

---

### Task 3: Add semantic-release configuration to `pyproject.toml`

**Files:**
- Modify: `/Users/frank/Projects/fx_bin/pyproject.toml`

**Goal:**
- Define where the version lives (`tool.poetry.version`)
- Ensure tags use `v{version}`
- Define which commit types trigger bumps
- Configure changelog output to `CHANGELOG.md`

**Step 1: Add semantic-release configuration (minimal, conventional commits)**
Add a new section near the bottom:

```toml
[tool.semantic_release]
tag_format = "v{version}"
version_toml = ["pyproject.toml:tool.poetry.version"]
version_variables = [
    "fx_bin/__init__.py:__version__",
]
commit_parser = "conventional"

[tool.semantic_release.commit_parser_options]
# Only bump on conventional types (typical industry default)
minor_tags = ["feat"]
patch_tags = ["fix", "perf"]
# Avoid treating merge commits like 'Merge pull request ...' as releases
ignore_merge_commits = true
parse_squash_commits = true

[tool.semantic_release.changelog.default_templates]
changelog_file = "CHANGELOG.md"
output_format = "md"
```

**Notes / policy**
- For breaking changes, require `feat!:` / `fix!:` or a `BREAKING CHANGE:` footer so semantic-release can bump major.

**Step 2: Validate TOML formatting**
- Run: `poetry run python -c "import tomllib; tomllib.loads(open('pyproject.toml','rb').read())"` (Py3.11+)
Expected: no output, exit code 0.

---

### Task 4: Add a GitHub Actions workflow to run semantic-release on `main`

**Files:**
- Create: `/Users/frank/Projects/fx_bin/.github/workflows/semantic-release.yml`

**Step 1: Create workflow**

```yaml
name: Semantic Release

on:
  push:
    branches: [ main ]

jobs:
  release:
    # Prevent infinite loop when the workflow itself pushes release commits
    if: github.actor != 'github-actions[bot]'
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Semantic Version Release
        uses: python-semantic-release/python-semantic-release@v9
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          git_committer_name: "github-actions[bot]"
          git_committer_email: "41898282+github-actions[bot]@users.noreply.github.com"
```

Expected behavior:
- On pushes to `main`, semantic-release evaluates commit messages since the last `v*` tag.
- If no bump-worthy commits, it does nothing.
- If bump-worthy commits, it:
  - Updates `pyproject.toml` + `fx_bin/__init__.py` + `CHANGELOG.md`
  - Commits those changes
  - Creates a tag like `v1.6.1`
  - Pushes commit + tag

---

### Task 5: Modify PyPI deployment workflow to publish on tags (not on every main push)

**Files:**
- Modify: `/Users/frank/Projects/fx_bin/.github/workflows/main.yml` (currently ‘Deploy to PyPi’)

**Goal:** Only publish when semantic-release creates a version tag.

**Step 1: Change triggers**
Replace:
```yaml
on:
  push:
    branches:
      - main
```
With:
```yaml
on:
  push:
    tags:
      - 'v*'
```

**Step 2: Keep the existing PyPI version-exists check (optional safety)**
The current workflow checks PyPI for the version and skips if it exists. Keeping it is fine.

**Step 3: Ensure checkout uses the tagged ref**
`actions/checkout@v4` already checks out the tag by default on tag pushes.

---

### Task 6: Local dry-run verification

**Files:** none

**Step 1: Dry-run semantic-release locally (no changes)**
Use pipx without adding dependencies to the repo:
- Run: `pipx run python-semantic-release version --noop -vv`
Expected:
- If baseline tag exists and no bump-worthy commits: “No release will be made” (or equivalent).

**Step 2: Create a dummy bump commit and confirm expected bump (optional)**
- Run: `git commit --allow-empty -m "fix: test semantic-release bump"`
- Run: `pipx run python-semantic-release version --noop -vv`
Expected: Next version is a patch bump.

Then reset the dummy commit if you don’t want it.

---

### Task 7: CI verification

**Step 1: Ensure normal CI still runs on PRs**
- Open a PR with these workflow changes.
- Confirm `.github/workflows/tdd-test.yml` still runs.

**Step 2: Ensure semantic-release workflow is present but does not release on PR**
- It should only run on `push` to `main`.

---

### Task 8: Commit and open PR

**Step 1: Commit workflow + config changes**
- Run: `git add pyproject.toml .github/workflows/semantic-release.yml .github/workflows/main.yml`
- Run: `git commit -m "ci: add semantic-release version automation"`

**Step 2: Push branch and create PR**
- Run: `git push -u origin chore/semantic-release`
- Run: `gh pr create --title "ci: automate versioning with python-semantic-release" --body "..."`

---

## Rollout checklist (after merge)

- Confirm baseline tag exists (`v1.5.0` or `v1.6.0`).
- Merge semantic-release PR.
- Merge a small `fix:` PR and confirm:
  - semantic-release creates a release commit + tag.
  - Deploy workflow publishes on the tag.
