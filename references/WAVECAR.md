# WAVECAR

**用途：** 平面波系数、波函数、反折叠

## 官方文档状态

📖 [VASP Wiki WAVECAR](https://www.vasp.at/wiki/index.php/WAVECAR)
VASP Wiki 仅说明 "The WAVECAR file is a binary file"，**二进制格式从未公开过**。
所有解析工具（vaspwfc, pyprocar, VaspBandUnfolding）都是反向工程的。

## 唯一可靠读取方式

```python
from vaspwfc import vaspwfc
wfc = vaspwfc('WAVECAR')
kv = wfc._kvecs          # (NKPTS, 3), [-0.5, 0.5)
nbands = wfc._nbands
encut = wfc._encut
```

## 关键属性

| 属性 | 说明 |
|------|------|
| `wfc._kvecs` | k-point 坐标 (NKPTS, 3)，范围 **[-0.5, 0.5)** |
| `wfc._nbands` | 能带数 |
| `wfc._encut` | 截断能 |
| `wfc._efermi` | 费米能级（并非所有版本都存在） |
| `wfc._gamma` | Gamma-point only 标志 |
| `wfc._lsorbit` | 是否 SOC |
| `wfc._ispin` | 1 或 2 |

## 坐标惯例（经本项目反复验证）

- `_kvecs` 在 **[-0.5, 0.5)**，不是 [0, 1)
- Gamma-centered NK 奇数：k = (i-1)/NK → 映射到 [-0.5, 0.5) 时 k>=0.5 减 1
- 有 shift 时：k += shift/NK（本项目中 kz shift = 0.05）
- `find_K_from_k` 输出也在 [-0.5, 0.5)，可直接比较

## 已知坑

- **二进制格式从未被 VASP 官方文档化**
- vaspwfc **不是线程安全的**，`ThreadPoolExecutor` 不可用
- `_kvecs` 是 private API，版本间可能改名
- **绝对不要对 `_kvecs` 做 `% 1.0`**：它已经在 [-0.5, 0.5)
- 降级方案：`NK = int(round(NKPTS^(1/3)))`
- 文件通常很大（本项目 3.4 GB），处理时有内存压力