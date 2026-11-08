# CHG-2120: Add Forgejo CI Workflow

**Applies to:** FXB project
**Last updated:** 2026-11-09
**Last reviewed:** 2026-11-09
**Status:** Proposed
**Date:** 2026-11-09
**Requested by:** saeba (D3718, forgejo 4e49fb5d)
**Priority:** Medium
**Change Type:** Normal

---

## What

Add `.forgejo/workflows/ci.yml`: one job that checks out, sets up Python 3.12, installs Poetry with `pip install poetry`, runs `poetry install --with dev`, flake8 on `fx_bin/`, and the same pytest command as the GitHub Tests job. Pull requests to main only. `.github/workflows` is not touched.

## Why

The Forgejo runner resolves `uses:` actions against data.forgejo.org, which lacks `snok/install-poetry`, `github/codeql-action`, `python-semantic-release` and `peaceiris/actions-gh-pages`, so every `.github/workflows` job fails there in about 5 seconds. Forgejo 16.0.3 reads `.forgejo/workflows` first and ignores `.github/workflows` when it exists (forgejo, ListWorkflows), so a separate file fixes Forgejo CI without changing the GitHub CI that fx_bin also uses.

## Impact Analysis

- **Systems affected:** Forgejo Actions for pilot/fx_bin only. GitHub Actions unchanged. Once `.forgejo/workflows` is in a commit tree, `.github/workflows` no longer runs on Forgejo for that tree (CodeQL, docs deploy and release stay GitHub-only).
- **Limit:** the rule is per commit tree, so a branch without `.forgejo/workflows` (PR 1) keeps running `.github` until main is merged into it.
- **Rollback plan:** delete `.forgejo/workflows/ci.yml`; Forgejo falls back to `.github/workflows`.

## Implementation Plan

1. Add `.forgejo/workflows/ci.yml`.
2. Open the PR; the new workflow runs on the PR itself.
3. After merge, merge main into open PR branches with a normal merge commit.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-11-09 | Initial version | fx-bin |
