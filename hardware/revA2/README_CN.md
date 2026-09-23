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

> 验证命令更新：日常官方检查使用 `bash tools/export_fab_revA2.sh --check-only`。即使电气计数清零，也不会创建或修改制造文件；不带参数才会在电气门禁通过后进入导出。警告、制造与机械门槛仍需逐项审核。见 CHECK_ONLY_CHECKPOINT_20260923_CN.md。

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

> 最新Flash检查点（2026-09-23）：固定32轮BUSY误超时已改为5ms实时时限，host23/23、MCU8/8、20 ARM对象通过。KiCad仅检查独立副本，未采用新布线；仍14未连接/119警告，NOT_FAB_RELEASED。见 `hardware/revA2/FLASH_TIMEOUT_CHECKPOINT_20260923_CN.md`。

> 最新软件等待/LED检查点（2026-09-23）：恢复时基误失效及UART锁存重试已修复，LED寄存器驱动通过模型；MCU8/8、host23/23、20 ARM对象。真实Stop/RTC、最终ELF/实物仍未完成；PCB未改，NOT_FAB_RELEASED。见 `hardware/revA2/IDLE_LED_CHECKPOINT_20260923_CN.md`。

> 最新启动检查点（2026-09-23）：ADC100ms非阻塞保护与LSE有界启动已模型验证，MCU8/8、host23/23、20 ARM对象通过；无最终ELF/板上验证。PCB未改，仍14未连接/119警告。见 `hardware/revA2/STARTUP_TIMING_CHECKPOINT_20260923_CN.md`，软件SLEEP恢复缺陷待修复。

> 最新分压/GPIO检查点（2026-09-23）：R4/R5已改180k/60.4k，阻抗数值超限修正但精度/功耗未实测。ERC0/0；DRC普通错误0、未连接14、警告119；NOT_FAB_RELEASED。见 `hardware/revA2/DIVIDER_GPIO_CHECKPOINT_20260923_CN.md`。旧记录为历史。

> 验证更正（2026-09-23）：旧参考地脚本可能读缓存；MISO PCB组已撤回，SCK候选拒绝。当前官方ERC0/0、DRC普通错误0/未连接14/警告119，NOT_FAB_RELEASED。以 `hardware/revA2/REFERENCE_AUDIT_CORRECTION_20260923_CN.md` 为准，后续必须用显式填铜审查器。

> 最新MISO/I²C检查点（2026-09-23）：ERC0/0，DRC普通错误0、未连接13、警告115；NOT_FAB_RELEASED。详见 `hardware/revA2/SPI_I2C_CHECKPOINT_20260923_CN.md`。In1局部信号的最终回流审查仍开放；旧计数为历史记录。

> 最新逃线/ADC检查点（2026-09-23）：ERC 0/0，DRC普通错误0、未连接14、警告119；NOT_FAB_RELEASED。ADC分压源阻抗另有设计阻塞。详见 `hardware/revA2/FANOUT_ADC_CHECKPOINT_20260923_CN.md`；旧计数为历史记录。

> 最新复位/UART检查点（2026-09-23）：ERC 0/0，DRC普通错误0、未连接15、警告119；NOT_FAB_RELEASED。详见 `hardware/revA2/RESET_UART_CHECKPOINT_20260923_CN.md`。下文旧计数为历史记录。

> 最新电源/SPI 检查点（2026-09-23）：官方 ERC 0/0，DRC 普通错误 0、未连接 18、警告 119；仍 NOT_FAB_RELEASED。详见 `hardware/revA2/POWER_CHECKPOINT_20260923_CN.md`（下文旧计数为历史记录）。

# 智能阿波共板 Rev.A2 工作区

> **活动目标最新桥路检查点**：ERC **0/0**；普通DRC错误 **0**，仍有 **22未连接、119警告**，一致性0，**NOT_FAB_RELEASED**。主差分输入已成对、同面、零过孔；J3物理顺序已旋转。TIM2寄存器后端模型测试通过，23项host＋2项MCU测试通过，最终ELF/板上未完成。详见 [桥路与时基检查点](ANALOG_CHECKPOINT_20260923_CN.md)。下方旧数字为历史。


此目录是从 Rev.A1 独立建立的生产候选工作区。任何 Rev.A2 生成或审查操作都不得写入上级目录中的 `*revA1*` 文件。

## 当前状态

- Rev.A1 基线 SHA-256 已记录在 `revA1_baseline_sha256.json`。
- `smart_apo_revA2.kicad_sym` 使用逐脚电气类型，不再把核心 IC 的所有引脚定义为 Passive。
- `smart_apo_common_revA2.kicad_sch` 是独立原理图；当前先完成符号电气类型修复，电路改动需在官方 ERC 与逐脚审查后进行。
- `SmartApoRevA2.pretty` 是项目级封装库目录。
- `BOM_revA2_WORKING.csv` 与 `ASSEMBLY_VARIANTS_revA2.csv` 保留双装配版本；前者仍是工作 BOM，不是最终下单 BOM。
- `CPL_revA1_REFERENCE_ONLY.csv` 只用于查看旧布局，严禁作为 Rev.A2 贴片坐标文件。
- 上级 `hardware/smart_apo_common_revA2_NETS_PLACED.kicad_pcb` 只是参考板；本目录 `smart_apo_common_revA2.kicad_pcb` 才是从网表重建的四层候选板。
- 已使用 KiCad 10.0.6 官方 ERC：0 错误、0 警告（SW1 改紧凑封装后重跑仍通过）。
- 已使用 KiCad 10.0.6 官方 DRC：**未通过**（2026-09-09 长程 CP05：104 错误、74 未连接）。过孔 0.60/0.30 已消除钻孔过小和孔环不足。完整布线仍未关闭。
- LSM6DSO 已使用项目封装 `SmartApoRevA2:LGA-14_2.5x3mm_P0.5mm_LSM6DSO`（2.5×3.0 mm，DS Figure 25）。无评估板 Gerber 交叉验证前，封装复核不能整项关闭。
- MCU 固件骨架在 `firmware/mcu/`；无 CubeMX / `arm-none-eabi-gcc`，不能当已验证固件。
- 生产导出脚本：`tools/export_fab_revA2.sh`（DRC 非零即拒绝）。长程检查点：`LONG_RUN_CHECKPOINTS_CN.md`。
- LPS28DFW footprint 已按 ST 官方 STEVAL-MKI225A 铜层/阻焊/钢网 Gerber 重建。
- STM32G031F8P6 已按 DS12992 Rev 4 的真实 TSSOP20 物理脚顺序重建。
- W25Q256 `/CS` 已增加 R12 10 kΩ 上电上拉；`/WP`、`/HOLD` 接 3V3。
- KiCad 官方网表已导出：43 个器件、33 个已连接网络、9 个明确未连接引脚。
- 电池焊盘、7 针 Pogo、6 线桥和紧凑磁簧已在项目级 `.pretty`。

## 放行原则

只有在从原理图更新 PCB、完成布线、官方 DRC 为零错误、独立查看 Gerber/钻孔并重新导出 BOM/CPL 后，才可把状态改为 `FAB_RELEASED`。
