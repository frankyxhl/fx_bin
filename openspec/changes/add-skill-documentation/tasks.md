# Tasks: Add SKILL.md Documentation

## Phase 1: 创建 SKILL.md 文档

**目标**: 在新分支上创建完整的 AI 技能文档

| # | Task | Type | Definition of Done |
|---|------|------|-------------------|
| 1.1 | ✅ 创建分支 `docs/add-skill-md` | Setup | 分支创建成功，已切换到新分支 |
| 1.2 | ✅ 创建 SKILL.md 文件 | Green | 文件包含：项目概述、安装说明、13个命令详情、使用场景、开发指南 |
| 1.3 | ✅ Commit 更改 | - | commit message 符合 conventional commits 规范 |
| 1.4 | ✅ Push 到远程 | - | 分支已推送到 origin |
| 1.5 | ✅ 创建 Pull Request | - | PR 创建成功，包含完整描述 |

---

## SKILL.md 内容规范

文件应包含以下章节：

1. **Project Overview** - 项目简介、包名、仓库地址、Python 版本要求
2. **Installation** - pip/pipx/源码安装方式
3. **Available Commands** - 13 个命令的表格概览
4. **Command Details** - 每个命令的详细说明和示例
5. **Common Use Cases** - 至少 4 个使用场景
6. **Development Commands** - 开发者命令（测试、lint、格式化）
7. **Architecture Notes** - 架构说明
8. **Key Files** - 关键文件位置
9. **Getting Help** - 帮助命令
10. **Documentation** - 文档链接

---

## 验收检查清单

- [x] 所有 13 个命令都有文档（实际 14 个）
- [x] 每个命令都有至少一个示例
- [x] 使用场景覆盖常见工作流（6 个场景）
- [x] 文档格式清晰，易于 AI 解析
- [x] PR 已创建并可供审查 (PR #41)
