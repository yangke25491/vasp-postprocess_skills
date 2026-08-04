# EIGENVAL

**用途：** 能带结构、占据数

## 官方文档状态

**VASP Wiki 无格式说明** — 该页面上没有描述文件格式。以下内容基于 VASP 5.x 真实文件的反向工程。

## 格式结构

**VASP 5.x 格式（真实文件验证，ISPIN=1）：**

```
  line 1: NIONS  NIONS  ISPIN  ?    例: "   36   36    1    1"
  line 2: 参数行 (NELECT / 其他常数)
  line 3: 1.000000000000000E-004     (可能是 SIGMA 或 EDIFF)
  line 4: 坐标类型                   "CAR" / "SEL" / "DIR"
  line 5: 体系名称                   由 INCAR SYSTEM 定义
  line 6: NKPT_full  NKPTS_IBZ  NBANDS
  line 7: (空行)

  --- 重复 NKPTS_IBZ 次，每段 = NBANDS + 2 行 ---
  line: kx  ky  kz  weight           (科学计数法)
  NBANDS 行: iband  eigenvalue  occupation [spin_occ2]
  line: (空行，最后一个 k-point 后没有)
```

**VASP 6.x 可能不同** — 没有官方文档确认。

## 数据段验证

总行数 = 6 (头) + NKPTS × (NBANDS + 2) - 1（无尾部空行）

## 已知坑

- **VASP Wiki 无格式文档** — 不要相信任何未经验证的格式说明
- VASP 4/5 头部与 VASP 6 可能完全不同
- NKPTS = IBZ k-points（对称性约化后）
- ISPIN=2 时每行有两个占据数（第三、四列）
- NKPT（line 6 第一字段）是 full BZ k-point 数，NKPTS 才是文件中的 k-point 数
