# STM32G031 GPIO / 磁簧轮询验证（2026-09-23）

已实现真实 GPIO 寄存器初始化和 IDR 读取；磁簧连续闭合用 TIM2 微秒计时并轮询 EXTI9 释放边沿。这里只证明宿主状态模型、回归和 ARM 目标文件通过；没有最终 ELF、烧录、实物电平/功耗或 Stop 唤醒成功声明。

## 实现契约

- `board_enable_syscfg` 仅置 RCC_APBENR2 SYSCFGEN 并读回；`board_apply_pa9_pa10_remap` 必须看到该时钟使能才置 CFGR1 的 PA11_RMP/PA12_RMP。其余 RCC/SYSCFG 位保留。
- `board_init_gpio` 仅使能 GPIOA/B。先写 BSRR 将 PA4 输出锁存器置高、PB0 置低，再设置推挽、低速、无上下拉、输出模式。先预载避免由输入切换至输出时误选 FLASH 或点亮 LED。输出初始化即使 remap 缺失仍先执行；PA0/9/10 的输入配置必须在 remap 成功后进行，外部已有驱动/上拉，不加内部拉电阻。所有寄存器按目标字段读改写，保留 SWD PA13/14、AFR、其他 GPIO 和 RCC 位。
- PA9 读取实际 IDR，低为闭合；PA0 读取实际 IDR，高为 IMU pending。输入 API 检查 GPIO 时钟、SYSCFG/remap、输入模式和 pull 配置，未初始化/漂移返回假。PA10 配置成输入，但本轮不新增 strain IRQ API。
- `board_reed_exti_setup` 独占 EXTI9：选择 PA、仅上升沿（释放）触发，IMR9/EMR9 都屏蔽，以 W1C 清本线 pending，保留其他线路。它只是硬件释放边沿锁存器的轮询初始化，不启用 NVIC 或 ISR，不构成 Stop 唤醒。现有 startup 的 EXTI handler 仍是 Default_Handler 弱别名，不能启用中断。
- `board_reed_held_for_sleep` 从第一次闭合观察开始计时，至少标称 1,500,000 us 才为真。IDR 观察到松开会清零；即使两次调用之间开闭，EXTI9 上升 pending 也会清零，下一次闭合调用重新开始计时。清 pending 后不复用清除前的时间戳，避免将释放前时间计入新的闭合。计时后再次查 IDR/pending，避免调用内松开被认作合格。时钟 API 失败、时间停滞/反向或间隔超过 INT32_MAX、配置失效也清零。32 位计时回绕和长闭合跨多次回绕均受模型覆盖。必须至少每 INT32_MAX us 调用一次；无并发 GPIO/EXTI/RCC 写者或其他 pending 清除者。
- `board_imu_int_exti_setup` 明确保留空兼容入口；IMU 是即时电平轮询，短脉冲可能漏检，不是事件队列。既有基于时间的传感器采样路径仍需保留。LED 仅有启动 PB0 低电平，闪烁控制仍未实现。

1.5 秒基于现有 TIM2/HSI 的标称时间及其容差，并非独立校准的绝对时长。EXTI 捕获只能保证满足芯片电气/脉宽要求且被硬件捕获的边沿；无法证明任意短毛刺都捕获。模式配置瞬时变更后在调用间恢复、其他代码清 pending 等情况不在独占契约内。物理拉电阻、焊接、逻辑阈值、机械抖动与长期时基精度须板上确认。

## 官方依据（实际读取）

- [ST STM32G031 CMSIS 器件头](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-g0/master/Include/stm32g031xx.h)：GPIO/EXTI 地址和偏移，SYSCFG remap bit3/4，EXTICR3 EXTI9 三位字段在 bit8，RPR/FPR 与 IMR/EMR。
- [ST GPIO LL](https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/master/Inc/stm32g0xx_ll_gpio.h)：输入/输出模式、IDR 输入读取、BSRR 原子置位/复位。
- [ST EXTI LL](https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/master/Inc/stm32g0xx_ll_exti.h)：独立 trigger、interrupt/event mask、rising/falling pending 和 W1C 清除。未声称完整核读 RM0444。

## 验证证据与复现

```sh
python3 -m unittest discover -s firmware/host/tests -v
python3 -m unittest discover -s firmware/mcu/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/gpio/arm
/opt/homebrew/opt/llvm/bin/clang --analyze --target=arm-none-eabi -mcpu=cortex-m0plus -mthumb -std=c11 -ffreestanding -I firmware/mcu/include -I firmware/mcu/runtime/include firmware/mcu/src/board.c -o firmware/mcu/validation/gpio/board.plist
```

host 23/23，MCU 7/7（原六项加 GPIO）通过。GPIO 模型各编译运行 AWA/UW 两变体，真实后端经宏 hook 操作独立状态模型；地址白名单拒绝未建模访问，BSRR 改输出锁存器、pending 为 W1C。断言 latch-before-mode、SYSCFG-before-remap、remap-before-input、GPIO/SWD 与 EXTI 非目标位保留、低有效/高有效 IDR、阈值前一微秒/正好阈值、两次轮询间释放、调用内释放、计时回绕、多次完整计数周期。注入 GPIO 时钟使能写丢失、remap 写丢失、MODER 写丢失、计时失败/停滞/反向及七类配置漂移。没有用固定成功返回模拟硬件行为。

LLVM AWA/UW 各 10 个 ARM 对象通过 `-Wall -Wextra -Werror`，`validation/gpio/objects.json` 记录各对象 ELF32 little-endian ARM REL 检查及 SHA256；静态分析无诊断。日志见 `validation/gpio/{host-tests,mcu-tests,arm-objects,static-analysis}.log`。没有安装依赖或提交。

修改范围：`src/board.c` 的 GPIO/SYSCFG/remap/磁簧/IMU 函数及局部 helpers；`include/board_revA2.h` GPIO 契约；`tests/gpio_registers.c`、`tests/test_gpio.py`；本报告和 `validation/gpio/`。未改 TIM2/SPI/UART/ADC/I2C 生产后端。分压硬件与换算由同任务其他工作流处理，不属于本 GPIO 验证结论。
