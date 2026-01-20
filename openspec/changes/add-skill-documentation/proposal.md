# Proposal: Add SKILL.md Documentation

## Change ID
`add-skill-documentation`

## Status
`proposed`

## Why
其他 AI 助手（如 Claude、GPT 等）在使用 fx-bin 项目时缺乏统一的引导文档，需要一个标准化的 SKILL.md 文件来描述项目能力、使用方法和最佳实践。

## What Changes
- 新增 `SKILL.md` 文件，遵循 AI 技能文档标准格式
- 包含项目概述、可用命令、使用示例、开发指南

## Impact
- **影响的代码**: 无代码修改，仅文档
- **Breaking Change**: No
- **向后兼容**: Yes

## Risks
| Risk | Severity | Mitigation |
|------|----------|------------|
| 文档过时 | Low | 命令列表相对稳定，更新时同步更新文档 |

## Rollback Strategy
- `git revert <commit-hash>` 或直接删除 SKILL.md

## Acceptance Criteria
- [ ] SKILL.md 包含项目概述
- [ ] SKILL.md 包含所有 13 个可用命令说明
- [ ] SKILL.md 包含常用使用场景示例
- [ ] 文件可被其他 AI 正确解析和理解

## Branch
`docs/add-skill-md`
