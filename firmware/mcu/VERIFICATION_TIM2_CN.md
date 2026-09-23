# STM32G031 TIM2 微秒时基（2026-09-23）

已实现寄存器级运行态时基；通过宿主寄存器模型和实际 ARM 目标文件编译。**未链接完整固件、未烧录、未验证板上运行/精度。** 本文更新旧 `VERIFICATION_TIMING_CN.md` 中“时基始终失败”的状态，其他未关闭 HAL 条件仍有效。

## 实现与约束

`board_start_clocks()` 在现有 app_boot 调用点初始化 TIM2。LSE 仍未实现，返回 0 保留 LSE_FAIL。`board_time_us()` 初始化前保持原来的失败闭合行为，不触碰 MMIO。

启动和每次读取验证 RCC：HSI 开启且就绪、HSIDIV=/1、系统时钟请求和实际来源均为 HSISYS、AHB/APB 分频均 /1。任何不同配置直接拒绝；不修改系统时钟树。读取时还验证校准/微调寄存器未变化。因此 TIM2 标称输入 16 MHz，PSC=15、ARR=0xffffffff；UG 装载预分频，清状态，启动内部时钟向上计数，禁用中断/DMA。32 位 CNT 原子读取并自然回绕，无软件溢出 ISR。

开启和重置只操作 TIM2 RCC 位，保留其他外设位；开启后读回作同步。初始化与每次取时最多 4096 次轮询，必须观察到真实 CNT 变化。循环次数仅限定失败等待，绝不充当时间。配置变化、停转或超过 INT32_MAX us 的差值均锁存失败，输出不变。重复初始化不重置 epoch 或清故障；重新上电/复位才清除。Stop 唤醒的现有 `board_buses_reinit_after_stop()` 明确作废 epoch，下一次 RECORD 走既有 APP_ERROR_CLOCK 路径，禁止继续伪连续记录。

TIM2 与 RCC 时钟树必须由此模块独占；不能被 ISR、调试脚本或未来 HAL 改写。每次调用间隔必须不超过 INT32_MAX us。HSI 是标称时间，温度、电压和校准误差需实测；该实现没有 RTC 补偿。**两次读取之间发生并恢复的短暂时钟停止、隐藏的 CNT 重写/复位、任意长停顿不能仅凭该计数器完整检测**，因此不能把寄存器检查解释为独立时钟监视器。真正 Stop 前后的连续时间需要独立 RTC/LPTIM 方案。

## 官方依据

2026-09-23 通过 web 工具实际读取以下 ST 官方资料；未新增 CMSIS/HAL 依赖：

- [STM32G031 数据手册 DS12992 Rev 4](https://www.st.com/resource/en/datasheet/stm32g031f8.pdf)，§3.16.2 / 表7：TIM2 为 32 位计数器、16 位预分频；§3.16.3：低功耗定时器的 Stop 工作条件。
- [ST stm32g031xx.h](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-g0/master/Include/stm32g031xx.h)：TIM2 地址、寄存器偏移、RCC 时钟/重置/睡眠位及 HSIDIV/SW/SWS/HPRE/PPRE 定义；TIM2EN/TIM2RST/TIM2SMEN 都是 bit0。
- [ST system_stm32g0xx.c](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-g0/master/Source/Templates/system_stm32g0xx.c)：HSI 标称 16 MHz，HSIDIV、AHB 分频计算以及实际频率容差说明。
- [ST LL TIM](https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/master/Inc/stm32g0xx_ll_tim.h)：CNT 读取、PSC+1 分频和更新事件装载规则。

尝试读取 RM0444 PDF 时 web 返回 Internal Error，未以“已读完整 RM”作为证据。实际依据为上列数据手册和 ST 官方 CMSIS/LL 源码。

## 检查及结果

仓库根目录执行：

```sh
python3 -m unittest discover -s firmware/host/tests -v
python3 -m unittest discover -s firmware/mcu/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/tim2/arm
/opt/homebrew/opt/llvm/bin/clang --analyze --target=arm-none-eabi -mcpu=cortex-m0plus -mthumb -std=c11 -ffreestanding -I firmware/mcu/include -I firmware/mcu/runtime/include firmware/mcu/src/board.c -o /tmp/tim2-board.plist
```

- 修改前 host 23/23（8.362s）；修改后 23/23（6.179s）。原故障闭合/APP_ERROR_CLOCK 回归仍通过。
- MCU 2/2（含现有 runtime 测试与新时基测试；1.346s）。TIM2 寄存器模型对 AWA/UW 分别测试初始化前失败、错误时钟源/分频、HSI 未就绪、未启动计数器、时基重入、无 IRQ/DMA、无关 RCC 位保留、跨 32 位回绕、过长间隔、各配置破坏及恢复后的错误锁存、停转、CNT 后退、Stop 唤醒后失败。
- 两变体所有 20 个 Cortex-M0+ 对象实际编译成功，`-Wall -Wextra -Werror`；独立解析 ELF 头确认 20 个为 ELF32 little-endian ARM relocatable。哈希清单 `validation/tim2/objects.json`。
- ARM clang 静态分析无诊断。完整命令/日志见 `validation/tim2/`。
- 未进行链接、硬件计时频率/抖动、调试冻结、Stop 功耗及连续性测量。模型不模拟真实 APB 总线、影子寄存器或振荡器。

修改 `src/board.c`、`include/board_revA2.h`；新增 `tests/tim2_timebase.c`、`tests/test_tim2.py`、本报告与证据。`app.c` 无需修改。修改前拥有范围的三个文件备份于 `validation/tim2_before/`，保留此前未提交改动。无新依赖、无安装、无提交。
