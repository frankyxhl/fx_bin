# Implementation Plans

This directory contains implementation plans and design documents for fx-bin.

## Active Plans

### 2026-01-05

- **[Common Utilities Refactoring](./2026-01-05-timestamp-utility-refactoring.md)** (2026-01-05)  
  Consolidate timestamps, multi-part extensions (e.g. `.tar.gz`), and size formatting into `fx_bin/common.py` to eliminate duplication and improve correctness.

## Completed Plans

### 2026-01-03

- **[Add Backup Command](./completed-2026-01-03-add-backup-command.md)** (2026-01-03)  
  Add `fx backup` command with timestamped backups, compression, and automatic cleanup.

### 2026-01-01

- **[Cleanup and Hardening](./completed-2026-01-01-cleanup-and-hardening.md)** (2026-01-01)  
  Remove pandas/json2excel dependencies, fix Oracle review findings, strengthen CI/CD.

- **[ff --first + fff Design](./completed-2026-01-01-ff-first-and-fff-design.md)** (2026-01-01)  
  Add `--first` option to `fx ff` and `fx fff` alias command.

- **[Python Semantic Release Automation](./completed-2026-01-01-python-semantic-release-automation.md)** (2026-01-01)  
  **CANCELLED** - Automated versioning with python-semantic-release (abandoned).

### 2026-01-02

- **[fx realpath Design](./completed-2026-01-02-fx-realpath-design.md)** (2026-01-02)  
  Add `fx realpath` command to get absolute path of files/directories.

---

## Convention

Plan files follow this naming convention:

- **Active plans:** `YYYY-MM-DD-short-title.md`
- **Completed plans:** `completed-YYYY-MM-DD-short-title.md`

Each plan file includes a `Status:` header block indicating its current state.
