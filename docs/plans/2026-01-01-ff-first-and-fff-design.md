# Design: fx ff --first + fff Command

**Date**: 2026-01-01  
**Status**: Approved  
**Author**: AI Assistant + User

## Summary

Add `--first` option to `fx ff` command to return only the first match and exit early (for speed). Also add `fff` as a shortcut alias.

## Requirements

1. `fx ff <keyword> --first` - return first match only, exit immediately
2. `fx fff <keyword>` - equivalent to `fx ff <keyword> --first`

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Flag name | `--first` | Clear intent, self-documenting |
| `fff` parameters | keyword only | Keep it simple; no `--exclude` etc. |
| `fff` in `fx list` | Yes | Discoverable by users |
| Implementation | Shared `_run_ff()` function | DRY, maintainable |

## Implementation

### 1. `fx_bin/find_files.py`

Add `first: bool = False` parameter to `find_files()`:

```python
def find_files(
    keyword: str,
    include_ignored: bool = False,
    exclude: Optional[List[str]] = None,
    first: bool = False,
) -> None:
    ...
    for name in dirs + files:
        if keyword in name and not is_excluded(name):
            click.echo(os.path.join(root, name))
            if first:
                return  # Early exit
```

### 2. `fx_bin/cli.py`

Add shared helper and new command:

```python
def _run_ff(keyword: str, include_ignored: bool, excludes: tuple, first: bool) -> int:
    from . import find_files
    if not keyword or keyword.strip() == "":
        click.echo("Please type text to search.", err=True)
        return 1
    find_files.find_files(keyword, include_ignored=include_ignored,
                          exclude=list(excludes), first=first)
    return 0

@cli.command()
@click.argument("keyword")
@click.option("--first", is_flag=True, default=False, help="Stop after first match")
@click.option("--include-ignored", ...)
@click.option("--exclude", ...)
def ff(keyword, first, include_ignored, excludes):
    return _run_ff(keyword, include_ignored, excludes, first)

@cli.command()
@click.argument("keyword")
def fff(keyword):
    """Find first file matching KEYWORD. Alias for `fx ff --first`."""
    return _run_ff(keyword, include_ignored=False, excludes=(), first=True)
```

### 3. Update `COMMANDS_INFO`

```python
("fff", "Find first file matching keyword (alias for ff --first)"),
```

## Testing

1. `ff --first` outputs exactly 1 line when matches exist
2. `fff <keyword>` behaves identically to `ff <keyword> --first`
3. No match case: exit 0, no output

## Files Changed

- `fx_bin/find_files.py` - add `first` parameter
- `fx_bin/cli.py` - add `_run_ff`, `--first` flag, `fff` command
- `tests/unit/test_find_files.py` - add tests
