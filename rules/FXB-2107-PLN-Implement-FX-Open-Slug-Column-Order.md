# PLN-2107: Implement FX Open Slug Column Order

**Applies to:** FXB project
**Last updated:** 2026-05-07
**Last reviewed:** 2026-05-07
**Status:** Active
**Related:** FXB-2106, COR-1202, COR-1500, COR-1615, COR-1612

---

## What Is It?

Implementation plan for FXB-2106, moving the `fx open` table `Slug` column to
the second position after the index column.

---

## Goals

- Make short 2-3 character slugs immediately visible next to the `#` index.
- Preserve all existing `fx open` behavior except display column order.
- Use TDD to protect normal list, search, and disabled/all table output.
- Publish via a ready PR, use COR-1615 for GitHub Codex review triggering and
  polling, and follow COR-1612 if actionable review comments arrive.

## Milestones

| # | Milestone | Target Date | Status |
|---|-----------|-------------|--------|
| 1 | Planning and branch setup | 2026-05-05 | Complete |
| 2 | Trinity fast-review approval gate | 2026-05-05 | Complete |
| 3 | RED tests for column order | 2026-05-05 | Complete |
| 4 | GREEN formatter update | 2026-05-05 | Complete |
| 5 | REFACTOR and Trinity code fast-review | 2026-05-05 | Complete |
| 6 | Verification | 2026-05-05 | Complete |
| 7 | Ready PR, CI, and COR-1615 review loop | 2026-05-05 | Complete |
| 8 | Merge and release verification | 2026-05-05 | Complete |

---

## Implementation Steps

1. Create an implementation branch from latest `origin/main`.
2. Before RED tests or implementation, run Trinity fast-review against the
   current FXB-2106/FXB-2107 plan and require approval:
   - confirm provider readiness with `trinity doctor --preset fast-review`
   - run `trinity review --preset fast-review --scope rules`
   - treat approval as both fast-review providers passing with no blocking
     findings
   - revise the plan before implementation if Trinity reports a blocker
3. Commit FXB-2106 and this PLN with the implementation if no separate docs-only
   commit is needed.
4. RED:
   - update unit table formatter tests to expect `| # | Slug | Name |`
   - add/adjust disabled/all test to expect `| # | Slug | State | Name |`
   - add/adjust tag-filtered list output tests to assert the same column order
   - add/adjust search CLI output test to assert the same order and preserved
     search index behavior
5. GREEN:
   - update `fx_bin/open_launcher.py` column construction order to `#`, `Slug`,
     optional `State`, `Name`, `Tags`, `Target`
   - do not change item sorting, selector resolution, search matching, dispatch,
     or config schema
6. REFACTOR:
   - keep formatter implementation simple and localized
   - update docs only if they show table column order
7. Code review gate via Trinity fast-review:
   - run `trinity doctor --preset fast-review`
   - run `trinity review --preset fast-review --scope .`
   - require both fast-review providers to pass with no blocking findings before
     proceeding to verification and PR publication
   - if Trinity reports a blocker, fix it, rerun focused RED/GREEN checks as
     needed, then rerun Trinity fast-review
8. Verify:
   - `poetry run pytest tests/unit/test_open_launcher.py tests/integration/test_open_cli.py -q --no-cov`
   - `poetry run black --check fx_bin/open_launcher.py tests/unit/test_open_launcher.py tests/integration/test_open_cli.py`
   - `poetry run flake8 fx_bin/ --statistics`
   - `python3 -m ruff check fx_bin/open_launcher.py tests/unit/test_open_launcher.py tests/integration/test_open_cli.py`
   - `af validate`
9. Publish:
   - verify `gh auth status` uses `ryosaeba1985`
   - push branch to fork
   - open ready PR, not draft
   - monitor GitHub CI
10. GitHub Codex review loop via COR-1615:
   - record PR number and current `headRefOid`
   - verify `gh auth status` before visible PR comments
   - trigger exactly one Codex review request for the current head when needed
   - do not duplicate `@codex review` while a request for the same head is
     pending
   - treat acknowledgement reactions such as `eyes` as queued/in-progress, not
     approval
   - poll PR state, review summaries, top-level comments, and inline comments
     every 3-5 minutes using JST timetable sleep when waiting
   - match any review result to the current `headRefOid`; stale reviews do not
     clear a newer push
11. Review comment handling via COR-1612:
   - classify fetched findings as blocking, advisory, question, or incorrect
   - fix blockers and adopted advisories in focused commits
   - reply with concrete verification
   - after every push, return to COR-1615 Step 1 for the new `headRefOid`
12. Release:
   - after merge, confirm semantic-release tag, GitHub Release, PyPI, and docs
     deploy.

## Risks / Controls

- **Risk:** Moving columns changes output consumed by scripts.
  **Control:** Keep change documented as human-facing display behavior and limit
  scope to table rendering.
- **Risk:** Optional `State` column could move `Slug` away from column 2.
  **Control:** Explicit tests for disabled/all output.
- **Risk:** Responsive truncation could regress.
  **Control:** Keep existing width-fitting tests and rerun focused suite.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-05-05 | Initial version | af CLI |
| 2026-05-05 | Filled implementation plan for FXB-2106 | Codex |
| 2026-05-05 | Revised PR review phase to use COR-1615 before COR-1612 | Codex |
| 2026-05-05 | Added Trinity fast-review approval gate before RED tests | Codex |
| 2026-05-05 | Addressed Trinity fast-review advisories | Codex |
| 2026-05-05 | Added tag-filtered RED coverage and Flake8 verification | Codex |
| 2026-05-05 | Added Trinity code fast-review gate before verification | Codex |
| 2026-05-07 | Implementation complete (shipped in v2.10.0) | Claude Code |
