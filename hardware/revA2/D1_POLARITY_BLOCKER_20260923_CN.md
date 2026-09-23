> 数字设计内部冲突现已修复，见D1_POLARITY_FIX_20260923_CN.md。以下为发现时历史证据；所购LED验证仍开放。

# D1极性约定冲突 · 2026-09-23

状态：BLOCKED_CONFIRMED_SYMBOL_FOOTPRINT_POLARITY_CONVENTION_CONFLICT。这是数字设计内部可修复问题，不只是等待所购LED资料。当前不允许将D1方向标识用于生产装配。

实际执行`python3 validation/revA2_led_polarity/audit.py`，exit0表示审查脚本成功识别冲突，不代表电路通过。证据audit.json绑定当前板SHA256 `5d1f8a7a330c3bbbf86d8e15930d2b26694e2a207ddf2a994f410223839efa94`与官方网表哈希；installed_Device_LED_symbol.txt为本机KiCad10.0.6库的LED符号摘录。

- 当前D1使用SmartApoRevA2:PASSIVE2通用无极性符号。
- 官方网表：D1.1=/LED_A，D1.2=/LED_K；LED_A接R6，LED_K接Q1漏极。
- 本机Device:LED明确1=K、2=A；派生来源LED_SMD:LED_0805_2012Metric采用KiCad阴极为1脚约定。
- 项目LED封装沿用了标准方向轮廓/Fab及3D方向，只曾裁短板边丝印。故当前电气定义与来源库的极性含义相反；前述“保留轮廓方向”的检查只证明未改图形方向，不能证明LED极性正确。

官方约定来源：[KiCad IDF Exporter — Pin orientation and positioning](https://docs.kicad.org/5.1/en/idf_exporter/idf_exporter.html#_pin_orientation_and_positioning)。该旧版文档作为约定背景，当前实际引脚命名由本机10.0.6库摘录直接佐证。

当前ERC0/0、DRC0错误/0未连/3项courtyard不能捕捉这个通用符号造成的极性冲突，不能据此放行。尚无所购LED准确MPN，器件实体标志与光学性能也未验证。

下一步在独立副本将D1换为明确A/K语义的符号，协调引脚编号、实际焊盘网络、阴极丝印/Fab及3D方向；优先保持已有铜几何。逐项验证R6→A、K→Q1漏极的物理连接、模型/标记一致性，再重跑官方ERC/DRC与BOM检查。不得只改网名或只旋转位号掩盖问题。

本阶段未改PCB、原理图、库或固件，只新增审查脚本/证据/本报告与交接阻断入口；因此未重复运行无修改的ERC/DRC。没有Gerber或生产BOM/CPL导出，NOT_FAB_RELEASED。
