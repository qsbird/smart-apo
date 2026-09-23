> 最新：Flash原厂land/paste修正已采用，官方ERC0/0、DRC普通错误0/未连接14/警告119。U3外围逃线仍开放，旧表“数字门槛关闭”不能用于整板放行。详情见 `FLASH_LAND_CHECKPOINT_20260923_CN.md` 及 `U3_ROUTING_REVIEW_20260923_CN.md`。

# Rev.A2 核心器件官方资料核对记录

> **活动目标最新桥路检查点**：ERC **0/0**；普通DRC错误 **0**，仍有 **22未连接、119警告**，一致性0，**NOT_FAB_RELEASED**。主差分输入已成对、同面、零过孔；J3物理顺序已旋转。TIM2寄存器后端模型测试通过，23项host＋2项MCU测试通过，最终ELF/板上未完成。详见 [桥路与时基检查点](ANALOG_CHECKPOINT_20260923_CN.md)。下方旧数字为历史。


核对日期：2026-09-08，补充复核 2026-09-09。此记录区分“已由官方资料确认”和“仍需 KiCad/CubeMX/实物完成”的事项。

| 器件 | 官方资料 | 已确认 | 未关闭门槛 | 2026-09-09 实现是否可行 |
|---|---|---|---|---|
| STM32G031F8P6 | [ST DS12992 Rev 4](https://www.st.com/resource/en/datasheet/stm32g031f8.pdf)、[RM0444 Rev 6](https://www.st.com/resource/en/reference_manual/rm0444-stm32g0x1-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) | TSSOP20 真实物理脚顺序已重建；PA11/PA12 经 remap 作 PA9/PA10；KiCad `TSSOP-20_4.4x6.5mm_P0.65mm` Pin 1 在封装左侧 | 本机仍无 CubeMX，不能关闭 remap/LSE/UART/I2C/SPI/启动的工具链验证 | CubeMX 项 **不可关闭**。手册级脚序 **可行且已落地**。 |
| LSM6DSOTR | [ST LSM6DSO 数据手册](https://www.st.com/resource/en/datasheet/lsm6dso.pdf) | 网表+ERC：I2C 模式 `CS` 接 3V3，`SDO/SA0` 接 GND，不悬空；INT2/OCS_AUX 为 NC。2026-09-09：已建项目封装 `SmartApoRevA2:LGA-14_2.5x3mm_P0.5mm_LSM6DSO`（DS Figure 25：2.5×3.0、节距 0.50、Pin 1 左上逆时针），原理图已改，ERC 仍为 0 | 无 STEVAL-MKI196V1 Gerber 交叉验证铜/阻焊/钢网；无 3D 模型 | **2.5×3.0 焊盘已落地，比 3.0×2.5 LSM6DS3 库封装可行。** 评估板 Gerber 交叉验证仍开放。 |
| LPS28DFWTR | DS13317 Rev 1、TN0018、STEVAL-MKI225A | 数字封装门槛已关闭 | 3D/O 形圈/壳体/首件焊接 | 数字封装 **可行且已落地**。 |
| NAU7802SGI | NAU7802 V1.7 | SOP-16；AVDD 为 power_out；KiCad `SOIC-16_3.9x9.9mm_P1.27mm` Pin 1 左侧，与手册 SOP-16 Pin 1 一致 | 320 SPS 噪声、共模、PGA、六线远端仍待电路/实物 | 封装选型 **可行**。噪声指标不能由封装复核关闭。 |
| W25Q256JVEIQ | Winbond RevR、AN0000009 Rev2.1 p21、官方FAQ | 原不匹配Microchip封装已换为项目Winbond land/paste；结构EP浮空允许，最大金属投影内无过孔；编号网络保持 | 来料/封装版本、钢网/焊接、正确3D、SI/PI和实物 | 2026-09-23数字几何修正已落地；整板仍NOT_FAB_RELEASED。见FLASH_LAND_CHECKPOINT。 |
| MCP73831T-2ACI/OT | DS20001984H | SOT-23-5 脚序与 KiCad `SOT-23-5` 一致；20 kΩ ≈ 50 mA | 必须以所购 401020 规格确认充电电流 | 50 mA 对 60–80 mAh 约 0.63–0.83 C，**像候选值，但不能代替电芯手册**。此项 **未关闭**。 |
| TPS7A0233PDBVR | TI SBVS277C | `33` 为 3.3 V 版本；EN 接 VBAT 不悬空；OUT 为 power_out；KiCad SOT-23-5 Pin 1=IN | 采购项必须是 `33` 后缀；热性能待实物 | EN 不悬空 **可行且已落地**。料号后缀仍要在下单日核对。 |

## 磁簧开关（SW1）

KiCad 库 `SW_SPST_REED_CT05-XXXX-G1` courtyard 约 11.65×4.05 mm，在 12 mm 宽板上 **放不下**（铜到板边还要 0.25 mm）。2026-09-09 已改为项目封装 `SmartApoRevA2:REED_CT05_COMPACT`（本体 5.1×1.9 mm，courtyard 6.8×2.8 mm），原理图已改、网表已导出、ERC 仍为 0。

这只解决“板子上放得下”。**所购 CT05 图纸未核对前，不能当 SMT 放行封装。**

## 本轮已落实的设计约束

- Rev.A2 项目符号库已把电源输入、稳压/充电输出、数字输入输出、双向总线和 NC 分开定义。
- LPS28DFW 与 LSM6DSO 的顶层器件投影区域内禁止走线和过孔；U3 禁布已被 DRC 抓到自动布线违例，说明约束有效，布线尚未遵守。
- LPS28DFW 周围机械压紧点和螺钉距离至少 2 mm；O 形圈只压金属压力口周边。
- WSON 中央结构焊盘若接地，不能放裸露过孔以免吸锡。
- 过孔当前脚本使用 **0.60 mm 外径 / 0.30 mm 钻孔**。0.45/0.20 与 0.45/0.30 已在官方 DRC 中失败。

## 尚未授权为生产文件

本记录不能替代 KiCad 官方 DRC、最终 Gerber 独立检查或实物验证。上述任一门槛未关闭时，Rev.A2 状态必须保持 `NOT_FAB_RELEASED`。
