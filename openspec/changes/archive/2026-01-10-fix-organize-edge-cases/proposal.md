# Change: Fix Organize Edge Cases

## Why

Code review 发现 4 个 edge case 和资源泄漏问题需要修复：

1. **文件描述符泄漏**: tempfile.mkstemp() 返回的 fd 没有关闭
2. **--yes + --quiet 语义不一致**: 额外输出违反 "errors and summary only"
3. **ASK 模式 TOCTOU**: 运行时新出现的磁盘冲突没有 prompt
4. **目录创建路径语义**: 使用 target 而非 real_target 可能导致不一致

## What Changes

- **FD 泄漏修复**: 在所有 tempfile.mkstemp() 调用后添加 os.close(fd)
- **--quiet 输出修正**: --yes 分支尊重 --quiet 标志
- **loguru 配置**: 根据 --quiet/--verbose 配置 loguru level
- **ASK 模式文档**: 运行时冲突跳过并记录警告（遵守 --quiet）
- **目录创建修复**: 使用 real_target 的父目录创建路径

## Impact

- **Affected specs**: organize
- **Affected code**:
  - Modified: `fx_bin/organize_functional.py` (move_file_safe, EXDEV 处理)
  - Modified: `fx_bin/cli.py` (--yes 分支输出, loguru 配置)

## Breaking Change

No - edge case 修复和资源清理
