> **已按用户要求暂停（2026-09-24）**。首读 `PAUSE_CHECKPOINT_20260924_CN.md`。UART航次头正在修改，8个文件尚未构建/测试；之前34项通过不能用于当前WIP。快照/哈希见 `validation/revA2_paused_20260924/`。全部未提交工作保留，NOT_FAB_RELEASED。

> 最新host入口校验：CSV数值/时间/表头检查已接入autotune，34项回归及真实加载函数对照通过，完整SciPy管线未运行。硬件/MCU未改。见 `firmware/host/VERIFICATION_CSV_INPUT_CN.md`，NOT_FAB_RELEASED。

> 最新host修复：autotune事件评分改为一对一匹配，28项回归、4096组穷举对照和实际搜索函数合成集成通过。完整滤波/实航次/MCU因果检测仍未实现或未验证，缺SciPy，未安装依赖。见 `firmware/host/VERIFICATION_EVENT_METRICS_CN.md`。硬件/MCU生产代码未改，NOT_FAB_RELEASED。

> 最新固件修复：日志CRC失败不再覆盖调用者输出，AWA/UW生命周期回归及host23项通过，20个ARM对象验证通过；datalog_dump_next静态帧40→72字节，旧栈审计需区分源码版本。见 `firmware/mcu/VERIFICATION_LOG_READ_SAFETY_CN.md`。PCB未改，最终链接/实机与放行门槛仍开放。

> 最新同版本审查包：`validation/revA2_review_bundle/`已刷新当前原理图、正反面装配PDF及D1旋转后的不完整STEP，manifest.json绑定源/输出哈希。电气结果ERC0/0、DRC0错误/0未连/3项courtyard；采购/工艺/3D/最终链接/实机与尚未完成固件功能见 `hardware/revA2/DELIVERY_GATES_CURRENT_CN.md`。NOT_FAB_RELEASED。

> 最新原理图字段检查点（2026-09-23）：58个阻容显示字段拉开、J2扩大并同步7标签、8个符号库默认字段修正。官方ERC0/0、DRC0错误/0未连/3项courtyard，网表完全一致、PCB未改。见 `hardware/revA2/SCHEMATIC_FIELDS_CHECKPOINT_20260923_CN.md`，NOT_FAB_RELEASED。

> 最新IC图面检查点（2026-09-23）：U1至U7符号及75引脚间距扩大，69个标签/NC同步，长引脚名清晰分列；网表components/nets完全一致，PCB未改。官方ERC0/0、DRC0错误/0未连/3项courtyard。见 `hardware/revA2/SCHEMATIC_IC_CHECKPOINT_20260923_CN.md`；阻容/连接器图面仍待改善，NOT_FAB_RELEASED。

> 最新网络标签检查点（2026-09-23）：148个网络标签改为朝外对齐，锚点/网络语义不变，PCB未改。官方ERC0/0、DRC0错误/0未连/3项courtyard；IC内部引脚名及阻容字段仍待修整。见 `hardware/revA2/SCHEMATIC_LABEL_CHECKPOINT_20260923_CN.md`，NOT_FAB_RELEASED。

> 最新原理图检查点（2026-09-23）：A3纵向解决越页，Population仅隐藏显示；独立坐标/网表审查发现并清除6个连接引脚上的遗留NC叉号，保留3个有效标记。全部网络语义不变，官方ERC0/0、DRC0错误/0未连/3项courtyard，PCB未改；内部标签拥挤仍待修整。见 `hardware/revA2/SCHEMATIC_PAGE_CHECKPOINT_20260923_CN.md`，NOT_FAB_RELEASED。

> 最新D1极性修复（2026-09-23）：正式采用明确A/K符号及K1封装，1=K/LED_K、2=A/LED_A；封装/模型/端标转180°且原物理铜连接保持。官方ERC0/0、DRC0错误/0未连/3项courtyard，17项工具测试通过。设计内部冲突已关闭，所购器件/整页原理图/旧3D更新仍开放。见 `hardware/revA2/D1_POLARITY_FIX_20260923_CN.md`，NOT_FAB_RELEASED。

> 新确认的D1极性阻断（2026-09-23）：D1以PASSIVE2符号定义1=LED_A/2=LED_K，与派生KiCad LED封装1=K/2=A约定相反；ERC/DRC未捕获。必须先修正明确A/K符号、焊盘编号/网络及方向标识，不能仅等待采购资料。见 `hardware/revA2/D1_POLARITY_BLOCKER_20260923_CN.md`。PCB尚未修改，NOT_FAB_RELEASED。

> 最新BOM一致性检查（2026-09-23）：修正C7=100n、C11/C12实际0402和完整封装ID；43位号/变体数量检查通过，15项工具测试通过。U5目录编号冲突及准确MPN/有效容量仍开放，不是生产BOM放行。PCB未改，ERC0/0、DRC0错误/0未连/3警告。见 `hardware/revA2/BOM_CONSISTENCY_CHECKPOINT_20260923_CN.md`。

> 最新交付证据审查（2026-09-23）：当前板STEP已重新导出但模型不完整；AWA/UW最终链接实测均失败（缺lld/ARM运行库），20对象编译不等于最终固件。PCB未改，ERC0/0、DRC0错误/0未连/3警告仍适用于同一哈希。见 `hardware/revA2/CURRENT_DELIVERY_AUDIT_20260923_CN.md`，NOT_FAB_RELEASED。

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

> LDO审查更正（2026-09-23）：C3=100n、C10=1µF；main与MOSI try6的U7→C10显式F路径均1.43635mm，不能以C3移动推定近端输出电容消失。C10具体MLCC/有效容量和实测仍开放。见hardware/revA2/LDO_CAPACITOR_REVIEW_CN.md。正式板未改，仍MOSI1未连接/107警告。

> 最新位号检查点（2026-09-23）：仅修正U3/J3可见丝印Reference字段，铜/器件位置/规则未变；官方ERC0/0、普通DRC错误0/1MOSI未连接/107警告、一致性0，无忽略/排除，NOT_FAB_RELEASED。见 `hardware/revA2/REFERENCE_TEXT_CHECKPOINT_20260923_CN.md`。MOSI候选仍独立迭代。

> 官方检查命令已增加 `--check-only`（5项编排测试+实际KiCad验证通过）；后续用它复检，即使0错误/0未连接也不创建制造文件。正式板本轮未改，仍1 MOSI开路/110警告。见hardware/revA2/CHECK_ONLY_CHECKPOINT_20260923_CN.md。

> 最新IMU完整连接（2026-09-23）：经两组几何合并与独立复核已采用；官方ERC0/0、普通DRC错误0/仅MOSI 1未连接/110警告、一致性0，无忽略/排除，NOT_FAB_RELEASED。最大U2本体理想via余量.10mm；局部供电参考缺口有明确处置、严格标记仍false。见 `hardware/revA2/IMU_CONNECTED_CHECKPOINT_20260923_CN.md`。以下候选未采用/计数为历史。

> IMU候选续进展（2026-09-23）：独立完整扇出重建已0普通错误但仍未接MCU，最大本体理想余量仅0.03mm；完整连接尝试有6普通错误及新增供电开路，拒绝。正式板未变，仍0普通错误/2未连接/111警告。见hardware/revA2/IMU_ROUTING_CHECKPOINT_20260923_CN.md。

> 最新DRC可见性检查点（2026-09-23）：五类原忽略检查已启用，无ignored_checks/单项排除；修正一处地线端点，并将工程状态长说明保留到Dwgs.User。官方ERC0/0、普通DRC错误0/2未连接/111警告、一致性0，NOT_FAB_RELEASED。3个连接区courtyard缺失现在明确可见，仍开放。见 `hardware/revA2/DRC_VISIBILITY_CHECKPOINT_20260923_CN.md`。以下为历史。

> 最新LED制造修复（2026-09-23）：LED阴极孔已移出焊盘，审查中元件焊接焊盘内中心为0，剩2处Pogo接触孔待资料；官方ERC0/0、DRC普通错误0/2未连接/122警告、一致性0，NOT_FAB_RELEASED。见 `hardware/revA2/LED_VIA_MANUFACTURING_CHECKPOINT_20260923_CN.md`。以下计数为历史。

> 最新SCL制造修复（2026-09-23）：ADC与MCU两端SCL孔已移出焊盘，焊盘内中心5→3（剩D1.2及J2.7/J2.5）。官方ERC0/0、DRC普通错误0/2未连接/122警告、一致性0；NOT_FAB_RELEASED。IMU候选失败未采用。见 `hardware/revA2/SCL_VIA_MANUFACTURING_CHECKPOINT_20260923_CN.md`。以下数字为历史。

> 最新R5制造修复（2026-09-23）：原审批路径已恢复可用，R5焊盘内孔修复stage3已采用；焊盘内中心6→5。主板官方ERC0/0、DRC普通错误0/2未连接/122警告、一致性0，NOT_FAB_RELEASED。见 `hardware/revA2/R5_MANUFACTURING_CHECKPOINT_20260923_CN.md`。下方审批失败和未采用记录为历史。

> 最新固件资源检查点（2026-09-23）：不依赖KiCad的ARM资源审查已完成，20对象编译通过，静态RAM714/705字节、已知栈路径616字节；非最终链接/全栈通过。见firmware/mcu/VERIFICATION_STACK_RESOURCES_CN.md。PCB未改，R5候选仍未采用，KiCad审批额度阻塞未解除。

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

# 智能阿波 + 智能水中项目交接上下文

> **活动目标最新进展**：先读 `hardware/revA2/ANALOG_CHECKPOINT_20260923_CN.md`。主板普通DRC错误0/警告119/未连接22，ERC0/0、一致性0；输入两路原始线各2.670mm、滤波主线各2.615mm，同面零过孔。J3旋转后接线见专用接口文档。23项host＋2项MCU测试与20个ARM对象构建通过；无最终ELF/板上验证。TIM2已实现并模型验证；工具链安装授权仍待答复。证据在 `validation/revA2_analog/`，目标保持active。


> **活动目标最新状态**：先读 `hardware/revA2/GOAL_CHECKPOINT_20260923_CN.md`。本轮主板0普通DRC错误/111警告/25未连接，ERC0/0，一致性0；LSE同面无过孔。23项host/native及1项runtime测试通过，真实ARM目标文件可编译但无最终ELF/HAL/板上验证。ARM工具链安装授权待答复；继续PCB工作。证据/回退在 `validation/revA2_goal/`。目标保持active，未完成，不要重置或重新生成整板。


> **最新续开发检查点**：先读 `hardware/revA2/CONTINUATION_20260923_CN.md`。ERC 0/0，普通DRC错误0、未连接40、警告108、一致性0，仍NOT_FAB_RELEASED。U2窄逃线规则已通过几何/官方正反例审查；固件17项native测试通过但ARM/HAL/板上未完成。证据与完整回退快照在 `validation/revA2_continue/`；下方旧数字为历史。


> **最新检查点 2026-09-23**：请先读 `hardware/revA2/DEVELOPMENT_20260923_CN.md` 和 `firmware/mcu/VERIFICATION_20260923_CN.md`。官方 ERC 0/0，DRC 12 错误/108 警告/59 未连接，短路0、原理图一致性0，仍 NOT_FAB_RELEASED。Rev.A1 哈希及所有焊盘网络保留；仍在 cursor，未提交。U2 旧几何方向错误已纠正，MCU 脚表以 Rev.A2 PIN_REVIEW 为准（下文 Rev.A1 表为历史，不可直接用于固件）。15项native回归通过，ARM/板上未验证。禁止重新生成或自动布线覆盖本轮PCB；回退证据在 `validation/revA2_20260923/`。


> 目标放置目录：本仓库根目录。
>
> 下一智能体开始工作前，必须先完整阅读本文件、`README_CN.md`、`hardware/PCB_RELEASE_CHECKLIST_CN.md` 和 `validation/revA1_validation_report.json`。不要把当前PCB误认为可直接投板版本。

## 1. 项目目标

设计一套面向真实海钓环境的双端研究系统：

- **智能阿波**：通过IMU、压力信号检测鱼讯，并以快速闪光提示，不需要无线实时通信。
- **智能水中**：安装在子线/鱼钩附近，通过316L弹性梁和应变桥直接记录钩侧张力，作为原型研究阶段的“教师传感器”。
- 两端独立记录原始数据，回收后自动对时；水中张力生成教师标签，自动优化阿波侧检测参数。
- 目标是可靠区分海浪/流致扰动与钩侧机械事件。必须注意：张力事件不等价于“鱼咬钩”，最终语义真值仍需摄像、提竿或捕获结果辅助。

## 2. 用户背景与协作方式

- 用户不了解嵌入式开发和PCB设计，需要按操作顺序解释，避免只给行业术语。
- 用户倾向直接使用定制PCB、SMT和3D打印在真实环境研究，不再做面包板级原型。
- 可以积极完成数字工程设计，但必须明确区分：数字检查通过、官方KiCad ERC/DRC通过、实物验证通过。
- 不得声称未经KiCad官方引擎验证的Gerber可以生产。

## 3. 已锁定的默认参数

| 项目 | 默认值 |
|---|---|
| 阿波外形 | 最大直径32 mm，高49 mm |
| 共用PCB | 12 × 35 × 1.0 mm，4层，ENIG |
| 首批数量 | PCB共10片；装5套阿波、5套智能水中 |
| 电池 | 带保护401020 LiPo，60–80 mAh，线焊 |
| 工作水深 | 10 m |
| 密封验证 | 15 m等效静水压力 |
| 水中张力量程 | 0–2 kgf工作 |
| 梁生存目标 | 独立样件验证≥5 kgf；未试验前不得作为额定载荷 |
| 弹性梁 | 0.30 mm 316L，首批10片 |
| 打印工艺 | PA12 MJF/SLS |
| 水中负浮力 | 海水中−2.900 g |
| 水中空气称重目标 | 23.294 g（按海水密度1.025 g/mL） |

## 4. 核心电气方案

### 4.1 共用核心板

- MCU：STM32G031F8P6，LCSC `C529334`。
- IMU：LSM6DSOTR，LCSC `C2655100`。
- 压力：LPS28DFWTR，LCSC `C3263277`。
- Flash：W25Q256JVEIQ，LCSC `C97522`；备选`C5334276`必须复核封装。
- 充电：MCP73831T-2ACI/OT，LCSC `C424093`。
- LDO：TPS7A0233PDBVR，LCSC `C2887324`。
- 低漂移时基：32.768 kHz晶振，接PC14/PC15。
- 磁簧开关只作唤醒输入，不能承载电池主电流。

此前曾考虑STM32U031F8P6，后因采购可用性和成熟度改为STM32G031F8P6。后续不要无理由改回U031。

### 4.2 智能水中专用

- 应变ADC：NAU7802SGI，LCSC `C5180029`。
- 采样上限：320 SPS。
- DVDD为3.3 V；内部LDO/AVDD及桥激励暂定3.0 V，确保DVDD高于AVDD约0.3 V。
- 350 Ω全桥，预计激励电流约8.6 mA。
- 六线桥接口：`E+ / E- / S+ / S- / A+ / A-`。
- NAU7802 `REFP/REFN`接远端`S+/S-`，以补偿细线激励压降。
- 差分输入：`A+ / A-`经R8/R9进入`VIN1P/VIN1N`。

### 4.3 阿波专用

- 红色高亮LED及MOSFET驱动。
- 水中版本不贴Q1、D1、R6、R7。
- 阿波版本不贴U4、J3、R8、R9、C6、C7、C13。

完整DNP规则见`hardware/ASSEMBLY_VARIANTS_revA1.csv`。

## 5. MCU引脚映射

| TSSOP20引脚 | MCU引脚/功能 | 网络 |
|---:|---|---|
| 1 | PB7 | I2C_SDA |
| 2 | VDD/VDDA | 3V3 |
| 3 | PA1/ADC | VBAT_SENSE |
| 4 | PF2/NRST | NRST |
| 5 | PB6 | I2C_SCL |
| 6 | PA13 | SWDIO |
| 7 | PA5 | SPI_SCK |
| 8 | PA6 | SPI_MISO |
| 9 | PA7 | SPI_MOSI |
| 10 | PB0 | LED_GATE |
| 11 | PA3 | UART_RX |
| 12 | PA14 | SWCLK |
| 13 | VSS/VSSA | GND |
| 14 | PA4 | FLASH_CS |
| 15 | PC14 | LSE_IN |
| 16 | PC15 | LSE_OUT |
| 17 | PA9 | REED_WAKE |
| 18 | PA10 | STRAIN_DRDY |
| 19 | PA0 | IMU_INT |
| 20 | PA2 | UART_TX |

正式放行前必须用最新STM32G031F8P6数据手册/CubeMX再次验证复用功能。

## 6. 现有文件与状态

### 6.1 原理图

文件：`hardware/smart_apo_common_revA1.kicad_sch`

- KiCad 9格式，可由KiCad 10打开并转换。
- 42个器件，11个嵌入式自定义符号定义。
- 生成器结构校验无报错，`kiutils`可解析。
- 引脚网络清单：`hardware/pin_net_review_revA1.csv`。
- 生成脚本：`tools/generate_schematic.py`。

**重要限制：**当前自定义符号的引脚主要定义为`Passive`，因此“结构校验通过”不代表正式ERC有充分覆盖。下一版本必须用原厂/正式符号重建，或逐脚设置正确电气类型后再运行ERC。

### 6.2 PCB

文件：`hardware/smart_apo_common_revA1_NETS_PLACED.kicad_pcb`

- 12 × 35 × 1.0 mm，4层。
- 42个封装。
- 35个网络（包含空网络）。
- 2个内层平面定义。
- 走线数量为0。
- `kiutils`可解析。
- 状态明确为：`BLOCKED_NO_ROUTING_NO_OFFICIAL_DRC_NO_GERBER`。
- 生成脚本：`tools/generate_pcb.py`。

**不要直接在该文件上投板。**建议把它作为布局参考；正式符号/封装完成后，从审核后的原理图重新更新/建立PCB。

### 6.3 LPS28DFW封装

这是当前最高优先级风险。

- 当前U3封装只是工程暂定封装。
- 当前近似焊盘：外围6个约0.45 × 0.55 mm，中央7号约0.65 × 0.65 mm。
- 必须从ST产品页面获得原厂EDA模型，并对照最新数据手册及TN0018复核：焊盘编号、铜焊盘、阻焊、钢网、Pin 1、中央PAD2LID、Courtyard、压力孔和机械禁布区。
- 当前7号PAD2LID接GND；ST允许金属盖按应用接地或悬空，因此该选择还需结合盐水环境、EMC和密封结构确认。
- U3上方压力孔必须无遮挡，O形圈不得堵孔或把压紧力传给陶瓷底座。
- 传感器下方避免过孔和不对称铜结构，远离螺钉、板弯曲区和梁固定点。

参考：

- ST LPS28DFW产品页：<https://www.st.com/en/mems-and-sensors/lps28dfw.html>
- ST TN0018：<https://www.st.com/resource/en/technical_note/tn0018-handling-mounting-and-soldering-guidelines-for-mems-devices-stmicroelectronics.pdf>

### 6.4 BOM/CPL

- BOM：`hardware/BOM_revA1_JLCPCB.csv`。
- 双版本装配：`hardware/ASSEMBLY_VARIANTS_revA1.csv`。
- 当前布局坐标：`hardware/CPL_revA1.csv`。

当前CPL只能用于审查，最终布局改变后必须从正式KiCad PCB重新导出。BOM中已锁7个核心LCSC料号；通用阻容、LED、MOSFET、晶振、磁簧管需在下单当天锁定实际可贴料号。

### 6.5 机械文件

- 参数源：`mechanical/smart_apo_revA.scad`。
- 阿波：主体、上盖、电子仓托架STL。
- 水中：两半壳、配重盒STL。
- 弹性梁：`mechanical/316L_flexure_0p30mm_revA.dxf`。
- 梁预览STL标明`NOT_FOR_PRINTING`，真正梁必须316L加工。
- 所有STL经处理后的封闭网格检查通过。
- 弹性梁规范：`mechanical/316L_FLEXURE_SPEC_CN.md`。
- 打印装配说明：`mechanical/PRINT_AND_ASSEMBLY_CN.md`。

注意：当前3D模型是工程验证几何，不是已经完成公差、O形圈压缩率和15 m压力验证的生产壳体。

### 6.6 自动调参工具

- 协议：`firmware/DATA_AND_AUTOTUNE_PROTOCOL_CN.md`。
- 主程序：`firmware/host/autotune.py`。
- 合成数据生成：`firmware/host/generate_synthetic_dataset.py`。
- 使用说明：`firmware/host/README_CN.md`。
- 合成数据结果：`firmware/host/example_result.json`。

当前链路包括：

1. 两端起始/结束三次敲击检测。
2. 线性拟合时间偏移和时钟漂移。
3. 水中张力高通+MAD阈值生成教师事件。
4. 阿波加速度、角速度、压力变化率生成特征。
5. 按连续时间60%/20%/20%切分训练/验证/测试，禁止随机打散相邻窗口。
6. 网格搜索权重、阈值和最短持续时间。
7. 报告事件级F1、精确率、召回率和每小时误报数。

合成双端日志的对时RMS残差约0.27 ms，烟雾测试通过。当前工具只产生候选参数，刻意不做自动刷机。参数必须在下一次完全未参与寻参的独立航次继续优于旧参数，才允许升级，否则回滚。

## 7. 已完成验证

验证文件：`validation/revA1_validation_report.json`

- 原理图解析：PASS。
- PCB解析：PASS。
- 机械STL封闭性：PASS。
- 自动调参合成数据烟雾测试：PASS。
- 总结状态：`PASS_WITH_FABRICATION_GATES`。

仍未通过/未执行：

- 原厂封装逐项验证。
- 正式原理图ERC。
- PCB布线。
- KiCad官方DRC及原理图一致性检查。
- Gerber/钻孔/CPL独立查看。
- 电池实物尺寸与保护板确认。
- 15 m等效压力试验。
- 316L梁0–2 kgf标定和≥5 kgf生存试验。

## 8. 下一智能体优先任务

当前长程进度写在 `hardware/revA2/LONG_RUN_CHECKPOINTS_CN.md`。Rev.A2 工作区是 `hardware/revA2/`，不要覆盖 `*revA1*`。

阶段A 数字门槛大部分已关闭：独立原理图/符号/封装库、STM32 TSSOP20 物理脚、LPS28DFW 官方封装、LSM6DSO 2.5×3.0 项目封装、ERC 0/0。仍开放：CubeMX、所购 CT05 图纸、401020 电芯手册。

阶段B：用 `tools/generate_pcb_revA2.py` + `tools/route_explicit_revA2.py`。不要再跑 `tools/route_pcb_revA2.py`（迷宫已暂缓）。官方 DRC 仍未清零，不能勾布线完成。

阶段C：`tools/export_fab_revA2.sh` 在 DRC 有错误或未连接时拒绝导出。未独立查看 Gerber 前不得写 `FAB_RELEASED`。

固件骨架在 `firmware/mcu/`。无 CubeMX、无 `arm-none-eabi-gcc` 时不要假装已编译通过。

1. 不直接修改Rev.A1，建立`revA2`工作副本。 **已完成。**
2. 获取并核对所有核心器件最新原厂数据手册。 **进行中**（CubeMX/电芯/磁簧图纸仍缺）。
3. 用正式符号重建原理图，设置正确电气引脚类型。
4. 逐脚复核STM32G031、LSM6DSO、LPS28DFW、NAU7802、W25Q256、MCP73831和TPS7A02。
5. 建立项目级`.kicad_sym`与`.pretty`库。
6. 从ST原厂CAD/数据手册重建LPS28DFW封装，并按TN0018添加禁布约束。
7. 复核其余封装、Pin 1和采购封装后，运行正式ERC。
8. 从审核后的原理图重新建立PCB；旧PCB仅作布局参考。

### 阶段B：四层布局布线

推荐层叠：

| 层 | 用途 |
|---|---|
| F.Cu | 器件及主要信号 |
| In1.Cu | 连续GND |
| In2.Cu | 3V3/VBAT电源 |
| B.Cu | 低速信号/少量器件 |

推荐初始规则：普通信号0.15 mm，电源0.25–0.35 mm，间距0.15 mm，过孔 **0.60/0.30 mm**（0.45/0.20 与 0.45/0.30 已在本机 DRC 中失败），铜到板边≥0.25 mm。最终以实际板厂能力为准。网格迷宫自动布线已按 5 轮规则暂缓，见 `hardware/revA2/LONG_RUN_CHECKPOINTS_CN.md`。

布线顺序：

1. J3—R8/R9—NAU7802桥路差分输入。
2. 六线桥的Sense/Reference和Excitation。
3. LSE晶振。
4. 电源和去耦。
5. SPI Flash。
6. I²C。
7. SWD/UART/中断/LED/磁簧等低速信号。
8. GND平面、3V3/VBAT平面和地过孔。

桥路输入要求短、并行、基本等长，尽量无过孔，保持连续地参考，远离SPI时钟、LED和充电回路。晶振短、对称、无过孔。

### 阶段C：生产输出

1. 使用KiCad官方引擎运行ERC和DRC。
2. DRC要求短路、未连接、间距、线宽、板框错误均为0。
3. 使用3D Viewer检查外形、压力口、Pogo、电池和壳体干涉。
4. 导出F/B及两内层铜、F/B阻焊、F/B丝印、Edge.Cuts和钻孔文件。
5. 用Gerber Viewer独立复核。
6. 最终PCB重新导出BOM和CPL。
7. 同一PCB建立阿波、水中两套SMT装配订单，严格执行DNP表。

## 9. 当前环境限制

此前生成Rev.A1的执行环境没有KiCad/OpenSCAD命令行程序，所以：

- KiCad文件通过Python生成并用`kiutils`解析。
- 机械STL通过Python几何工具生成和检查。
- 没有官方KiCad ERC/DRC报告。
- 没有完成走线。
- 没有Gerber。

如果下一智能体所在环境有`kicad-cli`，应优先使用官方引擎，不应继续只靠文本生成器模拟DRC。可检查：

```bash
kicad-cli version
kicad-cli sch erc --help
kicad-cli pcb drc --help
```

## 10. 当前重建与检查命令

在项目根目录执行。Python依赖包括`numpy scipy trimesh shapely manifold3d mapbox_earcut kicad-sch-api kiutils`。

```bash
python tools/generate_artifacts.py
python tools/generate_schematic.py
python tools/generate_pcb.py

python firmware/host/generate_synthetic_dataset.py
python firmware/host/autotune.py \
  firmware/host/example_data/awa.csv \
  firmware/host/example_data/underwater.csv \
  -o firmware/host/example_result.json

python tools/validate_revA1.py
```

不要在改过电气设计后盲目运行旧生成脚本覆盖正式手工审核结果；进入Rev.A2后，应把生成器同步升级或将其标记为Rev.A1归档工具。

## 11. 实物阶段不可由智能体替代的工作

- 316L材料、厚度、毛刺、平面度和加工质量确认。
- 应变片粘贴、固化、防水涂覆和绝缘检查。
- 真实0–2 kgf多循环标定、回差和温漂测量。
- 独立样件≥5 kgf生存/破坏试验。
- 电池尺寸、保护电路、充电温升和密封状态检查。
- 15 m等效压力测试。
- 盐水浸泡、腐蚀和湿式触点检查。
- SMT首件焊点、器件方向和必要的X-ray/AOI确认。

## 12. 下一智能体可直接采用的任务描述

> 请先完整阅读`CONTEXT_HANDOFF.md`及其中指定文件。基于现有Rev.A1建立独立Rev.A2生产候选版本，不覆盖Rev.A1。先对照最新原厂资料重建具有正确电气引脚类型的正式原理图和项目封装库，重点按ST LPS28DFW原厂CAD、数据手册及TN0018重建U3封装。随后完成12 × 35 × 1.0 mm四层共用PCB的低噪声布局布线，保留阿波/水中两个装配变体。必须使用KiCad官方ERC/DRC验证后才能生成Gerber、钻孔和最终BOM/CPL。任何无法完成的官方工具验证或实物验证均需明确标记为阻断项，不得推定通过。
