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

# Rev.A2 五小时长程任务检查点

> **活动目标最新桥路检查点**：ERC **0/0**；普通DRC错误 **0**，仍有 **22未连接、119警告**，一致性0，**NOT_FAB_RELEASED**。主差分输入已成对、同面、零过孔；J3物理顺序已旋转。TIM2寄存器后端模型测试通过，23项host＋2项MCU测试通过，最终ELF/板上未完成。详见 [桥路与时基检查点](ANALOG_CHECKPOINT_20260923_CN.md)。下方旧数字为历史。


开始时间：2026-09-09 00:20（UTC+8）。计划时长 5 小时，约每 20 分钟一条检查点。
目标：四层布局布线、MCU 固件骨架、可放行 Gerber / 钻孔 / 最终 CPL。
规则：同一问题连续尝试 ≥5 轮仍失败则**暂缓并标注**，改做其他工作。官方 DRC 未清零前不得把状态写成 `FAB_RELEASED`，也不得把失败 DRC 的 Gerber 当生产文件。

## 总安排（按文档阶段）

| 时段 | 对应文档 | 工作 |
|---|---|---|
| 0:00–1:20 | 阶段A 剩余门槛 | LSM6DSO 2.5×3.0 封装、原理图/网表/ERC、过孔规则 0.60/0.30 |
| 1:20–3:00 | 阶段B | 按布线顺序做**可过 DRC** 的显式布线；禁止再加密迷宫自动布线 |
| 3:00–4:20 | 固件 | STM32G031 引脚、remap、LSE 降级、采样/记录骨架 |
| 4:20–5:00 | 阶段C | DRC 门控的 Gerber/钻孔/CPL 导出流程；3D/实物项若仍缺条件则标注暂缓 |

## 已暂缓（≥5 轮或环境不可关闭）

| 项 | 原因 | 轮次 |
|---|---|---|
| 网格/迷宫自动布线当生产实现 | 多轮后短路变多、未连接未清、U3 禁布被穿过。2026-09-09 官方 DRC 380 错 / 73 未连接 | 历史 ≥5 轮，**本长程不再重跑迷宫** |
| STM32CubeMX 关闭 remap/启动验证 | 本机未安装 CubeMX | 环境阻断，暂缓 |
| 401020 充电电流关门 | 没有所购电芯手册 | 缺资料，暂缓 |
| 所购 CT05 磁簧图纸关门 | 紧凑封装只解决“板内放得下” | 缺采购图，暂缓 |
| 15 m 压力/盐水/梁标定等实物 | 无样机 | 暂缓 |
| Rev.A2 3D 干涉 | 无 LSM6DSO STEP，壳体仍是 Rev.A1 SCAD | 暂缓，见 `3D_CHECK_PARKED_CN.md` |
| 可放行 Gerber 本身 | 依赖官方 DRC=0 | 布线未过前禁止导出生产文件 |
| 无间隙强制边沿走线 | 一次试验把官方 DRC 从 84 推到 328（短路 68、禁布 12） | 第 5 轮脚本布线策略，**已撤回并暂缓** |
| 脚本自动达到 DRC=0 | 迷宫、纯曼哈顿、A*、密过孔、强制铜皮均未清零 | **暂缓**；后续改单网手工或交互布线 |
| 已布线板上直接挪封装 | courtyard 10→6，但错误 108→175 | **已撤回并暂缓** |

## 检查点日志

### CP00 · 2026-09-09 00:20 · 启动

- **完成**：建立本日志与长程顺序；确认迷宫布线按 5 轮规则暂缓。
- **进行中**：LSM6DSO 2.5×3.0 封装（DS Figure 25：L=2.50、W=3.00、焊盘 0.475×0.25、节距 0.50）；随后改原理图并重跑 ERC。
- **卡点**：KiCad 10 安装里没有 `LGA-14_2.5x3mm`；旧板仍是 3.0×2.5 LSM6DS3 焊盘。
- **尝试**：按 DS 外形把 LayoutBorder3x4y（短边 3 焊盘、长边 4 焊盘）做到 2.5×3.0 本体上，并加顶层禁布。
- **已解决**：无（本条为启动记录）。

### CP01 · 2026-09-09 00:40 · 封装与 ERC

- **完成**：按 DS Figure 25 建立 `SmartApoRevA2:LGA-14_2.5x3mm_P0.5mm_LSM6DSO`（2.5×3.0、节距 0.50、Pin 1 左上逆时针、顶层禁布）；原理图 U2 已改；官方 ERC **0 错误 0 警告**；网表 43 器件。迷宫布线脚本标注暂缓。
- **卡点**：KiCad 10 无现成 2.5×3 LGA 库封装；无 STEVAL-MKI196V1 Gerber 交叉验证。
- **尝试**：用与 3×2.5 库封装相同的 IPC 外延公式放到 2.5×3.0 本体上，而不是把 LSM6DS3 焊盘硬转 90°。
- **已解决**：LSM6DSO 3.0×2.5 错误焊盘已从原理图移除。

### CP02 · 2026-09-09 01:00 · 显式布线、固件骨架、导出门控

- **完成**：`tools/route_explicit_revA2.py`（过孔 0.60/0.30）；官方 DRC **380→84 错误**，禁布违例 **9→0**，孔环/钻孔过小 **0**；`firmware/mcu/` 引脚 remap 骨架；`tools/export_fab_revA2.sh` 在 DRC 非零时拒绝导出。当前 **NOT_FAB_RELEASED**。
- **卡点**：仍有约 15 条信号网未布通（I2C、SPI、部分桥路、NRST、CHARGE_IN 等）；短路 18；courtyard 重叠 10。12×35 mm 板上自动寻路无法同时避开焊盘、禁布和既有走线。
- **尝试**：1）纯曼哈顿 4/34 网；2）曼哈顿+约束 A* 19/33 网，DRC 106；3）挪位+收紧禁布，DRC 67 但未连接回升；4）密铺电源过孔，DRC 反弹到 149，已撤回。
- **已解决**：过孔规则 0.60/0.30 可行；U2/U3 顶层禁布约束有效且当前 0 违例；生产 Gerber 不会在 DRC 失败时被写出。
- **本轮新暂缓**：焊盘旁密铺 0.60 过孔（DRC 回归）；继续用迷宫加密（历史 ≥5 轮）。

下一检查点优先：剩余网络改短距离手工边沿走线，不再改过孔规则；固件补采样/Flash 日志伪代码；3D 干涉仍缺壳体模型则继续暂缓。

### CP03 · 2026-09-09 01:00 · 边沿通道试验与固件日志

- **完成**：挪开部分 courtyard 冲突器件（R1/C3/C8/U6/U7 等）；固件增加 `firmware/mcu/src/datalog.c`（W25Q256 页缓存追加，`APO2` 头，不覆盖旧航次）。占用检查布线恢复后官方 DRC **108 错误 / 74 未连接**。状态仍是 **NOT_FAB_RELEASED**。未导出生产 Gerber。
- **卡点**：12×35 mm 上脚本无法同时接通 I2C/SPI/部分桥路且保持 DRC 干净。
- **尝试**：无间隙强制边沿/背面干线一次接通 14 条优先网，官方 DRC 立刻 **84→328**（短路 68、禁布 12、阻焊桥 167）。已撤回该策略。
- **已解决**：确认“不查间距就铺铜”不可行；Flash 日志格式骨架可与协议字段对齐。
- **本轮新暂缓**：强制边沿走线；脚本自动把 DRC 做到 0（已累计 5 种策略）。

下一检查点优先：不要再改自动布线引擎；把时间用在固件采样状态机，或只修单个短路/courtyard，禁止再铺大面积强制铜。

### CP04 · 2026-09-09 01:20 · 固件采样状态机

- **完成**：`firmware/mcu/src/app.c` 状态 `BOOT → RECORD → DUMP → SLEEP`；`sensors.c` 按协议 ODR 调度 IMU/压力/张力/电池；LSE 失败记 `SAMPLE_FLAG_LSE_FAIL`；开机前三个样本打同步敲击标志。未改布线引擎，未导出 Gerber。PCB 官方 DRC 仍为 **108 错误 / 74 未连接**，`NOT_FAB_RELEASED`。
- **卡点**：无 CubeMX / HAL / `arm-none-eabi-gcc`，WHO_AM_I 和磁簧 EXTI 不能在本机验证。剩余 10 处 courtyard 重叠未动（避免再跑自动布线）。
- **尝试**：本轮按 CP03 约定不铺铜。寄存器表按 LSM6DSO / LPS28DFW / NAU7802 手册写入 `sensors.h`。
- **已解决**：采样循环不再空转；时钟失败仍可记日志的路径已写进状态机。
- **暂缓不变**：脚本 DRC=0、CubeMX、实物试验、可放行 Gerber。

下一检查点优先：可在不重布线的前提下只挪冲突封装；或补 UART 转储帧格式。禁止重开迷宫/强制干线。

### CP05 · 2026-09-09 01:40 · UART 回收帧

- **完成**：UART 回收帧 `A5 5A` + 样本 + CRC16（`firmware/mcu/src/uart_dump.c`）；主机解码 `firmware/host/dump_decode.py`，示例 `example_data/uart_dump_fixture.bin` 已解出 1 条样本。DUMP 状态会发最近一条样本。板子恢复为挪封装前的布线。官方 DRC **104 错误 / 74 未连接**。`NOT_FAB_RELEASED`。未导出 Gerber。
- **卡点**：10 处 courtyard 仍在。无 USART HAL，真机转储未验证。
- **尝试**：在已布线板上挪 C3/U6/C10 等，courtyard 降到 6，但焊盘压到旧铜，DRC 升到 175。已从备份恢复。
- **已解决**：回收数据有可测试的帧格式和主机解码器。
- **本轮新暂缓**：已布线板上直接改坐标。

下一检查点优先：固件/主机侧把解码 CSV 列对齐 `autotune.py`；或只写 courtyard 挪位清单供人工在 KiCad 里连铜一起挪。禁止自动铺铜、禁止再对现有走线改封装坐标。

### CP06 · 2026-09-09 02:00 · 调参 CSV 与人工挪位清单

- **完成**：`dump_decode.py --autotune awa|uw` 输出 `autotune.py` 必填列；量程与 `sensors.h` 候选值一致（±4 g / ±500 dps / 4096 LSB/hPa）。示例帧已解出阿波/水中 CSV。人工 courtyard 清单写在 `hardware/revA2/COURTYARD_MOVE_LIST_CN.md`（KiCad 拖动带铜，不要改死坐标）。未改 PCB 铜皮，未导出 Gerber。DRC 仍为 **104 错误 / 74 未连接**，`NOT_FAB_RELEASED`。
- **卡点**：本机 `autotune.py` 缺 scipy，不能用解码 CSV 跑完整寻参。张力无梁标定，水中 `tension_gf` 暂为原始计数。10 处 courtyard 仍要人手处理。
- **尝试**：用夹具 bin 生成 awa/uw CSV 并核对表头齐全。
- **已解决**：回收帧到调参输入的列名已经对齐，不再把 `pressure_raw`/`tension_raw` 直接喂给 `autotune.py`。
- **暂缓不变**：脚本 DRC=0、已布线改坐标、CubeMX、可放行 Gerber。

下一检查点优先：3D/壳体干涉仍缺模型则继续暂缓；可补固件量程写入 CTRL 寄存器的注释清单。禁止自动布线和禁止对现有走线改封装坐标。

### CP07 · 2026-09-09 02:20 · 传感器 CTRL 与 3D 暂缓

- **完成**：LSM6DSO CTRL1_XL/CTRL2_G 阿波 `0x48/0x44`、水中 `0x58/0x54`（104/208 Hz，±4 g / ±500 dps）写入 `sensors.h` 与 `sensors_configure()`；清单 `firmware/mcu/SENSOR_CTRL_INIT_CN.md`。3D 项书面暂缓于 `hardware/revA2/3D_CHECK_PARKED_CN.md`。未改 PCB，未导出 Gerber。DRC 仍为 **104 错误 / 74 未连接**，`NOT_FAB_RELEASED`。
- **卡点**：I2C 写返回 -1（无 HAL）。LPS28DFW CTRL_REG1 的 ODR 位需对照 DS13317 再填具体字节。无 Rev.A2 壳体 STEP。
- **尝试**：在 `sensors_init` 中调用 configure；无总线时保持 imu/press/strain 失败闭合。
- **已解决**：量程候选值与要写进芯片的 CTRL 字节已对齐，主机解码不再是孤立换算。
- **暂缓不变**：3D 干涉、脚本 DRC=0、可放行 Gerber、CubeMX。

下一检查点优先：可补 LPS28DFW CTRL 字节（对照 DS13317）；或 LED 闪光策略骨架。禁止自动布线。

### CP08 · 2026-09-09 02:40 · LPS28DFW CTRL 与 LED 闪光骨架

- **完成**：按 DS13317 Rev 1 Table 19/20 与 §9.7 写入 LPS28DFW：阿波 CTRL_REG1=`0x2C`（50 Hz，AVG 64）、CTRL_REG2=`0x08`（BDU，Mode 1）；水中 CTRL_REG1=`0x3C`（100 Hz，AVG 64）、CTRL_REG2=`0x48`（BDU，Mode 2）。解码：阿波 4096 LSB/hPa，水中 2048 LSB/hPa。阿波 LED 骨架 `firmware/mcu/src/led.c`：RECORD 中 10 Hz、2 s 闪光，DUMP/SLEEP 关闭；无咬钩检测器。未改 PCB，未导出 Gerber。DRC 仍为 **104 错误 / 74 未连接**，`NOT_FAB_RELEASED`。
- **卡点**：I2C 写仍返回 -1。无 GPIO HAL，LED 不会真正点亮。AVG 128 在 100 Hz 非法，未采用。
- **尝试**：先写 CTRL_REG2 再写 CTRL_REG1，避免 ODR 已开时再切满量程。对照 Table 21 确认 AVG 64 在 50/100 Hz 均可。
- **已解决**：压力 CTRL 不再写 0；15 m 水深不再误用 1260 hPa / 4096 LSB。
- **暂缓不变**：脚本 DRC=0、可放行 Gerber、CubeMX、3D、实物试验。

下一检查点优先：可补 NAU7802 上电 `PU_CTRL` 字节；或磁簧 EXTI 唤醒骨架。禁止自动布线。

### CP09 · 2026-09-09 03:00 · NAU7802 上电与磁簧 EXTI

- **完成**：水中 NAU7802 按 V1.7 §9.1 写 PU_CTRL `0x01`→`0x02`，读 PUR，再 `0x86`（内部 LDO）/`CTRL1=0x2F`（3.0 V、PGA 128×候选）/`CTRL2=0x70`（320 SPS）/`0x96`（CS）。阿波不初始化（U4 DNP）。磁簧：SW1 常开对地、R10 上拉，`board_reed_exti_setup()` 在 PA11_RMP 之后按 EXTI9 下降沿描述；长按 1.5 s 进 DUMP。未改 PCB，未导出 Gerber。DRC 仍为 **104 错误 / 74 未连接**，`NOT_FAB_RELEASED`。
- **卡点**：I2C 读写仍返回 -1，PUR 读不到。无 GPIO，磁簧不会唤醒。未做内部 offset 校准（需要等 CALS 清零）。PGA 128×未梁标定。
- **尝试**：对照 V1.7 §11.1–11.3 核对应节位；示例值 `0xAE` 含只读 PUR/CR，写入改用 `0x86`/`0x96`。
- **已解决**：张力 ADC 不再只写 CTRL2；磁簧极性与 EXTI 顺序已写进骨架，不会在 remap 前开 EXTI。
- **暂缓不变**：脚本 DRC=0、可放行 Gerber、CubeMX、3D、实物试验。

下一检查点优先：可补 LSM6DSO/LPS28DFW WHO_AM_I 读取顺序；或 W25Q256 页编程骨架。禁止自动布线。

### CP10 · 2026-09-09 03:20 · WHO_AM_I 与 Flash 页编程

- **完成**：`sensors_probe()` 先读 LSM6DSO WHO_AM_I=`0x6C`、LPS28DFW WHOAMI=`0xB4`，ID 不对不写 CTRL。W25Q256 骨架 `firmware/mcu/src/flash.c`：JEDEC `0x9F` 期望 `EF 40 19`，`0x06` 写使能、`0xB7` 四字节地址、`0x12` 页编程；失败则 RAM 页保留、地址不前进。未改 PCB，未导出 Gerber。DRC 仍为 **104 错误 / 74 未连接**，`NOT_FAB_RELEASED`。
- **卡点**：I2C/SPI 仍无 HAL，探测与编程都返回失败。无扇区擦除（避免覆盖未读航次）。
- **尝试**：页满时若编程失败则丢弃新样本，避免 RAM 越界；不用 3 字节 `0x02`，因为芯片是 32 MB。
- **已解决**：上电不再在未识别芯片上写 CTRL；Flash 不再在未编程成功时假装已经落盘。
- **暂缓不变**：脚本 DRC=0、可放行 Gerber、CubeMX、3D、实物试验。

下一检查点优先：可补 LSM6DSO 数据读取（OUTX_L_G/A）；或 VBAT ADC 分压换算骨架。禁止自动布线。

### CP11 · 2026-09-09 03:40 · IMU 连读与 VBAT 换算

- **完成**：LSM6DSO 写 CTRL3_C `0x04`（IF_INC），从 `OUT_TEMP_L` 连读 14 字节填温度/陀螺/加速度；LPS28 24-bit 压力、NAU7802 24-bit 张力。读失败不置 OK 标志。VBAT：R4=1 MΩ、R5=330 kΩ，`battery_mv = adc * 13300 / 4095`。未改 PCB，未导出 Gerber。DRC 仍为 **104 错误 / 74 未连接**，`NOT_FAB_RELEASED`。
- **卡点**：I2C/ADC 仍无 HAL，样本轴和电池毫伏保持 0。温度按 256 LSB/°C、0 LSB=25°C 写入 0.01°C。
- **尝试**：用 14 字节连读而不是分两次读 0x22/0x28，避免 IF_INC 关闭时读到重复寄存器。分压整数式先约分，避免 uint32 溢出。
- **已解决**：调度点不再在未读总线时假装 IMU/压力 OK；4.2 V 电芯在 12-bit 满量程之前（约 1.04 V 感测点）。
- **暂缓不变**：脚本 DRC=0、可放行 Gerber、CubeMX、3D、实物试验。

下一检查点优先：可补 LPS28DFW 温度寄存器；或 USART2 引脚 AF 初始化骨架。禁止自动布线。

### CP12 · 2026-09-09 04:00 · 压力温度与 USART2 AF

- **完成**：LPS28DFW 从 `PRESS_OUT_XL` 连读 5 字节，温度按 DS13317 100 LSB/°C 写入样本（已是 0.01°C）；与 IMU 同时到点时用压力温度。USART2：PA2/PA3 AF1、115200 8N1、HSI 16 MHz 时 BRR≈139；不占用 PA9/PA10。`uart_dump_send_sample()` 无 USART 时改为返回失败。未改 PCB，未导出 Gerber。DRC 仍为 **104 错误 / 74 未连接**，`NOT_FAB_RELEASED`。
- **卡点**：无 CubeMX 时钟树，未写 GPIO/USART 寄存器。无 I2C，温度字段仍为 0。
- **尝试**：确认 TEMP_OUT 紧跟 PRESS_OUT，IF_ADD_INC 默认已开。回收发送不再返回 0 假装已发出。
- **已解决**：样本温度有压力芯片路径；DUMP 不会在没串口时报告发送成功。
- **暂缓不变**：脚本 DRC=0、可放行 Gerber、CubeMX、3D、实物试验。

下一检查点优先：可补 SPI1 AF 脚（PA5/6/7）初始化顺序；或 I2C1 PB6/PB7 AF6 骨架。禁止自动布线。

### CP13 · 2026-09-09 04:20 · SPI1 与 I2C1 引脚骨架

- **完成**：`board_spi1_init()`：PA4 `/CS` 先拉高，再 PA5/6/7 AF0、SPI Mode 0；`board_i2c1_init()`：PB6/PB7 AF6 开漏，400 kHz TIMINGR 候选 `0x0010061A`（仅 HSI 16 MHz）。Flash/传感器读写改走这些入口，无 HAL 仍失败闭合。未改 PCB，未导出 Gerber。DRC 仍为 **104 错误 / 74 未连接**，`NOT_FAB_RELEASED`。
- **卡点**：无 CubeMX 时钟树，未写 SPI/I2C 寄存器。TIMINGR 必须按实际 PCLK 重算。
- **尝试**：SPI1EN 在 APBENR2 bit 12，I2C1EN 在 APBENR1 bit 21，避免和 USART2 时钟位搞混。
- **已解决**：总线初始化顺序写进开机路径；`/CS` 不会在 SPE 之前悬空为低。
- **暂缓不变**：脚本 DRC=0、可放行 Gerber、CubeMX、3D、实物试验。

下一检查点优先：可补 I2C1 起停时序/NACK 失败闭合；或 SPI1 忙等待超时。禁止自动布线。

### CP14 · 2026-09-09 04:40 · I2C NACK 恢复与 SPI/Flash 超时

- **完成**：I2C 写/读按 START → 数据 → STOP；NACK 或轮询满 `I2C_XFER_POLL_MAX` 时发 STOP 清 NACKF，半截缓冲不当有效。SPI 每字节等 TXE/RXNE，结束后等 BSY 清，满 `SPI_XFER_POLL_MAX` 失败。页编程后最多 32 次 RDSR1 等 BUSY。未改 PCB，未导出 Gerber。DRC 仍为 **104 错误 / 74 未连接**，`NOT_FAB_RELEASED`。
- **卡点**：仍不读 SPI/I2C 寄存器（无 SPE/PE），等待循环会到期失败。无无限空转。
- **尝试**：把超时做成有上限的轮询，而不是无条件 `return -1` 藏起路径。
- **已解决**：总线错误会 STOP/`/CS` 释放；Flash 不再在未看到 BUSY=0 时当作编程完成。
- **暂缓不变**：脚本 DRC=0、可放行 Gerber、CubeMX、3D、实物试验。

下一检查点优先：可补 I2C 总线卡死时的 SCL 时钟恢复；或 USART2 TXE 超时。禁止自动布线。

### CP15 · 2026-09-09 05:00 · I2C SCL 恢复与 USART2 TXE/TC 超时

- **完成**：`board_i2c1_bus_recover()`：PE 关闭后在 PB6 最多打 9 个 SCL 脉冲，再发 STOP（SDA 低→高、SCL 保持高）；初始化与 STOP 失败时调用。USART2 每字节等 TXE、帧末等 TC，满 `USART_XFER_POLL_MAX` 失败闭合。未改 PCB，未导出 Gerber。DRC 仍为 **104 错误 / 74 未连接**，`NOT_FAB_RELEASED`。
- **卡点**：本机不碰 GPIO/USART 寄存器，恢复与发送都会到期失败。无 CubeMX，不能上板验证从机是否松 SDA。
- **尝试**：`i2c_abort()` 自己轮询 STOPF，不再回调 `i2c_wait_isr()`，避免超时路径递归。恢复只走 PB6/PB7，不用 PA9/PA10。
- **已解决**：SDA 被从机拉死时有时钟恢复入口；DUMP 串口不会空等 TXE。
- **暂缓不变**：脚本 DRC=0、可放行 Gerber、CubeMX、3D、实物试验。

下一检查点优先：可补唤醒后 I2C/SPI 重初始化；或 IMU INT EXTI。禁止自动布线。

### CP16 · 2026-09-09 05:20 · Stop 唤醒重开总线与 IMU INT1（五小时长程结束）

- **完成**：`board_buses_reinit_after_stop()` 在 SLEEP→RECORD 时先拉高 `/CS` 再重开 SPI1/I2C1（含 SCL 恢复），不改 PA9/PA10 remap、不关 SWD。`board_imu_int_exti_setup()` 描述 PA0/EXTI0 上升沿；`INT1_CTRL=0x03`（XL+G DRDY）。未改 PCB，未导出 Gerber。DRC 仍为 **104 错误 / 74 未连接**，`NOT_FAB_RELEASED`。20 分钟循环 14 拍已跑完。
- **卡点**：无 CubeMX / 无 GPIO，Stop 进不出、INT 读不到。INT 不闸门时间调度采样，避免本机一直读不到 IMU。
- **尝试**：IMU 用 EXTI0 上升沿，磁簧仍用 EXTI9 下降沿，两条线不共用。唤醒只重开 MCU 外设，不重写传感器 CTRL（VDD 未掉）。
- **已解决**：休眠醒来不会拿着半截 SPI/I2C 事务继续记日志；INT1 脚与手册 INT1_CTRL 对齐。
- **暂缓不变**：脚本 DRC=0、可放行 Gerber、CubeMX、3D、实物试验、迷宫布线。

五小时长程到此结束。后续若继续：只能在 KiCad 里手工/交互布线清 DRC，或等本机装上 CubeMX 再生成可编译工程。禁止自动布线，禁止在 DRC 未清零时导出生产 Gerber。









### CP17 · 2026-09-23 · 官方基线重跑、局部PCB修复与固件回归

- 开始确认 cursor/已有未提交改动；ERC 0/0，DRC 104/133/74。检查点保存在 validation/revA2_20260923。
- 纠正 U2 X/Y，分组处理 Pogo/充电/桥接口/LED/过孔/板边，补局部供电与内层馈线，保留所有焊盘网络。最终 DRC 12/108/59、短路0、间距0、禁布0，一致性0。失败候选及 U2 逃线禁布矛盾均有官方报告，未合入诊断铜。
- 固件15项native回归通过；修正RCC地址、日志写入/重启/满盘保护、完整转储及严格主机数据门槛。ARM/板上未通过；scipy缺失。
- 实际生产导出 exit 2 拒绝，无生产文件。下轮执行顺序与所缺资料详见 DEVELOPMENT_20260923_CN.md。目标仍未完成，不把此次检查点称为PCB/固件发行完成。

### CP18 · 2026-09-23 · U2逃线与接地、供电及真实时基门槛

官方主板结果0普通错误/108警告/40未连接，一致性0；ERC0/0。新增U2径向窄通道且全投影禁via/pour，12个热焊盘错误通过接线消除。磁簧、Flash供电、电池分压局部连接完成。失败MCU供电候选未采用，下一步先成组处理LSE与阻挡铜。固件17测试通过，取消伪时间并验证3小时相位调度/回绕；真实HAL仍阻塞。导出exit2，无生产文件。详见CONTINUATION_20260923_CN.md。

### CP19 · 2026-09-23 · 活动目标首轮进展

40→25个连接缺口，0普通错误/111警告，ERC0/0、一致性0。成组重排LSE并通过独立几何/连通性复核，226采样点位于In1地；补电源与地岛。桥路铜长量化显示仍需模拟区重排。host时间展开和真实ARM对象构建均有新证据，最终ELF缺链接器/运行库。工具链安装问题待用户授权，未安装。目标持续active；细节见GOAL_CHECKPOINT_20260923_CN.md。

### CP20 · 2026-09-23 · 桥路主输入对称与TIM2后端

成组旋转U4/J3并重排R8/R9/C13及去耦，原始输入两路2.670mm、滤波主路径各2.615mm，全F无via；23个缺口、0普通错误、121丝印警告。近端地回流已补，696采样点有In1覆盖。J3按新物理顺序接线。TIM2寄存器模型两变体通过，主任务23 host/2 MCU回归、20 ARM对象构建通过；链接缺依赖仍失败。目标active，未放行；细节见ANALOG_CHECKPOINT_20260923_CN.md。

CP20末轮补充：LED供电实际接入主3V3后，主板为0普通错误/119警告/22未连接，一致性0，ERC0/0。导出仍exit2。前述23/121为本轮中间检查点，不代表当前主文件。


### 2026-09-23 · SCK 重新布线已采用

14→13 未连接，普通错误0，警告120，ERC0/0，一致性0。In1 无新信号，显式填铜敏感网及原有走线参考检查通过；C3/CS/供电连动修改，回退与逐阶段证据在 validation/revA2_sck_rework。丝印未关闭，导出 exit2。详见 SCK_CHECKPOINT_20260923_CN.md。


### 2026-09-23 · MISO重新布线已采用

SCK后13→12未连接，普通错误0，警告119，ERC0/0，一致性0。首版0.145mm间距违规拒绝，第二版通过后采用；新MISO单via，相关C14/CS/REED连动调整。独立填铜采样无自身反焊盘以外新缺口，但回流/SI未验证。回退、分类与命令见 MISO_CHECKPOINT_20260923_CN.md。导出exit2，NOT_FAB_RELEASED。


### 2026-09-23 · U3来源恢复及电源地闭合

找回原包hash/CRC匹配，原厂中央线与外围径向连接已解析。窄通道保留全本体via/pour禁布，经正反例及独立审核采用。官方主板0普通错误/8未连接/119警告、ERC0/0、一致性0，导出exit2。见 U3_ESCAPE_CHECKPOINT_20260923_CN.md，仍NOT_FAB_RELEASED。


### 2026-09-23 · 上部I²C与C2局部重排

U2/U3 SDA/SCL接通，8→6未连接；C2旋转连动供电/地，至U2供电线1.5575mm，同面无via。官方0普通错误/120警告、ERC0/0、一致性0；7个自身供电via反焊盘边缘参考点有独立处置。每次分类/回退与主板证据在validation/revA2_i2c，详见UPPER_I2C_CHECKPOINT_20260923_CN.md。NOT_FAB_RELEASED，导出exit2。


### 2026-09-23 · ADC SCL闭合

6→5未连接，0普通DRC错误/120警告、ERC0/0、一致性0。SCL三via跨F/In2/B/F；相关REED显式重排后SW1/R10/MCU实际连通。首两版拒绝，stage3采用；独立4560点新线参考采样和主板增量审查通过。制造脚本exit2，NOT_FAB_RELEASED。详见ADC_SCL_CHECKPOINT_20260923_CN.md。


### 2026-09-23 · SCL全线及上部SDA接入

按两组采用并分别官方复检：5→4→3未连接，普通错误0，最终122警告、ERC0/0、一致性0。R2及SCLvia连动，上部SDA新增In2连接与地孔。独立实际连通/填铜参考通过限定几何审查，SDA45个自身反焊盘边缘点单独处置；EP窄余量保留为装配风险。详见I2C_JOIN_CHECKPOINT_20260923_CN.md。生产导出仍exit2。


### 2026-09-23 · ADC SDA闭合与3D清单

3→2未连接，普通错误0、122警告、ERC0/0、一致性0。R1/SCK连动让出SDA桥；ADC新via从焊盘内移到外侧再采用。主任务6549点新铜参考采样及真实BFS通过限定几何审查。官方STEP审查件生成，但7器件无模型、Y1路径无效，3D仍未通过。见ADC_SDA_CHECKPOINT_20260923_CN.md。制造导出exit2。


### 2026-09-23 · Via/焊盘审查与未采用候选

主板未变。只读审查72via，发现6个焊盘内中心（4元件+2Pogo接触）。R5 stage2普通错误0、候选内孔6→5，但零长REED线待清理；最后stage3命令因审批额度不足未执行。MOSI候选15错误拒绝。详见VIA_PAD_CHECKPOINT_20260923_CN.md，全部候选保留，NOT_FAB_RELEASED。


### 2026-09-23 · 固件ARM资源证据

PCB操作审批受额度限制，未重试拒绝动作。独立固件工作：Clang23.1.0两个版本20对象带栈使用报告构建成功，llvm-size交叉确认RAM节714/705字节。已知调用路径616字节但运行库/异常未知，非完整上界，最终ELF未完成。见firmware/mcu/VERIFICATION_STACK_RESOURCES_CN.md。主板仍2未连接/122警告、R5候选未采用。


### 2026-09-23 · R5制造修复正式采用

账户状态变化后经原审批路径重试成功，未绕过审核。stage3移除零长度线，R5从焊盘内孔变为显式引线，6→5项焊盘内中心。官方主板0普通错误/2未连接/122警告、ERC0/0、一致性0，导出exit2。详见R5_MANUFACTURING_CHECKPOINT_20260923_CN.md。


### 2026-09-23 · SCL焊盘内孔两组修复

ADC及MCU SCL孔分别移出焊盘，5→4→3项内孔中心；连接/参考/官方检查后分组采用。0普通错误/2未连接/122警告，ERC0/0、一致性0，导出exit2。IMU独立候选29错误和参考缺口拒绝。详见SCL_VIA_MANUFACTURING_CHECKPOINT_20260923_CN.md。


### 2026-09-23 · LED焊盘内孔关闭

stage1碰电池焊盘拒绝；stage2缩短LED铜并把via移到(1.6,30.7)后采用。焊盘内中心3→2，剩Pogo接触孔，已询问所购头部/定位资料。官方主板0普通错误/2未连接/122警告、ERC0/0、一致性0，导出exit2。详见LED_VIA_MANUFACTURING_CHECKPOINT_20260923_CN.md。


### 2026-09-23 · 恢复DRC检查与工程状态注释

五项ignore改warning，修正地线端点；无ignored/exclusion，新增可见3个连接区courtyard项，125警告。随后仅将长工程说明B.SilkS→Dwgs.User，铜字节不变，官方111警告。主板0普通错误/2未连接、ERC0/0、一致性0，导出exit2。见DRC_VISIBILITY_CHECKPOINT_20260923_CN.md。


### 2026-09-23 · IMU逃逸收敛与完整连接诊断

U2/C10完整扇出重建候选0普通错误、关键/新铜参考通过，但仍需MCU终端且最大本体余量仅.03mm。完整通道首版6普通错误、新增3V3开路和3条旧铜新参考缺口，拒绝；主板未变。精确下一步见IMU_ROUTING_CHECKPOINT_20260923_CN.md，已询问实际板厂工艺，当前维持.6/.3via。


### 2026-09-23 · IMU正式闭合

上部余量与MCU try9分组修复后，冲突检查合并、全板官方DRC/九网BFS/29391点新铜审查完成并采用。0普通错误/1MOSI未连接/110警告、ERC0/0，一致性0，无忽略/排除；一处局部3V3换层参考裁剪明确处置，严格值未改。导出exit2。见IMU_CONNECTED_CHECKPOINT_20260923_CN.md，仍NOT_FAB_RELEASED。


### 2026-09-23 · 仅检查模式

export_fab支持--check-only，5个隔离编排测试通过，实际官方ERC0/DRC0普通错误/1MOSI开路/110警告，exit2；制造目录前后不存在。PCB未改。后续最后开路清零时仍用仅检查模式，避免警告/机械未审时自动导出。详见CHECK_ONLY_CHECKPOINT_20260923_CN.md。


### 2026-09-23 · U3/J3位号修正

仅两个Reference字段字节变化，保持可见丝印；110→107警告，无新增项。主板0普通错误/1MOSI开路、ERC0/0、一致性0；仅检查模式exit2，无制造导出。详见REFERENCE_TEXT_CHECKPOINT_20260923_CN.md。


### 2026-09-23 · LDO电容角色核对

读取网表/BOM及TI原厂资料确认C3=100n、C10=1µF，近端U7→C10路径未因候选C3移动改变；有效容量仍缺实际MLCC资料，未声称稳定性通过。独立MOSI候选仍迭代，正式板未改。见LDO_CAPACITOR_REVIEW_CN.md。


### 2026-09-23 · 整板电气连接闭合

MOSI最终独立回放、主任务官方/全网BFS/23262点新铜与关键参考检查通过后采用，0普通错误/0未连接/105警告、ERC0/0、一致性0。实际地岛接回，删除LSE悬端，无工艺下限放宽。仅检查exit0不生成fab；仍NOT_FAB_RELEASED。详见MOSI_CONNECTED_CHECKPOINT_20260923_CN.md。


### 2026-09-23 · U3最大本体余量与C13位号

C13仅文字属性调整，105→95警告并局部PDF渲染复核；U3移位/12段铜与库规则同步，最大本体via净距最小.10mm，正反例及主任务2958点审查通过。正式0错误/0未连/95警告、ERC0/0，无忽略排除；仅检查exit0无fab。详见U3_MARGIN_AND_C13_CHECKPOINT_20260923_CN.md。
