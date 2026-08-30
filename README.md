# VASP Post-Process Skills

<p align="center"><strong>English</strong> | <a href="README_zh.md">简体中文</a></p>

> **VASP post-processing Agent Skill** — a knowledge base and workflow for VASP file post-processing, designed for AI coding assistants.

## What is this?

This repository provides a complete VASP post-processing **Agent Skill**, covering format documentation, inspection scripts, and a list of known pitfalls for the core VASP output files: EIGENVAL, CHGCAR, PROCAR, WAVECAR, and DOSCAR.

All format details are verified against real files rather than relying solely on the VASP Wiki documentation. **Please note that VASP versions differ greatly; these have been tested in a limited environment and there may still be many uncovered pitfalls. Issue reports are welcome.**

## Why this skill?

### The problem: VASP file formats are unreliable

- **WAVECAR** — the binary format has **never been officially documented** by VASP
- **EIGENVAL** — the VASP Wiki page has **no format specification**
- **DOSCAR** — measured column counts may differ from the Wiki standard
- **PROCAR** — the column count depends on the PAW dataset (atoms with f-electrons add 7 extra f-orbital columns)
- File formats vary with VASP version, compile options, and INCAR settings

### The solution: verify first, then develop

This skill enforces a **three-step verification method**:

1. **Check the VASP Wiki** — establish the baseline from the official documentation
2. **Inspect real files** — use the inspection scripts to confirm the actual format of the local file
3. **Cross-verify** — align data across files (EIGENVAL NKPTS vs WAVECAR k-point count vs PROCAR k-point count)

## Repository structure

```
vasp-postprocess_skills/
├── README.md                          ← This file
├── README_zh.md                       ← Chinese version
├── SKILL.md                           ← Skill entry (trigger rules + core workflow)
├── references/                        ← Detailed format documentation
│   ├── CHGCAR.md                      ← Charge density format
│   ├── DOSCAR.md                      ← Density of states format
│   ├── EIGENVAL.md                    ← Band structure format
│   ├── PROCAR.md                      ← Orbital projection format
│   └── WAVECAR.md                     ← Wave function format
└── scripts/
    └── inspect_templates.py           ← VASP file inspection script templates
```

## Core files

### `SKILL.md` — Skill entry

Defines:
- **Trigger rules**: auto-triggers on keywords such as VASP, EIGENVAL, CHGCAR
- **Manual trigger mode**: asks for user confirmation before triggering, avoiding false positives
- **Six-step workflow**: read docs → inspect → confirm → develop → cross-verify → deliver
- **Known pitfalls**: 20 verified VASP file format pitfalls

### `references/` — Detailed format documentation

One `.md` file per format, covering:
- Official documentation link and status (documented / undocumented)
- Format structure diagram
- Physical quantity conversion formulas
- Known pitfalls (verified in practice, additions welcome)

| File | Official docs | Key caution |
|------|--------------|-------------|
| EIGENVAL | ❌ No wiki format docs | Version differences are huge; always inspect |
| CHGCAR | ✅ Wiki has docs | augmentation comes after the data |
| PROCAR | ✅ Wiki has examples | Contains f-orbital columns (rare-earth) |
| WAVECAR | ❌ No format docs | Only readable via vaspwfc |
| DOSCAR | ✅ Wiki has full format | Column count may differ from wiki |

### `scripts/inspect_templates.py` — Inspection script templates

Provides header-inspection functions for each VASP file type, **without reading the entire file** (avoiding memory overflow on GB-scale files):

```bash
# Usage
python inspect_templates.py /path/to/EIGENVAL
python inspect_templates.py /path/to/CHGCAR
python inspect_templates.py /path/to/PROCAR
python inspect_templates.py /path/to/WAVECAR
python inspect_templates.py /path/to/DOSCAR
```

```python
# Or import and call
from inspect_templates import inspect_eigenval
inspect_eigenval('EIGENVAL')
```

## Known pitfalls quick reference (20)

| # | Pitfall | File | Check method |
|---|---------|------|--------------|
| 1 | `_kvecs` in [-0.5, 0.5) | WAVECAR | `kv.min()` is negative |
| 2 | Do not apply `% 1.0` to `_kvecs` | WAVECAR | Do not add any coordinate transform |
| 3 | PROCAR `split()[1]` is "of" | PROCAR | use regex instead of split |
| 4 | OUTCAR may have multiple E-fermi | OUTCAR | take the last one in a loop |
| 5 | kfixed must align with WAVECAR kz plane | post-processing | snap to nearest unique kz |
| 6 | vaspwfc is not thread-safe | WAVECAR | multiprocessing (one wfc per process) |
| 7 | CHGCAR is Fortran column-major | CHGCAR | `order='F'` |
| 8 | EIGENVAL NKPTS is IBZ | EIGENVAL | differs from WAVECAR k-point count |
| 9 | DOSCAR has huge line count | DOSCAR | read header only, read on demand |
| 10 | LORBIT=10 vs 11 different column counts | PROCAR | check the LORBIT setting |
| 11 | CHGCAR augmentation after data | CHGCAR | search from the end of file |
| 12 | WAVECAR version compatibility | WAVECAR | try different vaspwfc versions |
| 13 | kfixed plane alignment | any | use unique kz values instead of input |
| 14 | EIGENVAL/DOSCAR header version differences | EIGENVAL, DOSCAR | print first 7 lines to confirm |
| 15 | DOSCAR column count differs from wiki | DOSCAR | confirm with `shape[1]` |
| 16 | CHGCAR augmentation position is version-dependent | CHGCAR | search 3-integer line from the end |
| 17 | PROCAR contains f-orbital columns | PROCAR | count actual columns after splitting header |
| 18 | PROCAR column header has leading spaces | PROCAR | strip() then startswith |
| 19 | WAVECAR has no official format docs | WAVECAR | only use third-party libraries |
| 20 | EIGENVAL has no official format docs | EIGENVAL | write an inspection script, check first 7 lines |

## How to use

This is a generic AI Agent skill applicable to any AI coding assistant that supports custom skills/knowledge bases. The core idea: **let the AI access these verified format docs and pitfall lists when answering VASP-related questions**, so it avoids generating incorrect parsing code.

Clone the repository into your project's skill directory:

```bash
cd your-project/
git clone https://github.com/yangke25491/vasp-postprocess_skills.git .opencode/skills/vasp-postprocess
```

Some AI tools (e.g., OpenCode) automatically detect the `SKILL.md` frontmatter in that directory and register it as a skill, triggering automatically in later conversations.

## Verification sources

All format documentation is verified against real VASP calculation files:
- WAVECAR: Gamma-centered, GB-scale size
- EIGENVAL: hundreds of k-points, hundreds of bands
- PROCAR: includes f-orbital columns (rare-earth PAW datasets)
- DOSCAR: configurable NEDOS, multiple atomic projections
- CHGCAR: large-scale FFT grids

## Limitations & contributions

- **Tested, but there are certainly many uncovered pitfalls.**
- VASP version differences (4.x / 5.x / 6.x) may change file formats
- ISPIN=2, SOC, and non-collinear calculation file structures are not fully verified
- **Issues and PRs are welcome** to help improve this post-processing knowledge base

## Changelog

```
2026-07-04: initial version
  - verified EIGENVAL/CHGCAR/PROCAR/WAVECAR/DOSCAR against real files + VASP Wiki
  - 20 known pitfalls documented
2026-07-12: published to GitHub
  - moved from local to standalone public repository
```

## License

MIT
