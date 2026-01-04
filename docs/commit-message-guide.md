# Commit Message Guide

This guide explains how to write commit messages for fx-bin. We use [Conventional Commits](https://www.conventionalcommits.org/) to enable automated semantic versioning and changelog generation.

## TL;DR Quick Reference

```bash
# Bug fix (Patch: 2.0.0 → 2.0.1)
git commit -m "fix: correct file path validation"

# New feature (Minor: 2.0.0 → 2.1.0)
git commit -m "feat: add incremental backup support"

# Breaking change (Major: 2.0.0 → 3.0.0)
git commit -m "feat!: change CLI argument structure

BREAKING CHANGE: --output flag renamed to --dest"

# No release
git commit -m "docs: update README examples"
```

---

## How It Works

When you merge a PR to `main`, **semantic-release** automatically:

1. ✅ Analyzes all commits since last release
2. ✅ Calculates the next version number
3. ✅ Updates `pyproject.toml` and `fx_bin/__init__.py`
4. ✅ Generates `CHANGELOG.md` entry
5. ✅ Creates a git tag (e.g., `v2.1.0`)
6. ✅ Publishes to PyPI

**You never manually change version numbers!**

---

## Commit Message Format

### Structure

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Examples

#### Simple Commit
```
fix: handle empty directory in filter command
```

#### With Scope
```
feat(backup): add support for .tar.bz2 compression
```

#### With Body
```
feat: add verbose logging mode

Add --verbose flag to enable detailed logging output.
Includes timestamps and severity levels for all log messages.
```

#### With Breaking Change
```
feat!: change configuration file format

BREAKING CHANGE: Configuration now uses YAML instead of JSON.
Users must migrate their config.json to config.yaml using the
included migration tool: fx migrate-config
```

---

## Commit Types and Version Bumps

### Version Format: `MAJOR.MINOR.PATCH`

| Commit Type | Version Impact | Example | Use When |
|-------------|---------------|---------|----------|
| **`feat!:`** or `BREAKING CHANGE:` | **Major** (2.0.0 → 3.0.0) | Remove feature, change API | Breaking existing functionality |
| **`feat:`** | **Minor** (2.0.0 → 2.1.0) | Add backup compression | Adding new features |
| **`fix:`** | **Patch** (2.0.0 → 2.0.1) | Fix path validation | Bug fixes |
| **`perf:`** | **Patch** (2.0.0 → 2.0.1) | Optimize file scanning | Performance improvements |
| `docs:` | **No release** | Update README | Documentation only |
| `style:` | **No release** | Run black formatter | Code formatting |
| `refactor:` | **No release** | Simplify validation logic | Code restructuring |
| `test:` | **No release** | Add edge case tests | Test additions |
| `ci:` | **No release** | Update workflow | CI/CD changes |
| `chore:` | **No release** | Update dependencies | Maintenance tasks |

---

## Detailed Examples by Scenario

### 1. Bug Fixes (`fix:`) → Patch Version

```bash
# Simple bug fix
git commit -m "fix: prevent crash when backup directory does not exist"

# Bug fix with scope
git commit -m "fix(filter): handle symbolic links correctly"

# Bug fix with detailed explanation
git commit -m "fix: correct timezone handling in today command

Previously, the today command used UTC time instead of local time,
causing confusion for users in non-UTC timezones. This fix uses
the system's local timezone for directory creation."
```

### 2. New Features (`feat:`) → Minor Version

```bash
# Simple feature
git commit -m "feat: add --exclude flag to filter command"

# Feature with scope
git commit -m "feat(backup): add support for encrypted backups"

# Feature with details
git commit -m "feat: implement dry-run mode for all commands

Add --dry-run flag that shows what would be done without
actually performing any file operations. Useful for testing
and validation before running destructive operations."
```

### 3. Breaking Changes (`feat!:` or `fix!:`) → Major Version

**Option 1: Using exclamation mark**
```bash
git commit -m "feat!: change default backup compression to .tar.xz"
```

**Option 2: Using BREAKING CHANGE footer (more detailed)**
```bash
git commit -m "feat: redesign CLI argument structure

BREAKING CHANGE: Positional arguments have been replaced with flags.

Before: fx backup myfile.txt backups/
After: fx backup --source myfile.txt --dest backups/

Migration: Update scripts to use new flag-based syntax."
```

**Multiple breaking changes:**
```bash
git commit -m "feat!: major CLI overhaul

BREAKING CHANGE: Renamed --max-backups to --retention-count
BREAKING CHANGE: Removed deprecated --old-format flag
BREAKING CHANGE: Changed default output format from JSON to YAML"
```

### 4. Non-Release Commits

#### Documentation (`docs:`)
```bash
git commit -m "docs: add examples for incremental backups"
git commit -m "docs: update installation instructions for Python 3.12"
git commit -m "docs(backup): clarify compression format options"
```

#### Code Style (`style:`)
```bash
git commit -m "style: apply black formatting to all modules"
git commit -m "style: fix line length violations in cli.py"
```

#### Refactoring (`refactor:`)
```bash
git commit -m "refactor: extract validation logic into separate module"
git commit -m "refactor(backup): simplify compression algorithm selection"
```

#### Tests (`test:`)
```bash
git commit -m "test: add integration tests for backup command"
git commit -m "test: improve coverage for edge cases in filter.py"
git commit -m "test(security): add path traversal attack tests"
```

#### CI/CD (`ci:`)
```bash
git commit -m "ci: add Python 3.13 to test matrix"
git commit -m "ci: optimize workflow to reduce run time"
git commit -m "ci: fix semantic-release PAT configuration"
```

#### Chores (`chore:`)
```bash
git commit -m "chore: update dependencies to latest versions"
git commit -m "chore: remove unused imports"
git commit -m "chore: bump version to 2.1.0"
```

---

## Common Scopes

Scopes help identify which part of the codebase is affected:

| Scope | Description | Example |
|-------|-------------|---------|
| `backup` | Backup command | `feat(backup): add encryption support` |
| `filter` | Filter command | `fix(filter): handle hidden files` |
| `cli` | CLI interface | `feat(cli): add --verbose flag` |
| `config` | Configuration | `feat(config): support YAML format` |
| `docs` | Documentation | `docs(backup): add usage examples` |
| `test` | Testing | `test(filter): add edge cases` |
| `ci` | CI/CD | `ci: add codecov integration` |

Scopes are optional but recommended for larger projects.

---

## Multi-Commit PRs

When your PR has multiple commits, semantic-release analyzes **all of them** to determine the version bump:

```bash
# PR with these commits:
fix: correct validation bug
feat: add new export format
docs: update README

# Result: Minor version bump (2.0.0 → 2.1.0)
# Because feat: triggers minor bump (highest among all commits)
```

**Version bump priority:**
1. **Major** (any `feat!:`, `fix!:`, or `BREAKING CHANGE:`)
2. **Minor** (any `feat:`)
3. **Patch** (any `fix:` or `perf:`)
4. **No release** (only `docs:`, `style:`, `refactor:`, `test:`, `ci:`, `chore:`)

---

## Best Practices

### ✅ Do

- **Be specific**: `fix: handle empty directories` not `fix: bug fix`
- **Use imperative mood**: `add feature` not `added feature` or `adds feature`
- **Keep subject line ≤ 72 characters**
- **Use body for complex changes** to explain why, not what
- **Reference issues**: `fix: correct path validation (fixes #123)`
- **One logical change per commit**

### ❌ Don't

- **Don't use vague messages**: `fix stuff`, `update code`, `changes`
- **Don't combine unrelated changes** in one commit
- **Don't forget the colon**: `fix validation` should be `fix: validation`
- **Don't manually update version numbers** in commits (semantic-release does this)

---

## Commit Message Template

Create a git commit template to help with formatting:

**`.gitmessage` (optional, place in project root):**
```
# <type>[optional scope]: <description>
# 
# [optional body]
# 
# [optional footer(s)]
# 
# Types:
#   feat:     New feature (Minor version)
#   fix:      Bug fix (Patch version)
#   perf:     Performance improvement (Patch version)
#   feat!:    Breaking change (Major version)
#   docs:     Documentation only
#   style:    Code style/formatting
#   refactor: Code restructuring
#   test:     Adding tests
#   ci:       CI/CD changes
#   chore:    Maintenance tasks
# 
# Examples:
#   feat: add user authentication
#   fix(backup): handle missing directories
#   feat!: remove deprecated API endpoints
# 
# Remember: semantic-release handles versioning automatically!
```

**Configure git to use it:**
```bash
git config commit.template .gitmessage
```

---

## Troubleshooting

### "No release will be made"

**Reason:** All commits since last release are non-release types (`docs:`, `style:`, etc.)

**Solution:** Ensure at least one commit uses `feat:`, `fix:`, or `perf:`

### "Unexpected major version bump"

**Reason:** A commit has `!` or `BREAKING CHANGE:` footer

**Check:** Review commits for accidental breaking change markers
```bash
git log --oneline | grep -E "!:|BREAKING"
```

### "Version not updated on PyPI"

**Possible causes:**
1. Semantic-release workflow failed (check Actions tab)
2. PAT expired or missing
3. No release-worthy commits

**Debug:**
```bash
# Check latest workflow run
gh run list --workflow=semantic-release.yml --limit 5

# Check workflow logs
gh run view <run-id> --log
```

---

## FAQ

### Q: Can I manually create releases?

**A:** Yes, but not recommended. If semantic-release fails, you can:
```bash
# Manually tag and push
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin v2.1.0
```

This will trigger PyPI publishing but won't update CHANGELOG or version files.

### Q: How do I skip a release for a hotfix?

**A:** Use non-release commit types:
```bash
git commit -m "chore: hotfix deployment configuration"
```

### Q: Can I combine multiple types?

**A:** No, use the most significant type. If you need both `feat` and `fix`, split into two commits.

### Q: What if I forgot to use conventional format?

**A:** Use `git commit --amend` before pushing:
```bash
git commit --amend -m "feat: add new feature"
```

After push, you'll need to:
1. Revert the commit
2. Make a new commit with correct format

---

## Related Resources

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Semantic Versioning (SemVer)](https://semver.org/)
- [Python Semantic Release Docs](https://python-semantic-release.readthedocs.io/)
- [Keep a Changelog](https://keepachangelog.com/)

---

## Quick Decision Tree

```
What changed?
├─ Breaking existing functionality? → feat!: or BREAKING CHANGE:
├─ New feature added? → feat:
├─ Bug fixed? → fix:
├─ Performance improved? → perf:
├─ Documentation only? → docs:
├─ Code formatting only? → style:
├─ Code restructured (no behavior change)? → refactor:
├─ Tests added/modified? → test:
├─ CI/CD changes? → ci:
└─ Everything else? → chore:
```

---

**Remember: Good commit messages are a gift to your future self and your team!**
