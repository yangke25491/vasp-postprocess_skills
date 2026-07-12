# VASP Post-Process Skills

> **VASP 后处理 Agent Skill** — 为 AI 编程助手（OpenCode / Claude 等）设计的 VASP 文件后处理知识库与工作流。

## 这是什么？

本仓库包含一套完整的 VASP 后处理 **Agent Skill**，涵盖 EIGENVAL、CHGCAR、PROCAR、WAVECAR、DOSCAR 等核心 VASP 输出文件的格式文档、探测脚本和已知陷阱清单。

这套 skill 最初在 `yangke25491/vaspunfold` 项目（VASP 费米面反折叠工具）的开发过程中积累而成，所有格式信息均经过真实文件验证，而非仅依赖 VASP Wiki 的官方文档。

## 为什么需要这个 skill？

### 问题：VASP 文件格式不可靠

- **WAVECAR** 的二进制格式**从未被 VASP 官方公开**
- **EIGENVAL** 的 VASP Wiki 页面**没有格式说明**
- **DOSCAR** 的实测列数可能与 Wiki 标准不同（本项目实测 17 列 vs Wiki 标准值）
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
- 已知坑（本项目实测验证）

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

## 如何在 OpenCode 中使用

1. 将本仓库 clone 到 OpenCode 的 skills 目录：

```bash
# 放到项目的 .opencode/skills/ 下
cd your-project/
git clone https://github.com/yangke25491/vasp-postprocess_skills.git .opencode/skills/vasp-postprocess
```

2. OpenCode 会自动识别 `.opencode/skills/vasp-postprocess/SKILL.md` 中的 frontmatter 并注册 skill。

3. 当你与 AI 助手对话时提及 VASP 文件，skill 会自动触发（或询问确认后触发）。

## 如何在 Claude / 其他 AI 中使用

将 `SKILL.md` 的内容作为 system prompt 的一部分加载，或将整个仓库作为项目上下文提供给 AI。

## 验证来源

所有格式文档均经过以下真实文件验证：
- **项目**: `yangke25491/vaspunfold`（La3Ni2O7 体系）
- **WAVECAR**: 25×25×5 Gamma-centered，3.4 GB，VASP 5.x
- **EIGENVAL**: 272 k-pts, 168 bands, ISPIN=1
- **PROCAR**: 含 f 轨道列（La/Pr/Nd/Sm/Eu/Gd PAW 数据集）
- **DOSCAR**: NEDOS=3000, NIONS=36, 实测原子 DOS 17 列
- **CHGCAR**: 448×144×144 FFT 网格

## 修改日志

```
2026-07-04: initial version
  - verified EIGENVAL/CHGCAR/PROCAR/WAVECAR/DOSCAR against real files + VASP Wiki
  - structured into SKILL.md (core) + references/ (format docs) + scripts/ (templates)
  - 20 known pitfalls documented
2026-07-12: published to GitHub as vasp-postprocess_skills
  - moved from local .opencode/skills/ to standalone repository
```

## 许可

仅供课题组内部传承使用。

## 相关项目

- [`yangke25491/vaspunfold`](https://github.com/yangke25491/vaspunfold) — VASP 费米面反折叠工具，本 skill 的验证来源
