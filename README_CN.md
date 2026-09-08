# 智能阿波 + 智能水中 Rev.A1 工程验证包

## 已锁定的首版默认值

| 项目 | 默认值 |
|---|---|
| 阿波外形 | 最大直径 32 mm，高 49 mm |
| 共用 PCB | 12 × 35 × 1.0 mm，4 层，ENIG |
| 首批数量 | 共板 10 片；装 5 套阿波、5 套智能水中 |
| 电池 | 带保护 401020 LiPo，60–80 mAh，线焊 |
| 工作/验证水深 | 10 m / 15 m 等效静水压力 |
| 智能水中量程 | 0–2 kgf 工作，独立样件验证 ≥5 kgf 生存 |
| 弹性梁 | 0.30 mm 316L，首批 10 片 |
| 打印工艺 | PA12 MJF/SLS |
| 水中负浮力 | 海水中 −2.900 g；整机空气称重目标 23.294 g |

本包面向真实水域 Rev.A1 研究，不是免审查量产文件。316L 梁独立承担钓线拉力，打印壳体只承担整流、防水与配重。

## 当前交付状态

| 文件 | 状态 |
|---|---|
| `hardware/smart_apo_common_revA1.kicad_sch` | 正式带网络原理图；42 个器件；脚位表已导出；结构解析与生成器校验通过 |
| `hardware/smart_apo_common_revA1_NETS_PLACED.kicad_pcb` | 4 层、真实焊盘/网络/器件坐标/内层平面；**尚未布线，禁止直接投板** |
| `hardware/BOM_revA1_JLCPCB.csv` | 双版本 BOM；关键 IC 已锁 LCSC 料号，通用阻容在下单时锁库存 |
| `hardware/ASSEMBLY_VARIANTS_revA1.csv` | 阿波/水中 DNP 差异表 |
| `mechanical/` | 参数化 SCAD、打印 STL、316L 梁 DXF；网格封闭性已检查 |
| `firmware/host/autotune.py` | 双端对时、张力教师标签、时序分块寻参、独立测试集评估 |
| `validation/` | 静载、密封、水槽和真实海况闭环试验方案 |

## 为什么还不能直接下 PCB 订单

当前运行环境没有 KiCad 官方布线/DRC 引擎，因此没有生成可能误导生产的 Gerber。下一步必须在 KiCad 中：逐项绑定官方封装，重点用 ST TN0018 复核 LPS28DFW；完成电源与差分桥路布线、过孔和铜皮；运行 ERC/DRC；用独立 Gerber 查看器复核后才改为 `FAB_RELEASED`。

## 推荐装配

- 阿波：STM32G031F8P6、LSM6DSO、LPS28DFW、W25Q256、红色 LED；U4/J3/R8/R9/C6/C7/C13 不贴。
- 智能水中：相同核心，加 NAU7802 与六线全桥；Q1/D1/R6/R7 不贴。
- NAU7802 的 AVDD/桥激励设为 3.0 V，REFP/REFN 接远端 S+/S−，避免线阻变化进入比例误差。
- 磁簧开关只作唤醒输入；整机依靠 MCU 深睡眠待机，不让电池主电流经过磁簧管。

## 闭环调参入口

```bash
cd firmware/host
python generate_synthetic_dataset.py
python autotune.py example_data/awa.csv example_data/underwater.csv -o example_result.json
```

候选参数只在验证段选出，并在测试段报告结果。真正升级必须再通过下一次未参与寻参的独立航次；张力证明的是“钩侧机械事件”，不能单独证明一定有鱼，因此最终真值仍建议叠加摄像或提竿结果。

## 重建机械文件

安装 `numpy trimesh shapely manifold3d mapbox_earcut` 后运行：

```bash
python tools/generate_artifacts.py
```

原理图与 PCB 草案的生成脚本分别为 `tools/generate_schematic.py` 和 `tools/generate_pcb.py`。
