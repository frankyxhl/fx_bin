# CHG-2102: Clarify FX Open Browser Selection Defaults

**Applies to:** FXB project
**Last updated:** 2026-05-05
**Last reviewed:** 2026-05-05
**Status:** Completed
**Related:** COR-1101, FXB-2100
**Date:** 2026-05-05
**Requested by:** Frank Xu
**Priority:** Medium
**Change Type:** Normal

---

## What

Clarify and preserve the `fx open` browser-selection policy:

1. By default, saved URL entries should not specify a browser.
2. When no browser is specified, `fx open` should let the operating system open
   the URL with the user's default browser.
3. Only URL entries that need a dedicated browser should set per-item
   `browser = "<Application Name>"` in `open.toml`.
4. `fx open <selector> --browser "<Application Name>"` remains the temporary
   command-line override and takes precedence over per-item config.
5. The browser field name is exactly `browser`; typos such as `brower` must
   remain invalid through the existing unknown-item-key validation.

This CHG is primarily a behavior and documentation clarification. The current
implementation already supports the desired default/override model on macOS.

## Why

The user wants most saved links to behave naturally with the system default
browser, while allowing a small number of testing or account-specific links to
open in Firefox or another browser.

This avoids over-configuring every saved URL and keeps the local registry easy
to maintain:

```toml
[[items]]
order = 10
name = "Claude Code usage"
slug = "cc-usage"
target = "https://example.com/usage"
tags = ["usage", "claude-code"]

[[items]]
order = 20
name = "Firefox test page"
slug = "firefox-test"
target = "https://example.com/test"
tags = ["test"]
browser = "Firefox"
```

## Impact Analysis

- **Systems affected:**
  - `README.md` and command/help examples for `fx open`
  - Existing `fx open` behavior documentation
  - Tests only if documentation examples or behavior assertions are adjusted
- **User-facing behavior:** No required behavior change. This records the
  intended policy for using the existing `browser` field and `--browser`
  option.
- **Platform scope:** Explicit browser selection is currently macOS-only because
  dispatch uses `open -a <Application Name> <URL>`. Linux and Windows continue
  to use OS defaults in v1. A per-item `browser` field may exist in a portable
  config, but it is only honored on macOS; on Linux and Windows v1 falls back to
  the OS default opener rather than launching that named browser.
- **Compatibility:** Existing configs remain valid. Entries without `browser`
  keep working. Entries with `browser` keep working on macOS. Unknown item keys
  remain rejected, so `brower` fails fast instead of being ignored.
- **Rollback plan:** Revert documentation/test changes. No config migration is
  required.

## Implementation Plan

1. Keep the implementation default unchanged:
   - macOS URL default: `open <url>`
   - macOS explicit browser: `open -a <browser> <url>`
   - Linux URL default: `xdg-open <url>`
   - Windows URL default: `os.startfile(url)`
2. Document the recommended config style:
   - omit `browser` for normal links
   - set `browser` only for special-case links
   - use CLI `--browser` for one-off testing
   - note that per-item `browser` is macOS-only in v1 and ignored by Linux and
     Windows dispatch
3. Make examples explicit that the field is `browser`, not `brower`.
4. Preserve validation behavior:
   - `browser` is allowed only for URL targets
   - `app` is allowed only for local path targets
   - unknown item fields are rejected
5. If implementation work touches this area, add or preserve tests proving:
   - URL item without `browser` uses OS default dispatch
   - URL item with per-item `browser` uses that browser on macOS
   - CLI `--browser` overrides per-item `browser`
   - misspelled item key `brower` is rejected

## Acceptance Criteria

- The recommended default is documented as "do not set `browser` unless the
  entry needs a specific browser."
- Per-item `browser` config remains available for special cases.
- CLI `--browser` remains available for temporary overrides.
- The docs clearly show Firefox and explain that another macOS application name
  can be used.
- The docs mention that explicit browser selection is macOS-only in v1.
- The docs mention that non-macOS systems ignore per-item browser preferences in
  v1 and use the OS default opener.
- Existing `fx open` behavior remains unchanged unless a later implementation
  task intentionally updates docs or tests.

## Testing / Verification

Implementation completed on 2026-05-05. README and `fx open --help` now state
that omitted browser settings use the OS default browser, per-entry `browser`
and CLI `--browser` are macOS-only explicit selections, and examples use
Firefox or a generic macOS application name. Unit tests validate dispatch plans
without requiring any named browser to be installed locally.

COR-1602/COR-1610 implementation review completed on 2026-05-05 with DeepSeek
PASS and GLM PASS.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-05-05 | Initial version | af CLI |
| 2026-05-05 | Filled change request with default browser selection policy | Codex |
| 2026-05-05 | Addressed Trinity review: document non-macOS browser preference fallback | Codex |
| 2026-05-05 | Adjusted examples to avoid requiring Microsoft Edge on the local machine | Codex |
| 2026-05-05 | Implemented documentation/help clarification and dispatch-plan tests | Codex |
| 2026-05-05 | Completed implementation review with DeepSeek and GLM PASS | Codex |
