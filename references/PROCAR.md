# PROCAR

**用途：** 能带投影（投影到原子/轨道）

## 官方文档

📖 [VASP Wiki PROCAR](https://www.vasp.at/wiki/index.php/PROCAR)

## 格式结构

```
  line 1: PROCAR lm decomposed          (LORBIT<11 时无 "lm decomposed")
  line 2: # of k-points: Nk  # of bands: Nb  # of ions: Ni
  line 3: (空行)

  --- 重复 Nk × Nb 次 ---
  k-point i : kx ky kz     weight = w
  (空行)
  band j # energy E # occ. O
  (空行)
  ion    [轨道列...]  tot
    1    投影值
    ...
    Ni   投影值
  tot    所有离子和
  (空行或下一个 band)
```

## 列数参考

| LORBIT | ISPIN | 列 (含 ion + tot) | 轨道 |
|--------|-------|-------------------|------|
| 10 | 1 | 5 | s p d tot |
| 10 | 2 | 8 | s_up s_dn p_up p_dn d_up d_dn tot |
| 11 | 1 | 11 | s py pz px dxy dyz dz2 dxz x2-y2 tot |
| 11 | 1 (有 f) | **18** | 同上 + **fy3x2 fxyz fyz2 fz3 fxz2 fzx2 fx3** tot |
| 11 | 2 | 每列×2+tot | 每轨道 up/down |

> **含 f 投影子的 PAW 数据集会产生额外的 7 个 f 轨道列。**

## 已知坑

- **列数取决于 PAW 数据集**：有 f 电子的原子额外产生 7 个 f 轨道列
- 解析维度必须用 regex，`split()` 取第二个是 "of"
- 列头行缩进不固定，需 `strip()` 后 `startswith('ion')`
- LORBIT=10 只有 s,p,d（lm 平均），无 f
- ISPIN=2 时每个 spin 有独立的一组投影
- 数据量巨大：Nk × Nb × (Ni+3) 行
