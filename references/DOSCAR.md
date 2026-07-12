# DOSCAR

**用途：** 态密度（总 DOS + 原子投影 DOS）

## 官方文档

📖 [VASP Wiki DOSCAR](https://www.vasp.at/wiki/index.php/DOSCAR)

## 格式结构

**头部 5 行（官方定义）：**

```
  line 1: NIONS  NIONS  0/1  NCDIJ
          (0=无 partial DOS, 1=有. NCDIJ=1/2 for ISPIN=1/2)
  line 2: Volume[Å³]  a[m] b[m] c[m]  POTIM[s]
  line 3: TEBEG[K]
  line 4: 'CAR'
  line 5: SYSTEM name
  line 6: E_max  E_min  NEDOS  E_fermi  1.0000
```

**总 DOS（NEDOS 行）：**

```
  ISPIN=1: energy  DOS  integrated_DOS               (3 列)
  ISPIN=2: energy  DOS_up  DOS_dwn  int_up  int_dwn  (5 列)
```

**原子投影 DOS（如果 LORBIT>=10，每个离子一个块）：**
每个块以格式行（同 line 6）开始，后跟 NEDOS 行：

| LORBIT | ISPIN | 数据列 (不含 energy) | 轨道 |
|--------|-------|---------------------|------|
| 10 | 1 | 3 | s, p, d |
| 10 | 2 | 6 | s_up s_dn p_up p_dn d_up d_dn |
| 11 | 1 | 9 | s, py, pz, px, dxy, dyz, dz2, dxz, x2-y2 |
| 11 | 2 | 18 | 每轨道×2 + (tot_up + tot_dn)? |

## 文件结构验证

本项目 VASP 5.x DOSCAR（NEDOS=3000, NIONS=36, ISPIN=1）：
- 总 DOS 列：3 (energy, DOS, integrated)
- 原子 DOS 列：**17** (1 energy + 16 data)
- 总行数：3000 + 36×(1+3000) + 6(头) = 111042 ✓
- 注：16 数据列与官方 LORBIT=10(3) 和 LORBIT=11(9) 的标准列数都不匹配

## 已知坑

- 头部行数可能因版本变化
- 总 DOS 是否有积分列 → 用 `shape[1]` 确认
- **原子 DOS 列数必须用探测脚本确认**（本项目实测 16 列，和 wiki 不同）
- NEDOS 默认为 301，由 INCAR 设置
- 费米能级在格式行第 4 字段（应与 OUTCAR 一致）
- NSW>1 时有多个时间步
- 无 LORBIT 时只有总 DOS