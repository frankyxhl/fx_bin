# REF-2117: Discussion Tracker 2026-08-13

**Applies to:** FXB project
**Last updated:** 2026-08-13
**Last reviewed:** 2026-08-13
**Status:** Active

---

## What Is It?

Tracks FXB discussion items raised on 2026-08-13.

---

## Active Items

| DN | Status | Parent | Source | Created | Updated | Topic |
|----|--------|--------|--------|---------|---------|-------|
| D1 | WIP | — | User | 19:42 | — | Add `fx repo` command to open the current GitHub repository |

## Archived Items

| DN | Parent | Source | Topic |
|----|--------|--------|-------|

## Discussion Notes

### D1: Add `fx repo` command to open the current GitHub repository

- **Alignment**: crisp; command is `fx repo`; GitHub.com only; prefer `origin`, support `--remote`, and use a single non-origin remote automatically.
- **Missing remote**: print `No Git remote found for the current directory.` and exit non-zero.
- **Process**: user explicitly selected a Normal CHG instead of a separate PRP; implementation will follow COR-1500 TDD.
- **Approval**: Frank Xu approved FXB-2118 and requested implementation plus a reviewable PR.
- **Implementation**: three RED→GREEN cycles completed; full suite passed with 86.76% coverage; publishing a reviewable PR from the `ryosaeba1985` fork.
- **PR**: `frankyxhl/fx_bin#92` opened as ready for review by `ryosaeba1985`.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-08-13 | Created tracker and recorded D1 | Codex |
