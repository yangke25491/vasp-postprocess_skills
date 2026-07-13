# VASP Post-Process Skills

> **VASP 后处理 Agent Skill** — 为 AI 编程助手（如 OpenCode、Claude 等）设计的 VASP 文件后处理知识库与工作流。

## 这是什么？

本仓库包含一套完整的 VASP 后处理 **Agent Skill**，涵盖 EIGENVAL、CHGCAR、PROCAR、WAVECAR、DOSCAR 等核心 VASP 输出文件的格式文档、探测脚本和已知陷阱清单。

所有格式信息均经过真实文件验证，而非仅依赖 VASP Wiki 的官方文档。**但请注意，VASP 版本差异巨大，我在有限的环境下测试过，可能还有很多未覆盖的坑。欢迎提 Issue 补充。**

## 为什么需要这个 skill？

### 问题：VASP 文件格式不可靠

- **WAVECAR** 的二进制格式**从未被 VASP 官方公开**
- **EIGENVAL** 的 VASP Wiki 页面**没有格式说明**
- **DOSCAR** 的实测列数可能与 Wiki 标准不同
- **PROCAR** 的列数取决于 PAW 数据集（含 f 电子的原子额外产生 7 个 f 轨道列）
- 文件格式随 VASP 版本、编译选项、INCAR 设置变化

### 解决方案：先验证，后开发

本 skill 强制执行一套**三步验证法**：

1. **查 VASP Wiki** — 了解官方格式的基准
2. **真实文件探测** — 用探测脚本确认本地文件的实际格式
3. **交叉验证** — 多文件间数据对齐（EIGENVAL NKPTS vs WAVECAR k点数 vs PROCAR k-point 数）

## 仓库结构

```
vasp-postprocess_skills/
├── README.md                          ← 本文件
├── SKILL.md                           ← Skill 入口（触发规则 + 核心工作流）
├── references/                        ← 各文件格式详细文档
│   ├── CHGCAR.md                      ← 电荷密度格式
│   ├── DOSCAR.md                      ← 态密度格式
│   ├── EIGENVAL.md                    ← 能带格式
│   ├── PROCAR.md                      ← 轨道投影格式
│   └── WAVECAR.md                     ← 波函数格式
└── scripts/
    └── inspect_templates.py           ← VASP 文件探测脚本模板
```

## 核心文件说明

### `SKILL.md` — Skill 入口

定义了：
- **触发规则**：用户提及 VASP、EIGENVAL、CHGCAR 等关键词时自动触发
- **手动触发模式**：触发前先询问用户确认，避免误触发
- **六步工作法**：读文档 → 探测 → 确认 → 开发 → 交叉验证 → 交付
- **已知陷阱清单**：20 个已验证的 VASP 文件格式陷阱

### `references/` — 格式详细文档

每个文件一个 `.md`，包含：
- 官方文档链接与状态（有/无文档）
- 格式结构图
- 物理量换算公式
- 已知坑（实测验证，但欢迎补充）

| 文件 | 官方文档 | 关键注意事项 |
|------|---------|-------------|
| EIGENVAL | ❌ 无 wiki 格式文档 | 版本差异极大，必须探测 |
| CHGCAR | ✅ wiki 有文档 | augmentation 在数据之后 |
| PROCAR | ✅ wiki 有示例 | 含 f 轨道列（稀土元素） |
| WAVECAR | ❌ 无格式文档 | 只能通过 vaspwfc 读取 |
| DOSCAR | ✅ wiki 有完整格式 | 列数可能和 wiki 不同 |

### `scripts/inspect_templates.py` — 探测脚本模板

为每种 VASP 文件提供头部探测函数，**不读取整个文件**（避免 GB 级文件内存溢出）：

```bash
# 用法
python inspect_templates.py /path/to/EIGENVAL
python inspect_templates.py /path/to/CHGCAR
python inspect_templates.py /path/to/PROCAR
python inspect_templates.py /path/to/WAVECAR
python inspect_templates.py /path/to/DOSCAR
```

```python
# 也可以 import 使用
from inspect_templates import inspect_eigenval
inspect_eigenval('EIGENVAL')
```

## 已知陷阱速查（20 条）

| # | 陷阱 | 文件 | 检查方法 |
|---|------|------|---------|
| 1 | `_kvecs` 在 [-0.5, 0.5) | WAVECAR | `kv.min()` 为负 |
| 2 | 对 `_kvecs` 做 `% 1.0` | WAVECAR | 不要加任何坐标变换 |
| 3 | PROCAR `split()[1]` 是 "of" | PROCAR | regex 替代 split |
| 4 | OUTCAR 可能有多个 E-fermi | OUTCAR | 循环取最后一个 |
| 5 | kfixed 必须对齐 WAVECAR kz 面 | 后处理 | snap 到最近 unique kz |
| 6 | vaspwfc 非线程安全 | WAVECAR | multiprocessing（每进程独立 wfc） |
| 7 | CHGCAR Fortran 列优先 | CHGCAR | `order='F'` |
| 8 | EIGENVAL NKPTS 是 IBZ | EIGENVAL | 和 WAVECAR 点数不同 |
| 9 | DOSCAR 巨量行数 | DOSCAR | 只读头部，按需读取 |
| 10 | LORBIT=10 vs 11 列数不同 | PROCAR | 检查 LORBIT 设置 |
| 11 | CHGCAR augmentation 在数据之后 | CHGCAR | 从文件尾部往前找 |
| 12 | WAVECAR 版本兼容性 | WAVECAR | 试不同版本 vaspwfc |
| 13 | kfixed 与切面对齐 | 任何 | 用 unique kz 值代替输入 |
| 14 | EIGENVAL/DOSCAR 头部版本差异 | EIGENVAL, DOSCAR | 打印前 7 行确认 |
| 15 | DOSCAR 列数与 wiki 不一致 | DOSCAR | `shape[1]` 确认 |
| 16 | CHGCAR augmentation 位置版本依赖 | CHGCAR | 从尾部往前搜 3 整数行 |
| 17 | PROCAR 含 f 轨道列 | PROCAR | split 列头后数实际列数 |
| 18 | PROCAR 列头有空格前缀 | PROCAR | strip() 后 startswith |
| 19 | WAVECAR 无官方格式文档 | WAVECAR | 只能用第三方库 |
| 20 | EIGENVAL 无官方格式文档 | EIGENVAL | 写探测脚本先看前 7 行 |

## 如何使用

这是一个通用的 AI Agent skill，适用于任何支持自定义技能/知识库的 AI 编程助手。核心思想是：**让 AI 在回答 VASP 相关问题时，能访问到这套经过验证的格式文档和陷阱清单**，从而避免生成错误的解析代码。

具体使用方式取决于你所用的工具，以下方案均可：

### 方案一：克隆到技能目录

```bash
cd your-project/
git clone https://github.com/yangke25491/vasp-postprocess_skills.git .opencode/skills/vasp-postprocess
```

部分 AI 工具（如 OpenCode）会自动识别该目录下 `SKILL.md` 的 frontmatter 并注册为 skill，后续对话中可自动触发。

### 方案二：作为项目上下文 / System Prompt

将 `SKILL.md` 的全部内容粘贴到 AI 的 system prompt 或项目说明文件中（如 `.clinerules`、`AGENTS.md`、`CONTEXT.md` 等）。这是最通用的方式，适用于所有 AI 编程工具。

### 方案三：手动关联

如果不确定工具支持哪种方式，直接将本仓库的文档内容提供给 AI 即可——AI 能理解其中的格式定义和已知陷阱，并据此生成正确的解析代码。

> **简单来说**：选一个能让 AI 读到这些文档的方式就行。

## 验证来源

所有格式文档均经过真实 VASP 计算文件验证（VASP 5.x, ISPIN=1）：
- WAVECAR: Gamma-centered，3.4 GB
- EIGENVAL: 272 k-pts, 168 bands
- PROCAR: 含 f 轨道列（含稀土元素 PAW 数据集）
- DOSCAR: NEDOS=3000, NIONS=36
- CHGCAR: 448×144×144 FFT 网格

## 不足与贡献

- **我测试过，但肯定还有很多未覆盖的坑。**
- VASP 版本差异（4.x / 5.x / 6.x）可能导致文件格式变化
- ISPIN=2、SOC、非共线计算等情况的文件结构尚未充分验证
- **欢迎提 Issue 或 PR**，帮助完善这套后处理知识库

## 修改日志

```
2026-07-04: initial version
  - verified EIGENVAL/CHGCAR/PROCAR/WAVECAR/DOSCAR against real files + VASP Wiki
  - 20 known pitfalls documented
2026-07-12: published to GitHub
  - moved from local to standalone public repository
```

## 许可

MIT
