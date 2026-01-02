# fx realpath 设计文档

**日期**: 2026-01-02
**状态**: 已确认
**审核**: Oracle APPROVED (2026-01-02)
**工作流模式**: 协调模式 (Coordination Mode)

## 概述

添加 `fx realpath` 命令，用于获取文件或目录的绝对路径（规范化路径）。

## 工作流模式说明

本项目使用 **协调模式** (Coordination Mode) 进行开发：
- **主会话** (Sisyphus) 负责协调、派发任务、最终决策
- **实现者** (coder) 负责代码实现和测试编写
- **审核者** (oracle) 负责架构决策、计划审核、代码审核

**职责分离原则**：实现者与审核者分离，形成 checks and balances。

---

## Agent → Model 映射

| Agent | Model | 角色 |
|-------|-------|------|
| **Sisyphus (主会话)** | 主会话模型 | 协调、派发、最终决策 |
| `oracle` | `google/gemini-2.5-pro-preview` | 架构决策、计划审核、代码审核 |
| `coder` | `openai/gpt-5.2-codex-high` | 代码实现、测试编写 |

---

## 工作流表格（协调模式）

| 阶段 | Skill | Agent | Model | Context | 主会话职责 |
|------|-------|-------|-------|---------|------------|
| 1. 需求澄清 | `superpowers:brainstorming` | 主会话 | 主会话模型 | 同一上下文 | ✅ 直接与用户对话 |
| 2. 实施计划 | `superpowers:writing-plans` | `oracle` | `google/gemini-2.5-pro-preview` | 独立 | ✅ 计划已完成 |
| 3. 隔离开发 | `superpowers:using-git-worktrees` | `coder` | `openai/gpt-5.2-codex-high` | 独立 | 确认分支创建成功 |
| 4. TDD 实现 | `superpowers:test-driven-development` | `coder` | `openai/gpt-5.2-codex-high` | 独立 | 确认实现完成 |
| 5. 验证交付 | `superpowers:verification-before-completion` | `oracle` | `google/gemini-2.5-pro-preview` | 独立 | 确认审核通过，批准合并 |

---

## 职责分离流程图

```
Sisyphus (协调者)
    │
    ├─► oracle [阶段2: 计划] ──► Sisyphus 审批 (✅ 已完成)
    │
    ├─► coder  [阶段3: 分支] ──► Sisyphus 确认
    │
    ├─► coder  [阶段4: 实现] ──► Sisyphus 确认
    │
    └─► oracle [阶段5: 审核] ──► Sisyphus 最终批准
              ↑
         独立 review
        (未参与实现)
```

---

## 委托 Prompt 模板

### 阶段 3: 隔离开发（派发给 coder）

```
1. TASK: Create feature branch for fx realpath implementation
2. EXPECTED OUTCOME:
   - Create git worktree branch `feature/add-realpath-command` based on `main`
   - Verify branch exists and is clean
3. REQUIRED SKILLS: `superpowers:using-git-worktrees`
4. REQUIRED TOOLS: Bash (git commands)
5. MUST DO:
   - Run `git worktree add ../fx_bin-realpath feature/add-realpath-command main`
   - Verify worktree created successfully
   - Report back worktree path
6. MUST NOT DO:
   - Do NOT make any code changes
   - Do NOT modify existing files
7. CONTEXT:
   - Design doc: `docs/plans/2026-01-02-fx-realpath-design.md`
   - Working directory: `/Users/frank/Projects/fx_bin`
   - Target branch: `feature/add-realpath-command`
   - Agent: `coder` using `openai/gpt-5.2-codex-high`
```
1. TASK: Create feature branch for fx realpath implementation
2. EXPECTED OUTCOME:
   - Create git worktree branch `feature/add-realpath-command` based on `main`
   - Verify branch exists and is clean
3. REQUIRED SKILLS: `superpowers:using-git-worktrees`
4. REQUIRED TOOLS: Bash (git commands)
5. MUST DO:
   - Run `git worktree add ../fx_bin-realpath feature/add-realpath-command main`
   - Verify worktree created successfully
   - Report back the worktree path
6. MUST NOT DO:
   - Do NOT make any code changes
   - Do NOT modify existing files
7. CONTEXT:
   - Design doc: `docs/plans/2026-01-02-fx-realpath-design.md`
   - Working directory: `/Users/frank/Projects/fx_bin`
   - Target branch: `feature/add-realpath-command`
```

### 阶段 4: TDD 实现（派发给 coder）

```
1. TASK: Implement fx realpath command with TDD methodology
2. EXPECTED OUTCOME:
   - Unit tests for `resolve_path()` function in `tests/unit/test_realpath.py`
   - Implementation in `fx_bin/realpath.py`
   - CLI command added to `fx_bin/cli.py`
   - Integration tests in `tests/integration/test_realpath_cli.py`
   - All tests passing
3. REQUIRED SKILLS: `superpowers:test-driven-development`
4. REQUIRED TOOLS: Write (file creation), Edit (file modification), Bash (test execution)
5. MUST DO:
   - Write tests FIRST before implementation (TDD discipline)
   - Follow existing code patterns in `fx_bin/` (see `root.py` as reference)
   - Handle errors properly (FileNotFoundError, PermissionError, OSError)
   - Return proper exit codes (0 = success, 1 = error)
   - Add type annotations
   - Write comprehensive docstrings
6. MUST NOT DO:
   - Do NOT skip tests
   - Do NOT use type suppression (`as any`, `@ts-ignore`)
   - Do NOT commit changes
7. CONTEXT:
   - Design doc: `docs/plans/2026-01-02-fx-realpath-design.md`
   - Worktree path: `../fx_bin-realpath`
   - Reference implementation: `fx_bin/root.py`
   - Code style: Black 88 chars, Flake8 strict, Mypy strict
```

### 阶段 5: 验证交付（派发给 oracle）

```
1. TASK: Review and approve fx realpath implementation
2. EXPECTED OUTCOME:
   - Code review completed with findings documented
   - Implementation approved or improvement suggestions provided
3. REQUIRED SKILLS: None (review task)
4. REQUIRED TOOLS: Read (code review), LSP (diagnostics), Bash (verification)
5. MUST DO:
   - Review `fx_bin/realpath.py` for correctness and security
   - Review test coverage and edge cases
   - Check CLI integration in `fx_bin/cli.py`
   - Verify error handling follows project patterns
   - Run `make lint`, `make type-check`, `make test`
   - Document any issues found
   - Provide approval decision
6. MUST NOT DO:
   - Do NOT make code changes (only review)
   - Do NOT modify test expectations
7. CONTEXT:
    - Design doc: `docs/plans/2026-01-02-fx-realpath-design.md`
    - Worktree path: `../fx_bin-realpath`
    - Project patterns: `fx_bin/errors.py` for error hierarchy
    - Security requirements: path traversal protection, symlink handling
    - Agent: `oracle` using `google/gemini-2.5-pro-preview`
```

---

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

**注意**: 以下技术细节已通过委托模板在阶段 4（TDD 实现）中明确执行。

### 核心函数 (`fx_bin/realpath.py`)

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
