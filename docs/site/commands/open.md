# Command: fx open

Open saved URLs, local files, images, and direct targets from the `fx` CLI.

`fx open` is useful when you want fast access to recurring resources without
keeping many browser tabs open. Saved targets live in a local TOML registry and
can be selected by slug, filtered index, or tag.

---

## Usage

```bash
fx open [OPTIONS] [TOKEN...]
fx open add TARGET [OPTIONS]
fx open search QUERY [OPTIONS]
```

## Common Commands

```bash
# List saved targets
fx open

# Open by slug
fx open cc-usage

# Open by 1-based index
fx open 3

# Filter before listing or selecting
fx open --tag usage
fx open --tag usage 2

# Search by name, slug, tags, or target URL
fx open search usage
fx open search --tag live snooker

# Open direct targets
fx open https://example.com
fx open ./diagram.png --app Preview

# Add a saved URL; bare domains are normalized to https URLs
fx open add yahoo.co.jp --name "Yahoo! JAPAN" --slug yahoo-jp --entry-tag portal --yes

# Ask an external AI command to propose metadata
FX_OPEN_AI_COMMAND="my-link-metadata" fx open add https://example.com --ai --yes
```

---

## Config

Default config path:

- POSIX/macOS: `${XDG_CONFIG_HOME}/fx-bin/open.toml` when `XDG_CONFIG_HOME` is
  set, otherwise `~/.config/fx-bin/open.toml`
- Windows: `%APPDATA%\fx-bin\open.toml` when `APPDATA` is set, otherwise
  `~/.config/fx-bin/open.toml` under the user's home directory

Use `--config PATH` to read or write a different registry:

```bash
fx open --config ./open.toml
fx open --config ./open.toml add https://example.com --yes
```

Example `open.toml`:

```toml
[[items]]
order = 10
name = "Claude Code usage"
slug = "cc-usage"
target = "https://example.com/claude-code-usage"
tags = ["usage", "claude-code"]
browser = "Google Chrome"
```

Supported item fields:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | yes | Display name |
| `slug` | string | yes | Stable selector |
| `target` | string | yes | `http`, `https`, or local path |
| `order` | non-negative integer | no | Sort key |
| `tags` | list of strings | no | Filter labels |
| `browser` | string | no | macOS URL browser override |
| `app` | string | no | macOS local file app override |

---

## Selection Rules

`fx open TOKEN` resolves in this order:

1. `http://` and `https://` tokens are direct URLs.
2. Explicit paths are local paths. Examples: `./file.png`, `/tmp/file.png`,
   `~/Downloads/file.pdf`, and `folder/file.md`.
3. Numeric tokens are 1-based indices in the current filtered view.
4. Exact slug matches win over bare local filenames.
5. Bare local filenames are opened only when no slug matches.

Examples:

```bash
fx open readme      # slug first, then local file named readme
fx open ./readme    # always local path
fx open 3           # index 3
fx open ./3         # local path named 3
```

Unsupported schemes such as `file://`, `javascript:`, and `data:` are rejected.
Local paths must resolve to regular files; directories, sockets, devices, and
symlink loops are rejected.

---

## Search Workflow

```bash
fx open search QUERY [--tag TAG] [--all | --disabled]
```

Search lists saved targets whose `name`, `slug`, `tags`, or `target` contains
`QUERY` as a case-insensitive substring. It uses the same responsive ASCII table
as `fx open` list output. Result indices are preserved from the current visible
list, so `fx open <index>` or `fx open --tag TAG <index>` can open a matching
enabled target.

Examples:

```bash
fx open search snooker
fx open search usage
fx open search --tag usage claude
fx open search --all old-dashboard
```

Search is list-only in this version. Use the displayed slug or preserved index
to open the target.

---

## Add Workflow

```bash
fx open add TARGET [--name NAME] [--slug SLUG] [--entry-tag TAG] [--yes]
```

`fx open add` normalizes targets before writing config:

- `https://example.com` is stored as provided.
- `yahoo.co.jp` is stored as `https://yahoo.co.jp`.
- Existing local files are stored as normalized absolute paths.

It also generates deterministic metadata when fields are omitted:

- URL slugs use the host with leading `www.` removed.
- Local file slugs use the filename stem.
- Duplicate and reserved slugs are rejected.
- Default `order` is max existing order plus 10, starting at 10.

Use `--entry-tag` for metadata tags. `--tag` is reserved for list/open filters
and is invalid in the add workflow.

```bash
fx open add https://www.yahoo.co.jp --entry-tag portal --entry-tag japan --yes
```

In non-interactive mode, `--yes` is required.

---

## AI Metadata

`--ai` calls the external command configured in `FX_OPEN_AI_COMMAND`.

Provider stdin:

```json
{"target":"https://example.com","existing_slugs":["example"],"allowed_fields":["name","slug","tags"]}
```

Provider stdout:

```json
{"name":"Example","slug":"example-docs","tags":["docs"]}
```

Rules:

- The provider must return valid JSON.
- Only `name`, `slug`, and `tags` are accepted.
- CLI options override AI output.
- AI output is validated before the TOML registry is written.
- Provider timeout, non-zero exit, and invalid JSON fail the command.

---

## Platform Behavior

- macOS: uses `open`; `--browser` and `--app` use `open -a`.
- Linux: uses `xdg-open`; explicit app/browser selection is not supported in v1.
- Windows: uses the platform default opener; explicit app/browser selection is
  not supported in v1.

Dispatch uses argument-vector subprocess calls or platform APIs, not shell
string execution.
