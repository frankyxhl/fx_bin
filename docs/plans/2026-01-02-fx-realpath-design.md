# fx realpath 设计文档

**日期**: 2026-01-02  
**状态**: 已确认  
**审核**: Oracle APPROVED (2026-01-02)

## 概述

添加 `fx realpath` 命令，用于获取文件或目录的绝对路径（规范化路径）。

## 需求

- 输出给定路径的绝对路径
- 路径必须存在，否则报错
- 解析符号链接到真实目标
- 支持 `~` 展开
- 纯路径输出（无前缀描述文字）

## 使用示例

```bash
# 基本用法
$ fx realpath .
/Users/frank/Projects/fx_bin

# 相对路径
$ fx realpath ../foo/bar.txt
/Users/frank/Projects/foo/bar.txt

# Home 目录展开
$ fx realpath ~/Downloads
/Users/frank/Downloads

# 路径不存在时报错
$ fx realpath not_exist.txt
Error: Path does not exist: not_exist.txt
$ echo $?
1
```

## 技术实现

### 核心函数 (`fx_bin/realpath.py`)

```python
from pathlib import Path
from typing import Optional

def resolve_path(path: str) -> Path:
    """Resolve a path to its absolute canonical form.
    
    Args:
        path: Path to resolve (can be relative, contain ~, or be a symlink)
        
    Returns:
        Absolute path with symlinks resolved
        
    Raises:
        FileNotFoundError: If path does not exist
        PermissionError: If path is not accessible
    """
    return Path(path).expanduser().resolve(strict=True)
```

### CLI 集成 (`fx_bin/cli.py`)

```python
@cli.command()
@click.argument("path", default=".")
def realpath(path):
    """Get absolute path of a file or directory.
    
    Resolves relative paths, symlinks, and ~ to the canonical absolute path.
    The path must exist.
    
    Examples:
        fx realpath .           # Current directory
        fx realpath ../foo      # Relative path
        fx realpath ~/Downloads # Home directory
    """
    from . import realpath as realpath_module
    
    try:
        resolved = realpath_module.resolve_path(path)
        click.echo(str(resolved))
        return 0
    except FileNotFoundError:
        click.echo(f"Error: Path does not exist: {path}", err=True)
        return 1
    except PermissionError:
        click.echo(f"Error: Permission denied: {path}", err=True)
        return 1
    except OSError as e:
        click.echo(f"Error: Cannot resolve path: {path} ({e})", err=True)
        return 1
```

### 命令注册

在 `COMMANDS_INFO` 中添加：
```python
("realpath", "Get absolute path of a file or directory"),
```

## 测试计划

### 单元测试 (`tests/unit/test_realpath.py`)

1. **基本功能**
   - 当前目录 `.` 解析
   - 相对路径 `../foo` 解析
   - 绝对路径直接返回
   - 默认参数 `"."` 正确处理

2. **特殊路径**
   - `~` 展开为 home 目录
   - symlink 解析到真实目标
   - 循环 symlink 抛出 OSError

3. **错误处理**
   - 路径不存在时抛出 FileNotFoundError
   - 权限不足时抛出 PermissionError
   - 其他 OSError 情况正确处理

### 集成测试 (`tests/integration/test_realpath_cli.py`)

1. CLI 正常输出测试
2. 无参数时使用当前目录
3. 错误路径退出码测试
4. 帮助信息测试
5. 命令出现在 `fx list` 中
6. 命令出现在 `fx --help` 中
7. 无效 flag 处理正确

## 文件变更清单

| 文件 | 操作 |
|------|------|
| `fx_bin/realpath.py` | 新建 |
| `fx_bin/cli.py` | 添加命令 |
| `tests/unit/test_realpath.py` | 新建 |
| `tests/integration/test_realpath_cli.py` | 新建 |

## 参考

- 现有命令: `fx root` (`fx_bin/root.py`)
- Python API: `pathlib.Path.resolve(strict=True)`
- Unix 命令: `realpath -e`
