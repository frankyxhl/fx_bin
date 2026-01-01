# Migration Guide: fx-bin v1.1.0

## Overview

FX-bin v1.1.0 introduces **breaking changes** that remove all legacy individual command entries in favor of the unified `fx` command structure. This guide helps you migrate from the old commands to the new ones.

## Breaking Changes Summary

### 1. Removed fx_upgrade Functionality
The `fx_upgrade` command has been **completely removed** with no replacement. If you were using this functionality, you'll need to implement your own upgrade mechanism.

### 2. Removed Legacy Command Entries
All individual `fx_*` command entries have been removed from the package. These commands are now only available through the unified `fx` command.

## Command Migration Table

| Old Command (v1.0.x) | New Command (v1.1.0+) | Status |
|----------------------|------------------------|--------|
| `fx_files` | `fx files` | ✅ Available |
| `fx_size` | `fx size` | ✅ Available |
| `fx_ff` | `fx ff` | ✅ Available |
| `fx_replace` | `fx replace` | ✅ Available |
| `fx_grab_json_api_to_excel` | ~~`fx json2excel`~~ | ❌ **REMOVED in v1.5.0** |
| `fx_upgrade` | ❌ **REMOVED** | ❌ No replacement |

## Migration Steps

### Step 1: Update Your Scripts

**Before (v1.0.x):**
```bash
fx_files /path/to/directory
fx_size /path/to/directory
fx_ff test
fx_replace "old" "new" file.txt
fx_grab_json_api_to_excel data.json output.xlsx
fx_upgrade
```

**After (v1.1.0+):**
```bash
fx files /path/to/directory
fx size /path/to/directory
fx ff test
fx replace "old" "new" file.txt
# fx_grab_json_api_to_excel was removed in v1.5.0 (pandas dependency dropped)
# fx_upgrade is no longer available
```

### Step 2: Update Shell Aliases

If you have shell aliases, update them:

**Before:**
```bash
alias count_files="fx_files"
alias check_sizes="fx_size"
alias find_files="fx_ff"
```

**After:**
```bash
alias count_files="fx files"
alias check_sizes="fx size"
alias find_files="fx ff"
```

### Step 3: Update Build Scripts and CI/CD

Update any automation scripts, Makefiles, or CI/CD configurations:

**Before (Makefile example):**
```makefile
analyze:
	fx_size .
	fx_files .
```

**After:**
```makefile
analyze:
	fx size .
	fx files .
```

### Step 4: Update Documentation

Update any internal documentation or README files that reference the old commands.

## New Features in v1.1.0

### Command Discovery
List all available commands:
```bash
fx list
```

### Improved Help System
Get help for the main command:
```bash
fx --help
```

Get help for specific subcommands:
```bash
fx files --help
fx size --help
fx ff --help
fx replace --help
```

## Compatibility Check Script

You can use this script to check if your environment has commands that need migration:

```bash
#!/bin/bash
# check_migration.sh - Check for legacy fx commands

echo "Checking for legacy fx commands that need migration..."

LEGACY_COMMANDS=("fx_files" "fx_size" "fx_ff" "fx_replace" "fx_grab_json_api_to_excel" "fx_upgrade")

for cmd in "${LEGACY_COMMANDS[@]}"; do
    if command -v "$cmd" &> /dev/null; then
        if [ "$cmd" = "fx_upgrade" ] || [ "$cmd" = "fx_grab_json_api_to_excel" ]; then
            echo "❌ $cmd: REMOVED - No replacement available"
        else
            NEW_CMD=$(echo "$cmd" | sed 's/fx_/fx /')
            echo "⚠️  $cmd: Replace with '$NEW_CMD'"
        fi
    fi
done

echo "Migration check complete."
```

## Rollback Instructions

If you need to rollback to v1.0.x temporarily:

```bash
pip install fx-bin==1.0.1
```

However, we recommend migrating to the new commands as soon as possible, as v1.0.x will not receive future updates.

## Troubleshooting

### Command Not Found
If you get "command not found" errors:

1. **Check your fx-bin version:**
   ```bash
   pip show fx-bin
   ```

2. **Verify the unified command works:**
   ```bash
   fx --version
   fx list
   ```

3. **Reinstall if necessary:**
   ```bash
   pip uninstall fx-bin
   pip install fx-bin
   ```

### Script Failures
If your existing scripts fail:

1. **Check the exact commands used** in your scripts
2. **Replace legacy commands** using the migration table above
3. **Test the new commands** before deploying

### Missing fx_upgrade Functionality
If you depended on `fx_upgrade`:

1. **Remove any scripts** that call `fx_upgrade`
2. **Implement custom upgrade logic** if needed
3. **Use standard pip commands** for package updates:
   ```bash
   pip install --upgrade fx-bin
   ```

## Support

If you encounter issues during migration:

1. **Check the documentation:** Updated README.rst and CLAUDE.md
2. **Review the changelog:** HISTORY.rst for detailed changes
3. **File an issue:** https://github.com/frankyxhl/fx_bin/issues

## Benefits of Migration

After migration, you'll benefit from:

- ✅ **Simplified CLI** with consistent command structure
- ✅ **Better command discovery** with `fx list`
- ✅ **Improved help system** with unified documentation
- ✅ **Cleaner installation** with fewer command entries
- ✅ **Future-ready architecture** for new features

## Timeline

- **v1.0.x:** Legacy commands deprecated but still available
- **v1.1.0:** Legacy commands removed (current)
- **Future versions:** New features will only be added to the unified CLI

Make sure to complete your migration before upgrading to v1.1.0 or later.
