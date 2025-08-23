# 代码质量审查报告

## 总体评价
- 稳定性: 功能与安全相关测试覆盖全面（并发/权限/性能/安全），覆盖门槛 ≥80%。
- 工程化: Poetry + Makefile + Tox + GitHub Actions 组合完善，包含分阶段 TDD 流程与报告产出。
- 安全/健壮性: 文本替换采用原子写入与备份回滚；目录遍历具备循环/权限/深度限制与异常兜底。

## 主要优点
- 测试体系: 单元/集成/性能/并发/安全用例齐备，质量门槛与运行方式清晰（`make test*`、CI 工作流）。
- 代码结构: 模块职责明确，命令式与函数式实现并行，便于逐步演进与替换。
- 工具链: flake8/black/mypy/bandit/safety 配置完善，`Makefile` 命令实用，覆盖报告与工件上传齐全。

## 待改进点
- 版本一致性: `fx_bin/__init__.py` 的 `__version__='0.7.1'` 与 `pyproject.toml` 的 `0.9.4` 不一致。
- 无效目标: `Makefile` 中 `run-server` 指向 `fx_server`（不存在脚本）。
- URL 安全: `fx_bin/pd.py` 未阻止 `file://` 与内网地址，存在 SSRF/本地文件读取风险（测试已暗示期望）。
- CLI 一致性: 混用 `print`/`click.echo`/`ClickException`；`find_files` 空关键词仍遍历并输出。
- 跨设备替换: `replace.py` 以数值 18 判定跨设备，建议使用 `errno.EXDEV`。
- 依赖声明: `pandas` 同时在可选依赖与 dev 组，建议收敛至 `extras.excel` 并完善文档。
- 符号链接: `SizeEntry.from_scandir` 未显式 `follow_symlinks=False`。
- 命名/语义: `lib.count_fullwidth` 返回 ASCII+特殊计数，与名称语义不符。
- 风格/类型: dataclass 自定义 `__slots__`；建议 `@dataclass(slots=True)`；少量函数缺少类型注解/统一 docstring。
- 历史配置: `.travis.yml` 过时，建议移除以免误导。

## 改进建议（优先级）
- 高: 统一版本来源；完善 `pd.py` URL 校验；修正 `find_files` 空参行为；`replace.py` 使用 `errno.EXDEV`。
- 中: 清理无效 `Makefile` 目标；合并 `pandas` 依赖策略；统一 CLI 输出与错误处理；`from_scandir` 禁止跟随符号链接。
- 低: 调整/重命名 `count_fullwidth`；dataclass `slots=True`；增加 pre-commit 钩子与文档补充。

## 执行清单（Checklist）
- [ ] 版本一致: 用 `importlib.metadata.version("fx-bin")` 或从 `pyproject.toml` 同步到 `fx_bin/__init__.py`。
- [ ] 移除 `.travis.yml`；修正/移除 `Makefile` 的 `run-server` 目标。
- [ ] `pd.py` URL 校验: 使用 `urllib.parse` 与 IP/域校验，拒绝 `file://`、环回/私网/云元数据地址。
- [ ] CLI 统一: 用 `click.echo(..., err=True)` 与 `click.ClickException`；仅在入口处处理 `sys.exit`；日志用 loguru。
- [ ] `find_files`: 空关键词直接返回用法提示；可增加 `--path/--hidden/--ignore`（可选）。
- [ ] 替换跨设备: `import errno` 并使用 `e.errno == errno.EXDEV` 分支处理。
- [ ] 依赖收敛: 将运行期 `pandas` 仅保留在 `extras.excel`；README/AGENTS.md 提示 `pip install fx-bin[excel]`。
- [ ] 符号链接安全: `from_scandir` 使用 `entry.is_file(..., follow_symlinks=False)`/`is_dir(..., follow_symlinks=False)`。
- [ ] 语义修正: 重命名或重写 `count_fullwidth` 并补充 docstring/测试。
- [ ] 数据类/类型: 使用 `@dataclass(slots=True)`；为公共函数补全类型注解与简短 docstring。
- [ ] 预提交: 添加 `.pre-commit-config.yaml`（black/flake8/mypy/bandit）；在 CI 中运行。
- [ ] 文档: README/AGENTS.md 补充 `excel` extra、CLI 选项与安全提示。

