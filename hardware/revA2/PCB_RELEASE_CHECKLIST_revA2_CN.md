> 最新同版本审查包：`validation/revA2_review_bundle/`已刷新当前原理图、正反面装配PDF及D1旋转后的不完整STEP，manifest.json绑定源/输出哈希。电气结果ERC0/0、DRC0错误/0未连/3项courtyard；采购/工艺/3D/最终链接/实机与尚未完成固件功能见 `hardware/revA2/DELIVERY_GATES_CURRENT_CN.md`。NOT_FAB_RELEASED。

> 最新原理图字段检查点（2026-09-23）：58个阻容显示字段拉开、J2扩大并同步7标签、8个符号库默认字段修正。官方ERC0/0、DRC0错误/0未连/3项courtyard，网表完全一致、PCB未改。见 `hardware/revA2/SCHEMATIC_FIELDS_CHECKPOINT_20260923_CN.md`，NOT_FAB_RELEASED。

> 最新IC图面检查点（2026-09-23）：U1至U7符号及75引脚间距扩大，69个标签/NC同步，长引脚名清晰分列；网表components/nets完全一致，PCB未改。官方ERC0/0、DRC0错误/0未连/3项courtyard。见 `hardware/revA2/SCHEMATIC_IC_CHECKPOINT_20260923_CN.md`；阻容/连接器图面仍待改善，NOT_FAB_RELEASED。

> 最新网络标签检查点（2026-09-23）：148个网络标签改为朝外对齐，锚点/网络语义不变，PCB未改。官方ERC0/0、DRC0错误/0未连/3项courtyard；IC内部引脚名及阻容字段仍待修整。见 `hardware/revA2/SCHEMATIC_LABEL_CHECKPOINT_20260923_CN.md`，NOT_FAB_RELEASED。

> 最新原理图检查点（2026-09-23）：A3纵向解决越页，Population仅隐藏显示；独立坐标/网表审查发现并清除6个连接引脚上的遗留NC叉号，保留3个有效标记。全部网络语义不变，官方ERC0/0、DRC0错误/0未连/3项courtyard，PCB未改；内部标签拥挤仍待修整。见 `hardware/revA2/SCHEMATIC_PAGE_CHECKPOINT_20260923_CN.md`，NOT_FAB_RELEASED。

> 最新D1极性修复（2026-09-23）：正式采用明确A/K符号及K1封装，1=K/LED_K、2=A/LED_A；封装/模型/端标转180°且原物理铜连接保持。官方ERC0/0、DRC0错误/0未连/3项courtyard，17项工具测试通过。设计内部冲突已关闭，所购器件/整页原理图/旧3D更新仍开放。见 `hardware/revA2/D1_POLARITY_FIX_20260923_CN.md`，NOT_FAB_RELEASED。

> 新确认的D1极性阻断（2026-09-23）：D1以PASSIVE2符号定义1=LED_A/2=LED_K，与派生KiCad LED封装1=K/2=A约定相反；ERC/DRC未捕获。必须先修正明确A/K符号、焊盘编号/网络及方向标识，不能仅等待采购资料。见 `hardware/revA2/D1_POLARITY_BLOCKER_20260923_CN.md`。PCB尚未修改，NOT_FAB_RELEASED。

> 最新BOM一致性检查（2026-09-23）：修正C7=100n、C11/C12实际0402和完整封装ID；43位号/变体数量检查通过，15项工具测试通过。U5目录编号冲突及准确MPN/有效容量仍开放，不是生产BOM放行。PCB未改，ERC0/0、DRC0错误/0未连/3警告。见 `hardware/revA2/BOM_CONSISTENCY_CHECKPOINT_20260923_CN.md`。

> 最新1脚标记检查点（2026-09-23）：U1/U5方向三角形仅平移并保持形状/指向，项目库同步；5→3警告，全部丝印DRC清零。官方ERC0/0、DRC0错误/0未连/0一致性问题，剩J1/J2/J3 missing_courtyard开放；NOT_FAB_RELEASED。见 `hardware/revA2/PIN1_SILK_CHECKPOINT_20260923_CN.md`。以下较大计数为历史。

> 最新连接区丝印检查点（2026-09-23）：J2/J3轮廓与库同步修复，9→5警告，无新增项。官方ERC0/0、DRC0错误/0未连/0一致性问题，NOT_FAB_RELEASED。见 `hardware/revA2/CONNECTOR_SILK_CHECKPOINT_20260923_CN.md`。剩2项方向标记压铜和3项courtyard，以下较大计数为历史。

> 最新上部位号检查点（2026-09-23）：U1/U7位号回到各自本体，六个拥挤丝印位号不印刷并保留原位Fab装配标识；36→9警告，无新增项。官方ERC0/0、DRC0错误/0未连/0一致性问题，NOT_FAB_RELEASED。见 `hardware/revA2/UPPER_LABEL_CHECKPOINT_20260923_CN.md`。以下较大警告数为历史。

> 最新被动元件位号检查点（2026-09-23）：R8/C5/C3/C8/R10可见位号调整，50→36警告，无新增项。官方ERC0/0、DRC0错误/0未连/0一致性问题，NOT_FAB_RELEASED。见 `hardware/revA2/PASSIVE_LABEL_CHECKPOINT_20260923_CN.md`。以下较大警告数为历史。

> 最新装配位号检查点（2026-09-23）：补齐6个项目封装Fab标识，43个封装各有一个原位Fab位号并导出正反面审查PDF；仅新增非制造层文字。官方ERC0/0、DRC0错误/0未连/50警告，项目库一致，NOT_FAB_RELEASED。见 `hardware/revA2/ASSEMBLY_LABEL_CHECKPOINT_20260923_CN.md`。完整装配/极性/工艺验证仍开放。

> 最新MCU标识处置（2026-09-23）：五个拥挤丝印位号不印刷，保留原位F.Fab并输出核对装配图，R4移到邻近空白区；70→50警告，无新增项。官方ERC0/0、DRC0错误/0未连/0一致性问题，NOT_FAB_RELEASED。见 `hardware/revA2/MCU_LABEL_CHECKPOINT_20260923_CN.md`。完整装配图仍为交付门槛，下方较大警告数为历史。

> 最新充电区丝印检查点（2026-09-23）：U6/R3/C11位号调整，75→70警告，无新增项。官方ERC0/0、DRC0错误/0未连/0一致性问题，NOT_FAB_RELEASED。见 `hardware/revA2/CHARGER_LABEL_CHECKPOINT_20260923_CN.md`。下方较大警告数为历史。

> 最新J1丝印检查点（2026-09-23）：J1丝印与项目库同步，79→75警告，板边丝印类别清零，无新增项。官方ERC0/0、DRC0错误/0未连/0一致性问题，NOT_FAB_RELEASED。见 `hardware/revA2/J1_SILK_CHECKPOINT_20260923_CN.md`。以下较大警告数为历史。

> 最新D1丝印检查点（2026-09-23）：D1位号及两段板边轮廓调整，项目专用封装同步原理图，82→79警告，无新增项。官方ERC0/0、DRC0错误/0未连/0一致性问题；NOT_FAB_RELEASED。见 `hardware/revA2/BOTTOM_SILK_CHECKPOINT_20260923_CN.md`。D1所购器件极性仍须核验，下方较大警告数为历史。

> 最新字高检查点（2026-09-23）：U2/SW1/J2位号字高修复，89→82警告，text_height类别清零，无新增项。官方ERC0/0、DRC0错误/0未连/0一致性问题，NOT_FAB_RELEASED。见 `hardware/revA2/TEXT_HEIGHT_CHECKPOINT_20260923_CN.md`。下方较大警告数为历史。

> 最新板边位号检查点（2026-09-23）：U4/C6/C16/R6仅Reference字段调整，95→89警告，无新增项；官方ERC0/0、DRC0错误/0未连/0一致性问题，NOT_FAB_RELEASED。见 `hardware/revA2/EDGE_LABEL_CHECKPOINT_20260923_CN.md`。下方警告数为历史。

> 最新U3/C13检查点（2026-09-23）：C13可见位号修复消除10项警告；U3及配套库按最大本体重建禁布，最小理想via余量.10mm/顶部.125mm。官方ERC0/0、DRC普通错误0/未连接0/95警告、一致性0，无忽略/排除，NOT_FAB_RELEASED。见 `hardware/revA2/U3_MARGIN_AND_C13_CHECKPOINT_20260923_CN.md`。以下较小余量和警告数均为历史。

> 最新整板电气闭合（2026-09-23）：MOSI最终候选已独立复检并采用。官方ERC0/0、DRC普通错误0/未连接0/105警告、一致性0，无忽略/排除；NOT_FAB_RELEASED。仅检查模式exit0且fab_export不存在。见 `hardware/revA2/MOSI_CONNECTED_CHECKPOINT_20260923_CN.md`。还须警告、制造公差/采购资料、当前3D及固件/实物门槛；下方未连接数字均为历史。

> 最新位号检查点（2026-09-23）：仅修正U3/J3可见丝印Reference字段，铜/器件位置/规则未变；官方ERC0/0、普通DRC错误0/1MOSI未连接/107警告、一致性0，无忽略/排除，NOT_FAB_RELEASED。见 `hardware/revA2/REFERENCE_TEXT_CHECKPOINT_20260923_CN.md`。MOSI候选仍独立迭代。

> 后续复检使用 `bash tools/export_fab_revA2.sh --check-only`，避免最后开路清零时自动进入制造导出。无参导出行为保留，只有其余放行审查完成后使用。见CHECK_ONLY_CHECKPOINT_20260923_CN.md。

> 最新IMU完整连接（2026-09-23）：经两组几何合并与独立复核已采用；官方ERC0/0、普通DRC错误0/仅MOSI 1未连接/110警告、一致性0，无忽略/排除，NOT_FAB_RELEASED。最大U2本体理想via余量.10mm；局部供电参考缺口有明确处置、严格标记仍false。见 `hardware/revA2/IMU_CONNECTED_CHECKPOINT_20260923_CN.md`。以下候选未采用/计数为历史。

> 最新DRC可见性检查点（2026-09-23）：五类原忽略检查已启用，无ignored_checks/单项排除；修正一处地线端点，并将工程状态长说明保留到Dwgs.User。官方ERC0/0、普通DRC错误0/2未连接/111警告、一致性0，NOT_FAB_RELEASED。3个连接区courtyard缺失现在明确可见，仍开放。见 `hardware/revA2/DRC_VISIBILITY_CHECKPOINT_20260923_CN.md`。以下为历史。

> 最新LED制造修复（2026-09-23）：LED阴极孔已移出焊盘，审查中元件焊接焊盘内中心为0，剩2处Pogo接触孔待资料；官方ERC0/0、DRC普通错误0/2未连接/122警告、一致性0，NOT_FAB_RELEASED。见 `hardware/revA2/LED_VIA_MANUFACTURING_CHECKPOINT_20260923_CN.md`。以下计数为历史。

> 最新SCL制造修复（2026-09-23）：ADC与MCU两端SCL孔已移出焊盘，焊盘内中心5→3（剩D1.2及J2.7/J2.5）。官方ERC0/0、DRC普通错误0/2未连接/122警告、一致性0；NOT_FAB_RELEASED。IMU候选失败未采用。见 `hardware/revA2/SCL_VIA_MANUFACTURING_CHECKPOINT_20260923_CN.md`。以下数字为历史。

> 最新R5制造修复（2026-09-23）：原审批路径已恢复可用，R5焊盘内孔修复stage3已采用；焊盘内中心6→5。主板官方ERC0/0、DRC普通错误0/2未连接/122警告、一致性0，NOT_FAB_RELEASED。见 `hardware/revA2/R5_MANUFACTURING_CHECKPOINT_20260923_CN.md`。下方审批失败和未采用记录为历史。

> 当前制造审查补充（2026-09-23）：正式板未变，仍2未连接/122警告、NOT_FAB_RELEASED。新增全板via/焊盘审查发现4处元件焊盘内孔与2处Pogo接触孔。R5候选尚未采用，最后修改/复检因自动审批额度不足未执行；MOSI试验拒绝。见 `hardware/revA2/VIA_PAD_CHECKPOINT_20260923_CN.md`。

> 当前ADC SDA检查点（2026-09-23）：I²C两条总线已全部接通；官方ERC0/0、DRC普通错误0/未连接2/警告122、一致性0；NOT_FAB_RELEASED。见 `hardware/revA2/ADC_SDA_CHECKPOINT_20260923_CN.md`。剩IMU_INT/MOSI；官方STEP为不完整模型审查件，未通过3D干涉。以下为历史。

> 当前I²C主干检查点（2026-09-23）：SCL全部接通，上部SDA接入MCU；官方ERC0/0、DRC普通错误0/未连接3/警告122、一致性0；NOT_FAB_RELEASED。见 `hardware/revA2/I2C_JOIN_CHECKPOINT_20260923_CN.md`。余下ADC SDA/IMU_INT/MOSI；局部反焊盘及装配余量仍有明确审查边界。以下为历史。

> 当前ADC SCL检查点（2026-09-23）：MCU/上拉至ADC的SCL已连通，相关REED支路完整。官方ERC0/0、DRC普通错误0/未连接5/警告120、一致性0；NOT_FAB_RELEASED。见 `hardware/revA2/ADC_SCL_CHECKPOINT_20260923_CN.md`。显式填铜增量参考及独立连通审查通过，非EM/实物通过；以下数字为历史。

> 当前上部I²C检查点（2026-09-23）：U2/U3 SDA/SCL已连接，C2同面供电路径缩短。官方ERC0/0、DRC普通错误0/未连接6/警告120、一致性0；NOT_FAB_RELEASED。见 `hardware/revA2/UPPER_I2C_CHECKPOINT_20260923_CN.md`。7个供电过孔边缘参考点单独处置，非EM通过；以下计数为历史。

> 当前 U3 检查点（2026-09-23）：找回哈希匹配的原厂Gerber，按实际中央接地和外围逃线路径建立窄通道，电源/地缺口关闭。官方ERC0/0、DRC普通错误0/未连接8/警告119、一致性0；NOT_FAB_RELEASED。见 `hardware/revA2/U3_ESCAPE_CHECKPOINT_20260923_CN.md`。以下数字为历史。

> 当前 MISO 检查点（2026-09-23）：SCK与MISO已分组采用，官方ERC0/0、DRC普通错误0/未连接12/警告119、一致性0；NOT_FAB_RELEASED。见 `hardware/revA2/MISO_CHECKPOINT_20260923_CN.md`。In1新填铜几何通过，换层回流/SI仍开放；以下旧计数为历史。

> 当前 SCK 检查点（2026-09-23）：已采用独立验证的 B/In2/F 布线，In1 保持地。官方 ERC0/0、DRC 普通错误0/未连接13/警告120、一致性0；NOT_FAB_RELEASED。详见 `hardware/revA2/SCK_CHECKPOINT_20260923_CN.md`。以下旧检查点数字均为历史。

> 最新Flash封装检查点（2026-09-23）：误用Microchip焊盘已按Winbond原著land/paste替换，编号网络保持，错误3D移除。官方ERC0/0、DRC普通错误0/未连接14/警告119；NOT_FAB_RELEASED。见 `hardware/revA2/FLASH_LAND_CHECKPOINT_20260923_CN.md`；局部供电过孔参考缺口有独立处置，不等于EM验证。

> 最新启动检查点（2026-09-23）：ADC100ms非阻塞保护与LSE有界启动已模型验证，MCU8/8、host23/23、20 ARM对象通过；无最终ELF/板上验证。PCB未改，仍14未连接/119警告。见 `hardware/revA2/STARTUP_TIMING_CHECKPOINT_20260923_CN.md`，软件SLEEP恢复缺陷待修复。

> 最新分压/GPIO检查点（2026-09-23）：R4/R5已改180k/60.4k，阻抗数值超限修正但精度/功耗未实测。ERC0/0；DRC普通错误0、未连接14、警告119；NOT_FAB_RELEASED。见 `hardware/revA2/DIVIDER_GPIO_CHECKPOINT_20260923_CN.md`。旧记录为历史。

> 验证更正（2026-09-23）：旧参考地脚本可能读缓存；MISO PCB组已撤回，SCK候选拒绝。当前官方ERC0/0、DRC普通错误0/未连接14/警告119，NOT_FAB_RELEASED。以 `hardware/revA2/REFERENCE_AUDIT_CORRECTION_20260923_CN.md` 为准，后续必须用显式填铜审查器。

> 最新MISO/I²C检查点（2026-09-23）：ERC0/0，DRC普通错误0、未连接13、警告115；NOT_FAB_RELEASED。详见 `hardware/revA2/SPI_I2C_CHECKPOINT_20260923_CN.md`。In1局部信号的最终回流审查仍开放；旧计数为历史记录。

> 最新逃线/ADC检查点（2026-09-23）：ERC 0/0，DRC普通错误0、未连接14、警告119；NOT_FAB_RELEASED。ADC分压源阻抗另有设计阻塞。详见 `hardware/revA2/FANOUT_ADC_CHECKPOINT_20260923_CN.md`；旧计数为历史记录。

> 最新复位/UART检查点（2026-09-23）：ERC 0/0，DRC普通错误0、未连接15、警告119；NOT_FAB_RELEASED。详见 `hardware/revA2/RESET_UART_CHECKPOINT_20260923_CN.md`。下文旧计数为历史记录。

> 最新电源/SPI 检查点（2026-09-23）：官方 ERC 0/0，DRC 普通错误 0、未连接 18、警告 119；仍 NOT_FAB_RELEASED。详见 `hardware/revA2/POWER_CHECKPOINT_20260923_CN.md`（下文旧计数为历史记录）。

# Rev.A2 PCB 放行状态

> **活动目标最新桥路检查点**：ERC **0/0**；普通DRC错误 **0**，仍有 **22未连接、119警告**，一致性0，**NOT_FAB_RELEASED**。主差分输入已成对、同面、零过孔；J3物理顺序已旋转。TIM2寄存器后端模型测试通过，23项host＋2项MCU测试通过，最终ELF/板上未完成。详见 [桥路与时基检查点](ANALOG_CHECKPOINT_20260923_CN.md)。下方旧数字为历史。


更新时间：2026-09-09。未勾选项均为阻断项；全部完成前不得生成生产 Gerber。

## 已完成的数字工程准备

- [x] Rev.A1 文件 SHA-256 基线已锁定，Rev.A2 使用独立目录与文件名。
- [x] 建立项目级 `smart_apo_revA2.kicad_sym`、`sym-lib-table`、`SmartApoRevA2.pretty` 和 `fp-lib-table`。
- [x] 核心符号的引脚不再全部使用 Passive；已区分电源输入/输出、数字输入/输出、双向、三态和 NC。
- [x] 阿波/智能水中两套装配变体表已复制为 Rev.A2 工作文件。
- [x] 已记录七个核心器件的官方资料核对入口与当前结论。
- [x] 离线结构检查通过，且复核确认 Rev.A1 哈希未变化。

## 原理图与封装阻断项

- [ ] 用当前 STM32CubeMX 验证 STM32G031F8P6 TSSOP20 的所有小封装引脚复用/重映射及启动状态。2026-09-09 复查：本机仍未安装 CubeMX，此项不能关闭。
- [x] 按 ST DS12992 Rev 4 重建 STM32G031F8P6 TSSOP20 真实物理脚顺序，并按 RM0444 记录 PA9/PA10 remap 要求。
- [x] 使用 ST 官方 STEVAL-MKI225A Gerber 与 DS13317 Rev 1 重建 LPS28DFW footprint；已核对铜、阻焊、钢网、Pin 1、PAD2LID，并加入顶层走线/过孔/铜皮禁布区。
- [ ] 完成其余核心器件的原厂封装/Pin 1/采购后缀复核。2026-09-09：LSM6DSO 已改为项目级 2.5×3.0 LGA-14（见 `LSM6DSO_FOOTPRINT_SOURCE_CN.md`），电气 CS/SA0 仍正确，ERC 0/0。磁簧仍缺所购 CT05 图纸，充电电流仍缺 401020 手册，故本项不能整项打勾。详见 `OFFICIAL_COMPONENT_REVIEW_CN.md`。
- [x] W25Q256 `/CS` 增加 R12 10 kΩ 上电上拉。
- [ ] 按实际 401020 电芯规格确认 MCP73831 约 50 mA 充电电流。没有所购电芯手册前不能关闭；50 mA 对 60–80 mAh 约合 0.63–0.83 C，只是候选值。
- [x] 使用 KiCad 10.0.6 官方 ERC；错误为 0，警告为 0。SW1 改为紧凑封装后已重跑，仍为 0。

## PCB、制造与实物阻断项

- [x] 从通过 ERC 的 Rev.A2 原理图新建 12 x 35 x 1.0 mm 四层 PCB；文件为 `smart_apo_common_revA2.kicad_pcb`。Rev.A1 PCB 及上级目录中早期 `smart_apo_common_revA2_NETS_PLACED.kicad_pcb` 均仅作布局参考。
- [ ] 完成差分桥路、LSE、电源去耦、SPI、I2C、低速信号及平面/地过孔的**可过 DRC**完整布线。
- [ ] 使用 KiCad 官方 DRC，短路、未连接、间距、线宽和板框错误为零。
- [ ] 3D Viewer 检查压力口、Pogo、电池、O 形圈和壳体干涉。
- [ ] 导出并独立查看 Gerber、钻孔；从最终 PCB 重新导出 BOM/CPL。
- [ ] 完成 15 m 等效压力、电池、盐水、梁标定和 >=5 kgf 生存等实物验证。

## 阻塞项消除检查（2026-09-09 长程）

迷宫自动布线已按 ≥5 轮失败规则**暂缓**。改用 `tools/route_explicit_revA2.py`（过孔 0.60/0.30、避开 U2/U3 顶层禁布）。

| 原计划 | 最新官方 DRC | 实现是否可行 |
|---|---|---|
| 过孔 0.60/0.30 | `drill_out_of_range` 与 `annular_width` 均为 **0** | **可行且已落地** |
| U3/U2 顶层禁布 | `items_not_allowed` **0**（收紧焊盘清除后） | **约束可行**；部分网络因此改未连接 |
| 可过 DRC 完整布线 | 错误 **104**，未连接 **74**，短路 **24** | **未关闭**。在已布线板上挪封装会使焊盘压到旧铜，已撤回 |
| 0402/器件 courtyard | 重叠 **10** | **部分改善**（挪了 U2/U7/R1/R2 等） |

官方 DRC 总计：错误 380 → **104**，未连接 **74**。**不能**把布线或 DRC 勾成完成。

Gerber/钻孔/CPL：`tools/export_fab_revA2.sh` 在 DRC 非零时拒绝导出。当前结论：`NOT_FAB_RELEASED`。

长程检查点：`LONG_RUN_CHECKPOINTS_CN.md`。


- [ ] 关闭全板via与SMT焊盘/Pogo接触孔制造审查：当前4处元件焊盘内孔、2处接触孔，另10对铜环近焊盘需核阻焊/装配；无填孔盖孔或接触工艺证据不得推定通过。见VIA_PAD_CHECKPOINT_20260923_CN.md。


- [ ] 明确U7近端C10的实际MLCC料号及3.3V/温度/容差下有效容量，满足TI TPS7A02有效Cout至少0.5µF要求，并验证启动/负载瞬态；C3是100n，不能误当唯一LDO输出电容。见LDO_CAPACITOR_REVIEW_CN.md。


- [ ] U3按最大2.95×2.95×2.1mm及实际贴装/钻孔公差检查，不能只用名义2.8mm投影；顶部via理想余量0.025mm需进一步布局或工艺依据。见LPS28DFW_FOOTPRINT_SOURCE_CN.md更新。
