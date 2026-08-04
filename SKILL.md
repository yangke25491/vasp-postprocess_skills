---
name: vasp-postprocess
description: >
  VASP post-processing skill for EIGENVAL, CHGCAR, PROCAR, WAVECAR, DOSCAR, etc.
  When the user mentions VASP files or post-processing, ASK for confirmation
  before using this skill — do not auto-trigger.
---

# VASP 后处理 Agent Skill

> **⚠ 手动触发模式：** 当检测到用户可能涉及 VASP 后处理时，**先询问用户是否需要使用本 skill**，获得明确同意后再加载完整内容执行。

> **重要：** 本 skill 包含核心工作流和陷阱。各文件格式的详细文档在 `references/` 目录下，
> Python 探测脚本模板在 `scripts/inspect_templates.py` 中。按需加载。

## 核心理念：先验证，后开发

**在写任何后处理代码之前，必须先确定文件的实际格式。**

VASP 的文件格式取决于 VASP 版本、编译选项、INCAR 设置、甚至计算是否做完。
同一个文件名在不同计算中可能有完全不同的结构。

### 三步验证法

1. **查 VASP Wiki** — 有文档的文件：DOSCAR, PROCAR, CHGCAR, POSCAR, CONTCAR, OUTCAR
   无文档：WAVECAR（二进制格式从未公开）、EIGENVAL（wiki 页面无格式说明）

2. **真实文件探测** — 即使 wiki 有文档，实测列数可能不同（已发现 DOSCAR 实测 17 列 vs wiki 标准）

3. **交叉验证** — 不同文件间对齐：EIGENVAL NKPTS vs WAVECAR NKPTS vs PROCAR k-point 数

### 标准编码流程

```
  1. 查 VASP Wiki 了解官方格式
  2. 出探测脚本 → 用户跑 → 贴输出
  3. 对比 wiki 和实测（有差异时相信实测）
  4. 确认格式后再写处理代码
  5. 交叉验证多文件一致性
  6. 交付代码 + 更新 skill
```

## 触发规则

出现以下任一情况即触发本 skill：
- VASP / vasp / DFT 后处理
- EIGENVAL / CHGCAR / PROCAR / WAVECAR / DOSCAR / OUTCAR
- 费米面 / 能带 / 态密度 / 电荷密度 / 谱权重
- band unfolding / 反折叠 / 后处理脚本
- 读 VASP 文件报错 / 格式不对 / 数据异常

触发后：**先不要写处理代码**，先读对应 `references/` 文件了解格式，再出探测脚本。

## 文件格式速查表

| 文件 | 参考文档 | 官方状态 | 关键注意事项 |
|------|---------|---------|-------------|
| EIGENVAL | `references/EIGENVAL.md` | ❌ 无 wiki 格式文档 | 版本差异极大，必须探测 |
| CHGCAR | `references/CHGCAR.md` | ✅ wiki 有文档 | augmentation 在数据之后 |
| PROCAR | `references/PROCAR.md` | ✅ wiki 有示例 | 含 f 轨道列（稀土元素） |
| WAVECAR | `references/WAVECAR.md` | ❌ 无格式文档 | 只能通过 vaspwfc 读取 |
| DOSCAR | `references/DOSCAR.md` | ✅ wiki 有完整格式 | 列数可能和 wiki 不同 |

脚本模板：`scripts/inspect_templates.py` 含每个文件类型的探测函数。

## 六步工作法

### 步骤 0：读参考文档 + 出探测脚本

确定文件类型后，先去 `references/` 读对应文档了解格式，然后用 `scripts/inspect_templates.py` 中的函数或按需写探测脚本。

### 步骤 1：用户反馈

用户到 HPC 上跑探测脚本，贴回输出。**这一步不能跳过。**

### 步骤 2：确认理解

对照输出确认文件结构、维度、列数。如果和预期不符，分析原因（shift？spin？VASP 版本？设备架构？）。

### 步骤 3：开发处理代码

基于确认的格式写代码。添加断言验证维度（帮助后续调试）。

### 步骤 4：交叉验证

多文件数据对齐：
- EIGENVAL NKPTS vs WAVECAR `_kvecs` 数量 vs PROCAR k-point 数量
- DOSCAR 费米能级 vs OUTCAR 的 E-fermi
- PROCAR 原子数 vs POSCAR 原子数
- CHGCAR 积分 NELECT vs INCAR 预期

### 步骤 5：交付

把探测脚本和处理代码一起交付。如发现新的版本差异，更新 `references/`。

## 已知陷阱清单

| # | 陷阱 | 文件 | 表现 | 检查方法 |
|---|------|------|------|---------|
| 1 | `_kvecs` 在 [-0.5, 0.5) | WAVECAR | `find_K_index` 找不到 K 点 | `kv.min()` 为负 |
| 2 | 对 `_kvecs` 做 `% 1.0` | WAVECAR | 匹配错乱 | 不要加任何坐标变换 |
| 3 | PROCAR `split()[1]` 是 "of" | PROCAR | int("of") 崩溃 | regex 替代 split |
| 4 | OUTCAR 可能有多个 E-fermi | OUTCAR | 取到中间步的值 | 循环取最后一个 |
| 5 | kfixed 必须对齐 WAVECAR kz 面 | 后处理 | 大量 k-point 报错 | snap 到最近 unique kz |
| 6 | vaspwfc 非线程安全 | WAVECAR | 并行读崩溃 | multiprocessing（每进程独立 wfc） |
| 7 | CHGCAR Fortran 列优先 | CHGCAR | 形状错 | `order='F'` |
| 8 | EIGENVAL NKPTS 是 IBZ | EIGENVAL | 和 WAVECAR 点数不同 | 两者可能不同 |
| 9 | DOSCAR 巨量行数 | DOSCAR | 内存溢出 | 只读头部，按需读取 |
| 10 | LORBIT=10 vs 11 列数不同 | PROCAR | 列数不对应 | 检查 LORBIT 设置 |
| 11 | CHGCAR augmentation 在数据之后 | CHGCAR | 在数据前搜不到 | 从文件尾部往前找 |
| 12 | WAVECAR 版本兼容性 | WAVECAR | vaspwfc 读不了 | 试不同版本 vaspwfc |
| 13 | kfixed 与切面对齐 | 任何 | 部分 k-point 报错 | 用 unique kz 值代替输入 |
| 14 | EIGENVAL/DOSCAR 头部版本差异 | EIGENVAL, DOSCAR | 硬编码行号错 | 打印前 7 行确认 |
| 15 | DOSCAR 列数与 wiki 不一致 | DOSCAR | 列数不是标准值 | `shape[1]` 确认 |
| 16 | CHGCAR augmentation 位置版本依赖 | CHGCAR | 列表不明 | 从尾部往前搜 3 整数行 |
| 17 | PROCAR 含 f 轨道列 | PROCAR | 假设只有 5d 列 | split 列头后数实际列数 |
| 18 | PROCAR 列头有空格前缀 | PROCAR | regex 匹配不到 | strip() 后 startswith |
| 19 | WAVECAR 无官方格式文档 | WAVECAR | 无法手动解析 | 只能用第三方库 |
| 20 | EIGENVAL 无官方格式文档 | EIGENVAL | 格式随版本变 | 写探测脚本先看前 7 行 |

## WAVECAR 配置参考

典型 Gamma-centered 网格（kz shift 示例）：

```
_kvecs range: [-0.480000, 0.480000]
Unique kx: 25 values (0, 0.04, 0.08, ...)
Unique ky: 25 values (0, 0.04, 0.08, ...)
Unique kz: 5 values (-0.35, -0.15, 0.05, 0.25, 0.45)
                             ↑ shift!
```

对应 KPOINTS：
```
Automatic generation
0
Gamma
25 25 5
0 0 1           ← kz shift (NK 单位)
```

## 维护说明

本 skill 记录常见 VASP 后处理陷阱。当遇到新问题时：

1. 先查 VASP Wiki + 参考文档
2. 再出探测脚本确认本地文件格式
3. 确认后再写处理代码
4. 踩新坑就更新 `references/` 对应文件

**修改日志：**
```
2026-07-04: initial version
  - verified EIGENVAL/CHGCAR/PROCAR/WAVECAR/DOSCAR against real files + VASP Wiki
  - structured into SKILL.md (core) + references/ (format docs) + scripts/ (templates)
YYYY-MM-DD: updated by [name]
  - what was added/changed
```
