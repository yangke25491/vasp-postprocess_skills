# CHGCAR

**用途：** 电荷密度、差分电荷、ELF

## 官方文档

📖 [VASP Wiki CHGCAR](https://www.vasp.at/wiki/index.php/CHGCAR)

## 格式结构

```
  Block 1: POSCAR 格式头 (lattice, atom types, counts, coordinates)
  Block 2: NGXF  NGYF  NGZF           ← FFT 网格维度
  Block 3: ρ(r) × V_grid              ← NGXF×NGYF×NGZF 个浮点数
           按 Fortran 列优先 (NX 最快, NZ 最慢)
  Block 4: augmentation occupancies   ← 在网格数据之后！
```

**ISPIN=2 时有两组：**
```
  Block 1-4: 总电荷密度 (up + down)
  Block 5-8: 磁化密度 (up - down)，网格重复
```

## 物理量换算

```python
# 真实电荷密度 n(r) [1/Å³]:
V_cell = |a · (b × c)|   # 晶胞体积
V_grid = NGXF * NGYF * NGZF
n_r = data / (V_grid * V_cell)
# 验证：sum(n_r) × dV = sum(data) / V_grid = NELECT
```

## Fortran 列优先

`data[nx + ny*NGXF + nz*NGXF*NGYF]`，nx 变化最快。
`np.reshape(data, (NGXF, NGYF, NGZF), order='F')`

## 已知坑

- 文件可能巨大（数 GB），**不要全部读到内存**
- augmentation occupancies **始终在网格数据之后**
- 真实电荷密度需除以 `V_grid × V_cell`（两个体积，不是只除一个）
- NELECT 验证：`data.sum() / V_grid`
- 差分电荷 CHGCAR_diff 可能为负值
- 网格尺寸由 `NGXF` / `NGYF` / `NGZF` 或 PREC 决定
- Selective dynamics 会增加坐标行数
