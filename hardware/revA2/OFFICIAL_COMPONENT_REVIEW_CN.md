# Rev.A2 核心器件官方资料核对记录

核对日期：2026-09-08。此记录区分“已由官方资料确认”和“仍需 KiCad/CubeMX/实物完成”的事项。

| 器件 | 官方资料 | 已确认 | 未关闭门槛 |
|---|---|---|---|
| STM32G031F8P6 | [ST DS12992 Rev 4](https://www.st.com/resource/en/datasheet/stm32g031f8.pdf)、[RM0444 Rev 6](https://www.st.com/resource/en/reference_manual/rm0444-stm32g0x1-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) | TSSOP20 真实物理脚顺序已重建；PA11/PA12 物理脚分别通过 `PA11_RMP`/`PA12_RMP` 用作 PA9/PA10 | 本机未发现 CubeMX；仍需生成配置并编译验证 remap、LSE、UART、I2C、SPI 和启动状态 |
| LSM6DSOTR | [ST LSM6DSO 数据手册](https://www.st.com/resource/en/datasheet/lsm6dso.pdf) | LGA-14 2.5 x 3.0 mm；I2C 模式 CS 必须为高；SDO/SA0 不得悬空；10 脚 OCS_Aux 可不接，11 脚 SDO_Aux 可不接或接 VDDIO | 对照原厂封装图复核焊盘、Pin 1 和坐标轴；在正式 ERC 中检查 CS/SA0 状态 |
| LPS28DFWTR | [ST DS13317 Rev 1](https://www.st.com/resource/en/datasheet/lps28dfw.pdf)、[TN0018 Rev 8](https://www.st.com/resource/en/technical_note/tn0018-handling-mounting-and-soldering-guidelines-for-mems-devices-stmicroelectronics.pdf)、[STEVAL-MKI225A 官方参考板](https://www.st.com/en/evaluation-tools/steval-mki225a.html) | CCLGA-7L 2.8 x 2.8 mm；1 SDA、2 SA0、3 SCL、4 INT/DRDY、5 GND、6 VDD、7 PAD2LID；官方参考板铜/阻焊/钢网已提取并写入项目 footprint | 数字封装门槛已关闭；仍需 3D 检查压力口、O 形圈、壳体压紧和首件焊接质量 |
| NAU7802SGI | [Nuvoton NAU7802 数据手册 V1.7](https://www.nuvoton.com/resource-files/NAU7802%20Data%20Sheet%20V1.7.pdf) | SOP-16；DVDD 必须比内部 VDDA 目标高约 0.3 V；3.0 V VDDA 可驱动至少 10 mA，适合约 8.6 mA 的 350 Ω 桥 | 复核 320 SPS 下噪声、输入共模、PGA 增益和六线远端感测接法；正式 ERC 检查 AVDD power-output |
| W25Q256JVEIQ | [Winbond W25Q256JV 官方资料页](https://www.winbond.com/hq/support/documentation/?__locale=en&category=%2F.categories%2Fresources%2Fdatasheet%2F&family=%2Fproduct%2Fcode-storage-flash%2Fqspi-nor%2Findex.html&line=%2Fproduct%2Fcode-storage-flash%2Findex.html&pno=W25Q256JV) | 2.7-3.6 V，8 x 6 mm WSON-8；中央金属焊盘无内部电气连接，可悬空或接 GND且下方避免裸露过孔；Rev.A2 已增加 R12 10 kΩ `/CS` 上拉 | 下单前核对 2026-05-11 版数据手册、JVEIQ 精确封装与中央焊盘 |
| MCP73831T-2ACI/OT | [Microchip DS20001984H](https://ww1.microchip.com/downloads/en/DeviceDoc/MCP73831-Family-Data-Sheet-DS20001984H.pdf) | SOT-23-5：1 STAT、2 VSS、3 VBAT、4 VDD、5 PROG；4.7 µF VBAT 电容为推荐最小值；20 kΩ 对应约 50 mA | 必须以所购 401020 电芯规格确认允许充电电流；热分析和热调节仍需实物验证 |
| TPS7A0233PDBVR | [TI SBVS277C](https://www.ti.com/lit/ds/symlink/tps7a02.pdf) | DBV SOT-23-5：1 IN、2 GND、3 EN、4 NC、5 OUT；输入 1.5-6 V，输出要求有效电容至少 0.5 µF，推荐 1 µF | 确认采购项确为 3.3 V `33` 版本；正式 ERC 检查 EN 不悬空及 OUT power-output |

## 本轮已落实的设计约束

- Rev.A2 项目符号库已把电源输入、稳压/充电输出、数字输入输出、双向总线和 NC 分开定义。
- LPS28DFW 与 LSM6DSO 的顶层器件投影区域内禁止走线和过孔，焊盘引出必须尽量对称。
- LPS28DFW 周围机械压紧点和螺钉距离至少 2 mm；O 形圈只压金属压力口周边，不向陶瓷本体传递不均匀载荷。
- WSON 中央结构焊盘若接地，不能放裸露过孔以免吸锡。

## 尚未授权为生产文件

本记录不能替代 KiCad 官方 DRC、最终 Gerber 独立检查或实物验证。上述任一门槛未关闭时，Rev.A2 状态必须保持 `NOT_FAB_RELEASED`。
