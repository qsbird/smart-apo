# STM32G031 LSE 有界启动（2026-09-23）

本报告更新旧 TIM2/时序报告中“LSE 未实现”的软件状态。已实现寄存器级启动与失败返回；**未验证实板起振、晶体参数、RTC 或低功耗功能**。

`board_start_clocks()` 先运行原有 `time_start()`，再要求 `board_time_us()` 给出有效 TIM2 时间。无有效时基时不访问 LSE/PWR。返回 1 仅表示本次观察到 LSEON+LSERDY 且无 bypass/CSS 故障/备份域 reset；其他路径返回 0。既有 app_boot 将该布尔值保存到 `sensors->lse_ok`，样本按此生成 LSE_FAIL；它是启动状态快照，不是运行期间的连续振荡器监控。APP_ERROR_CLOCK 的独立失败语义不变。

启动只写 BDCR.LSEON，保留 LSEDRV、RTCSEL、RTCEN、CSS、LSCO 等位，禁止 reset 备份域。已经 ready 时不进行备份域写入。已开但未 ready 时继续有界等待。BYP、CSS 检测故障、BDRST 或 ON=0/RDY=1 异常直接失败，不擅自修复已有备份域。开启 PWR 时钟并读回，设置 DBP 并在 TIM2 总预算内等待；受保护写入无效时失败。结束时恢复本次获取的 DBP/PWREN 位，保留原来已开启的权限与其他位；恢复读回失败也返回 0。超时不关闭 LSE，避免破坏其他备份域消费者。要求启动阶段独占 RCC/PWR 写入。

2 秒是软件策略超时，包含 DBP 等待，单位来自现有 HSI16/TIM2 标称微秒；允许计数器自然回绕。TIM2 停转或配置故障使等待立即失败。**TIM2 仍是 HSI16 来源，LSE ready 不代表时间戳已被 LSE 校准。** DS 的 2 秒只是典型启动时间，没有最坏上限；本策略可能拒绝较慢但健康的晶体，不承诺所有温度电压下启动成功。

硬件工作 BOM 的 Y1 仅列 `32.768kHz 12.5pF`，没有可核查的准确料号/ESR/最大驱动参数。代码保留当前 drive（复位默认低驱动），没有人为提高 drive；这不等于与板上负载匹配。仍需确认准确晶体规格、负载/寄生电容、增益裕量、实际驱动功率以及冷启动/温度/电压边界。没有 NVIC、RTC 配置、Stop 唤醒或成功测量声明。

## 官方依据

本次实际读取 ST 官方资料，未新增依赖：

- [stm32g031xx.h](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-g0/master/Include/stm32g031xx.h)：RCC BDCR 偏移0x5C、LSEON/RDY/BYP/DRV/CSSD/BDRST 位，APBENR1.PWREN bit28，PWR.CR1.DBP bit8。
- [ST LL RCC](https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/master/Inc/stm32g0xx_ll_rcc.h)：LSE enable/ready 与晶体/bypass 模式、drive 字段、CSS 故障状态访问。
- [ST LL PWR](https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/master/Inc/stm32g0xx_ll_pwr.h)：DBP 控制备份域写访问。
- [DS12992 Rev4](https://www.st.com/resource/en/datasheet/stm32g031f8.pdf) 表40及其说明：四种 drive 对应不同晶体增益条件；2秒启动为典型值，随晶体厂商显著变化，负载器件/布局必须独立确认。

## 实际验证

仓库根目录执行，日志见 `validation/lse/`：

```sh
python3 -m unittest discover -s firmware/host/tests -v
python3 -m unittest discover -s firmware/mcu/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/lse/arm
/opt/homebrew/opt/llvm/bin/clang --analyze --target=arm-none-eabi -mcpu=cortex-m0plus -mthumb -std=c11 -ffreestanding -I firmware/mcu/include -I firmware/mcu/runtime/include firmware/mcu/src/board.c -o /tmp/lse-board.plist
```

- host 23/23，7.553秒；MCU 8/8，6.266秒（原7项+LSE模型）；两变体分别运行全部寄存器模型。
- LSE 模型直接编译实际 board.c，并使用真实 TIM2 实现配合模拟寄存器，覆盖 cold start、already ready、already on、重入 epoch、超时、计数器回绕、无有效时基、PWREN/DBP/BDCR 写入被拒绝、运行中时基停止/时钟破坏、BYP/CSS/reset 异常、无关位保留与权限恢复。
- 原 TIM2 模型仅新增惰性 LSE hooks，原断言全部保留。未改 TIM2/GPIO/ADC/其他总线实现；ADC 由主代理同时修改，本次全回归包含该修改。
- AWA/UW 共20个 Cortex-M0+ 目标文件通过 `-Wall -Wextra -Werror`；独立解析20个 ELF 头均为 little-endian ELF32 ARM relocatable，SHA256见 `validation/lse/objects.json`。
- ARM clang 静态分析无诊断，plist 见验证目录。没有链接/烧录/实板测量；模型不模拟真实晶体、异步同步器、APB 延迟或电气特性。

修改范围：`src/board.c` 的 LSE helper/启动返回；`include/board_revA2.h` LSE 常量与契约；`tests/tim2_timebase.c` 惰性 hook；新增 `tests/lse_registers.c`、`tests/test_lse.py`、本报告及验证日志。无安装、无新依赖、无提交。
