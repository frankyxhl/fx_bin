# Use Case: Dataset Management

Organize datasets by date for easier management and analysis.

## Overview

Datasets often accumulate over time without proper organization. This use case demonstrates how to use `fx organize` to structure datasets by date, making them easier to find, analyze, and manage.

## Dataset Organization Workflow

### 1. Preview Organization Plan

Always preview before organizing:

```bash
# Preview organization with dry-run
fx organize ~/Data --dry-run

# Output shows plan without moving files
# Review to ensure correct behavior
```

### 2. Organize by Creation Date

Organize datasets by creation time:

```bash
# Basic organization
fx organize ~/Data

# Output directory: ~/Data/organized/
# Structure: organized/2026/202601/20260110/
```

### 3. Filter by File Type

Organize only specific dataset types:

```bash
# Organize only CSV files
fx organize ~/Data -i "*.csv" --recursive

# Organize only JSON datasets
fx organize ~/Data -i "*.json" --recursive

# Organize multiple types
fx organize ~/Data -i "*.csv" -i "*.json" -i "*.parquet" --recursive
```

### 4. Custom Depth and Output

Configure organization structure:

```bash
# Use 2-level depth (year/day)
fx organize ~/Data --depth 2 -o ~/Data/Organized

# Use 1-level depth (day only)
fx organize ~/Data --depth 1 -o ~/Data/Simple
```

### 5. Clean Up Empty Directories

Remove empty source directories after organization:

```bash
# Organize and clean empty directories
fx organize ~/Data --recursive --clean-empty
```

## Real-World Scenarios

### Scenario 1: Research Data Organization

Organize research datasets by date:

```bash
# Preview organization
fx organize ~/Research/Data --dry-run -o ~/Research/Organized

# Execute organization
fx organize ~/Research/Data --recursive -o ~/Research/Organized
```

### Scenario 2: ML Training Data

Organize machine learning training data:

```bash
# Organize by file type
fx organize ~/ML/Data -i "*.csv" -i "*.parquet" -i "*.json" --recursive

# Use creation time
fx organize ~/ML/Data --date-source created --recursive
```

### Scenario 3: Sensor Data Management

Organize time-series sensor data:

```bash
# Organize sensor data by date
fx organize ~/Sensors --recursive --date-source modified

# Clean up empty directories
fx organize ~/Sensors --recursive --clean-empty
```

### Scenario 4: Archive Management

Organize archived datasets:

```bash
# Organize archives with custom depth
fx organize ~/Archives --depth 2 -o ~/Archives/Sorted

# Use specific patterns
fx organize ~/Archives -i "*.tar" -i "*.zip" -i "*.gz" --recursive
```

## Dataset Organization Script

```bash
#!/bin/bash
# organize_datasets.sh

set -e

DATA_DIR=$1

if [ -z "$DATA_DIR" ]; then
  echo "Usage: organize_datasets.sh DATA_DIR"
  echo "Example: organize_datasets.sh ~/Data"
  exit 1
fi

echo "=== Dataset Organization ==="
echo "Source: $DATA_DIR"
echo ""

# 1. Preview organization
echo "1. Previewing organization plan..."
fx organize "$DATA_DIR" --dry-run --recursive
echo ""

# 2. Confirm organization
read -p "Proceed with organization? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "2. Organizing datasets..."

  # Execute organization
  fx organize "$DATA_DIR" --recursive --clean-empty --yes --quiet

  echo "   Organization complete"
  echo ""
else
  echo "2. Organization cancelled"
  echo ""
  exit 0
fi

# 3. Summary
echo "3. Summary..."
OUTPUT_DIR="$DATA_DIR/organized"
echo "   Output directory: $OUTPUT_DIR"

if [ -d "$OUTPUT_DIR" ]; then
  FILE_COUNT=$(find "$OUTPUT_DIR" -type f | wc -l)
  echo "   Files organized: $FILE_COUNT"
fi

echo "=== Organization Complete ==="
```

## Advanced Dataset Management

### Organize by Data Type

```bash
# Organize CSVs
fx organize ~/Data -i "*.csv" -o ~/Data/CSV

# Organize JSON
fx organize ~/Data -i "*.json" -o ~/Data/JSON

# Organize Parquet
fx organize ~/Data -i "*.parquet" -o ~/Data/Parquet
```

### Conflict Handling

```bash
# Skip conflicting datasets
fx organize ~/Data --on-conflict skip --recursive

# Rename conflicting datasets
fx organize ~/Data --on-conflict rename --recursive

# Overwrite old datasets (use carefully)
fx organize ~/Data --on-conflict overwrite --recursive
```

### Verification

```bash
# Verify organization
echo "Organized datasets:"
find ~/Data/organized -type f -name "*.csv" | head -20

# Check for missing datasets
echo "Unorganized datasets:"
find ~/Data -maxdepth 1 -type f -name "*.csv" 2>/dev/null
```

## Related Commands

- [`fx organize`](../commands/organize.md) - Organize files by date
- [`fx filter`](../commands/filter.md) - Filter files by extension
- [`fx size`](../commands/size.md) - Analyze file sizes
