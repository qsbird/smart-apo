# STM32G031 SPI1 / PA4 软件片选验证（2026-09-23）

已用真实 MMIO 实现 SPI1，取代发送/接收/片选失败桩。**仅通过寄存器模型及 ARM 目标文件编译；未链接最终固件、未烧录、未进行板上验证。** TIM2 生产代码保持不变；I2C、UART 等未实现部分不因此获得硬件支持。

## 行为及边界

- PA4 先通过 BSRR 置高，再配置推挽输出，最后开启 SPI；PA5/6/7 AF0。仅修改对应 GPIO 字段和 GPIOA/SPI1 RCC 位，保留 SWD PA13/14、其他引脚及 SYSCFG remap。
- 严格检查 HSI 开启/就绪、HSIDIV=/1、SW/SWS=HSISYS、AHB/APB=/1，不修改时钟树。16 MHz PCLK 配 BR=/16，得到标称 1 MHz SCK；每次轮询检查时钟和微调值及关键外设配置。HSI 容差仍然存在。
- Mode 0、主机、MSB first、软件 NSS（SSM/SSI），全双工；DS=7、FRXTH=1，DR 只通过 volatile uint8_t 读写，避免 16 位访问打包出额外时钟。TX 每字节读取并丢弃收到的数据；RX 发 0xFF dummy。
- 每个 TXE、RXNE、BSY 等待最多 256 次；次数不是校准时间。CS 释放前等待 TXE 且 BSY/RXNE 清零，跨 tx/rx 调用保持片选。调用者必须串行访问；不支持 ISR/DMA 并发，也不允许其他模块更改 SPI1/PA4..7。
- OVR/MODF/FRE、时钟变化、无效指针及超时返回 -1，释放片选并锁存失败。通过 DR→SR→CR1 序列处理故障并关闭 SPE；下次显式 init 的 RCC reset 丢弃残余 FIFO。重新初始化会终止既有事务，不透明重试。
- 失败前发送的字节可能已经影响 flash；接收缓冲区可能保留有效前缀。失败不等于没有副作用，不得将部分数据当完整事务。初始化前调用保持失败闭合，不触碰 MMIO；已初始化后的失败会释放 CS。
- Stop 唤醒仍调用 SPI init，但不会恢复 TIM2 epoch；现有时基错误策略保持原样。GPIO/RCC 被并发修改、引脚硬件故障或整机失钟不能由软件保证恢复。

## 官方依据

本次实际读取：

- [ST CMSIS stm32g031xx.h](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-g0/master/Include/stm32g031xx.h)：GPIOA、SPI1、RCC 地址、寄存器布局和位定义。
- [ST LL SPI](https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/master/Inc/stm32g0xx_ll_spi.h)：ReceiveData8 / TransmitData8 的字节访问、OVR 的 DR→SR 清除、MODF 的 SR→CR1 清除，以及 BSY 行为。
- [ST DS12992 Rev 4](https://www.st.com/resource/en/datasheet/stm32g031f8.pdf)：引脚复用表、HSI16 与 SPI 外设。
- [ST 系统时钟源码](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-g0/master/Source/Templates/system_stm32g0xx.c)：HSI 标称频率和时钟分频计算。

[RM0444](https://www.st.com/resource/en/reference_manual/rm0444-stm32g0x1-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) 本次 web 请求返回 Internal Error；未声称读取完整 RM。实现依据为上面的官方器件头文件、LL 源码和数据手册；没有引入 CMSIS/HAL 依赖。

## 实际验证命令及证据

从仓库根目录执行：

```sh
python3 -m unittest discover -s firmware/host/tests -v
python3 -m unittest discover -s firmware/mcu/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/spi/arm
/opt/homebrew/opt/llvm/bin/clang --analyze --target=arm-none-eabi -mcpu=cortex-m0plus -mthumb -std=c11 -ffreestanding -I firmware/mcu/include -I firmware/mcu/runtime/include firmware/mcu/src/board.c -o firmware/mcu/validation/spi/board.plist
```

Host 23/23，MCU 3/3（runtime、TIM2、新增 SPI，每个寄存器模型运行 AWA/UW 两变体）。SPI 模型模拟延迟 TX/RX 状态、接收 FIFO 消耗、尾部 BSY、软件 CS、电路配置顺序、8 位 DR 限制、RCC reset 副作用；注入 TXE/RXNE/BSY 卡住、OVR/MODF/FRE、错误时钟、配置破坏、空指针、部分 RX、重初始化。测试验证无关 GPIO/RCC 字段保留。它不是完整 STM32 仿真，不证明引脚波形或实际总线行为。

20 个 Cortex-M0+ 对象使用 `-Wall -Wextra -Werror` 编译成功，独立解析 ELF 头确认 ELF32 little-endian ARM；哈希清单 `validation/spi/objects.json`。clang 静态分析无诊断。完整日志 `validation/spi/{host-tests,mcu-tests,arm-objects}.log`。

修改范围：`src/board.c`、`include/board_revA2.h`；新增 `tests/spi_registers.c`、`tests/test_spi.py`、本报告。`tests/tim2_timebase.c` 只加入惰性 SPI hooks，使其 Stop 测试不会访问宿主物理地址，保留原断言。修改前文件备份 `validation/spi_before/`。没有安装工具、增加依赖、提交或宣称最终 ELF 成功。

尚需硬件：逻辑分析仪确认 CS 启动与错误释放、SCK=Mode0/约 1 MHz、每字节恰好 8 个脉冲、MISO/MOSI 与电压/负载下的边沿；实际 JEDEC ID、读状态/页编程/读回、断开 flash、总线故障、Stop 后重新初始化和 SWD 保持。GNU 工具链和最终链接由独立授权/验证流程处理。
