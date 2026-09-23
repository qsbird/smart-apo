> 最新日志读取修复：CRC失败时不再覆盖调用者的有效样本，空指针不推进游标的既有防护纳入回归。host契约23项通过（日志用双变体），20个ARM对象编译验证通过；函数静态栈帧40→72字节，仍无最终ELF/上板。见VERIFICATION_LOG_READ_SAFETY_CN.md。

> 最新最终链接实测（2026-09-23）：AWA/UW两次`make all`均因现有Clang找不到lld而exit2，20个新目标文件确认为ARM ELF32 REL；没有最终ELF、未上板。缺ARM链接器及builtins库，未安装新依赖。详见 hardware/revA2/CURRENT_DELIVERY_AUDIT_20260923_CN.md及validation/revA2_current_delivery_audit/。

> 最新资源证据（2026-09-23）：两个版本20个真实ARM对象带-fstack-usage编译通过；静态RAM节714/705字节，已知调用链栈帧小计616字节。未知运行库/异常栈未覆盖，最终ELF和完整栈安全仍未通过。见VERIFICATION_STACK_RESOURCES_CN.md。

# STM32G031 Rev.A2 固件开发状态

截至2026-09-23：主代理实际重跑MCU模型/runtime **8/8**、host回归 **23/23**，AWA/UW两变体共 **20个Cortex-M0+ ELF32目标文件**编译及标头检查通过。**最终ELF未链接、未烧录、没有板上运行或发行包**；缺链接器与ARM compiler runtime，新增工具链安装授权待答复。未安装CubeMX，没有声称CubeMX生成或验证过完整工程。

## 实现层级

| 功能 | 当前证据 | 尚未完成 |
|---|---|---|
| TIM2微秒时基 | 真实寄存器+状态模型 | HSI精度、实物计时、跨Stop补偿 |
| LSE启动 | 真实寄存器、有界2s策略超时+模型 | 准确晶体/drive/负载匹配、板上起振、连续监控 |
| SPI1 / UART TX / I²C1 | 真实寄存器+故障模型 | 真实器件、波形、吞吐与边界工况 |
| GPIO / 磁簧 | IDR实读、释放边沿锁存、1.5s模型 | 电平/抖动、NVIC/ISR、Stop唤醒 |
| ADC电池 | 原始码后端、分压换算、100ms启动保护 | 参考电压、实际RC/漏电/精度、运行中电压阶跃 |
| 传感器/Flash/转储 | 模型与协议回归 | 实际寄存器应答、NOR写入/掉电、整航次 |
| LED | PB0写入/读回、闪光/取消/故障模型 | 实际波形/亮度、轮询节拍、咬钩检测 |
| SLEEP/Stop | 软件等待保持时基、恢复及故障转储模型 | 真正硬件Stop、RTC补偿与功耗验证 |

每项证据与局限见 `VERIFICATION_TIM2_CN.md`、`VERIFICATION_LSE_CN.md`、`VERIFICATION_SPI_CN.md`、`VERIFICATION_UART_CN.md`、`VERIFICATION_I2C_CN.md`、`VERIFICATION_GPIO_CN.md`、`VERIFICATION_ADC_CN.md`。早期报告的“骨架”和测试数量是历史状态。

## 启动、变体和引脚

`app_boot`依次开启SYSCFG、设置PA11_RMP/PA12_RMP、启动TIM2并尝试LSE，然后初始化GPIO、SPI/I²C、磁簧轮询边沿、UART及日志/传感器。PA13/14保留SWD。LSE仅提供启动ready快照；无论LSE成功与否，当前时间戳仍由HSI16/TIM2提供。`SAMPLE_FLAG_LSE_FAIL`不是时间戳校准状态。

同一PCB的AWA变体为LSM6DSO+LPS28DFW+Flash+LED；UW另贴NAU7802与桥路，用`SMART_APO_VARIANT_AWA/UW`选择。物理引脚表见仓库 `hardware/revA2/STM32G031_TSSOP20_PIN_REVIEW_CN.md`，数据协议见 `firmware/DATA_AND_AUTOTUNE_PROTOCOL_CN.md`。

R4/R5现为180kΩ/60.4kΩ、1%，名义毫伏换算 `adc*132220/41223`。启动前100ms拒绝ADC读取且不改输出；C14的100nF X7R、容差≤20%及温度/时钟裕量是设计条件，未由实物证明。详见硬件 `DIVIDER_GPIO_CHECKPOINT_20260923_CN.md` 与启动检查点。

## 状态、存储和接口

软件路径为BOOT→RECORD→DUMP→SLEEP，失败进入ERROR；发现已有APO2日志则只读DUMP。**SLEEP目前不是硬件Stop**，不能宣称低功耗或磁簧中断唤醒已运行。`board_buses_reinit_after_stop`故意使失去补偿的TIM2时基失效；软件SLEEP现不再调用它；等待和转储期间持续服务真实时基，恢复保持同一epoch。时钟失效则仅允许只读转储，不恢复写日志。

RECORD按整数相位调度104/208/320Hz等名义速率；迟到只读当前值，不伪造历史样本。IMU连读14字节、压力5字节，失败不置有效位。同步敲击检测尚未实现；PA0即时电平轮询不能保证捕获短脉冲。

磁簧为PA9低有效。1.5s持续闭合资格使用TIM2及EXTI9上升沿pending清除释放历史，IMR/EMR屏蔽，没有NVIC/ISR。GPIO或时基错误清除资格。

SPI为Mode0、约1MHz、8位访问和软件CS；I²C使用保守标准模式时序计算、7bit地址、重复起始读和有界故障处理，干净NACK不屏蔽其他设备，硬故障需要显式恢复。具体时序假设和测试不等于板上合格。

Flash写前检查整页空白/WEL，写后读回；已有日志只读回收，未知/损坏头拒写，不自动擦除历史。BUSY已改为TIM2实时时限5ms，并有连续4096次停滞终止；首次ready允许无TIM2只读恢复，真正PP前必须验证时基进展。原厂页写最大3ms的依据及边界测试见 `VERIFICATION_FLASH_TIME_CN.md`。读失败/半帧不当有效数据。UART格式仍 `A5 5A | version=1 | len | sample | crc16`；TX等待TXE和末尾TC，失败后APP显式重新初始化TX后端并在下一步重试原记录，但没有主机ACK，不能证明主机持久化。

`app_error_flags()`提供日志/转储粘滞错误；失败保留样本/记录。主机解码为 `firmware/host/dump_decode.py`，默认拒绝时戳回绕，显式展开需满足记录间隔约束。TIM2的模2^32单调契约要求调用间隔不超过INT32_MAX微秒；Stop、停转或配置异常失败闭合。

## 实际验证

在仓库根目录：

```sh
python3 -m unittest discover -s firmware/mcu/tests -v
python3 -m unittest discover -s firmware/host/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/flash_time_checkpoint/arm
python3 tools/check_divider_revA2.py
```

当前集成日志及20个对象哈希在 `validation/revA2_interactive/`；软件等待/转储/LED的新回归与局限见 `VERIFICATION_IDLE_LED_CN.md`；各后端还有独立状态模型/静态分析证据。不得直接运行宿主编译的生产main：默认MMIO地址属于MCU；宿主测试必须使用明确隔离的hooks。

下一步：完成真实Stop/RTC时间设计、咬钩检测与最终链接/栈预算，再以样机验证传感器、NOR/转储、ADC、时钟、功耗和故障恢复。PCB仍NOT_FAB_RELEASED。
