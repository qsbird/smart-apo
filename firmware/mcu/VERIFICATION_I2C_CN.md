# STM32G031 I2C1 PB6/PB7 验证（2026-09-23）

已替换 I2C 桩为寄存器轮询后端，现有 LSM6DSO、LPS28DFW、NAU7802 驱动直接调用这些接口。模型和编译通过不等于器件应答或板上时序合格；没有最终 ELF、烧录、示波器或传感器成功声明。

## 实现契约

- 独占单主机 I2C1，PB6=SCL、PB7=SDA、AF6、开漏、低速GPIO、无内部上下拉，需要外部上拉。只修改这两个引脚字段、I2C1时钟/reset/CCIPR字段；保留其他GPIO/RCC位，不更改系统时钟树、remap、SWD、TIM2/SPI/UART/ADC实现。
- 仅接受已验证 HSI16 /1、AHB/APB /1；I2C1SEL=00选择PCLK。每次事务等待检查 RCC、微调、PE、TIMINGR、滤波/控制、GPIO配置，拒绝漂移。关闭从机地址、IRQ/DMA、SMBus超时；模拟滤波开、DNF=0。初始化局部reset I2C1。
- 参数地址为未左移的7位地址；写时SADD=addr7<<1、NBYTES=2、AUTOEND，逐次TXIS写寄存器号和实际值。读先NBYTES=1写寄存器号、不AUTOEND，TC后重复START读、AUTOEND；读取实际RXDR。支持1..255字节，不做RELOAD；当前驱动最大14字节。
- 成功要求STOPF且BUSY清零，随后清STOPCF/CR2。允许最后字节RXNE与STOPF同时出现。读用255字节局部暂存，整个事务成功才复制，任何失败不改调用者缓冲区；错误没有补零或伪造有效数据。增加的栈开销须在最终链接/实际栈水位验证时评估。
- NACK/BERR/ARLO/OVR/PECERR/TIMEOUT/ALERT均使当前事务失败。只有纯NACK且STOP已完成、BUSY清零、配置仍有效才保留总线就绪，因此缺装一个器件不阻止探测其他地址。无透明重试，部分写可能已生效。
- 硬错误、异常STOP、BUSY卡住、超时、配置改变均失效，需显式init/recover。只有本次已START且仍持有总线时请求STOP；ARLO不发STOP、不自动GPIO恢复，避免干扰其他主机。STOP收尾失败不递归重试；显式恢复才产生恢复时钟。与旧桩注释不同：不在任意超时后盲目产生GPIO脉冲。
- 正常事务等待及SCL拉伸有TIM2名义25ms与4096次双上限；STOP错误收尾最多4096次。循环上限可能早于25ms，是有限终止保证，未证明板上最坏执行时延或支持25ms拉伸。所有延时使用`board_time_us`，不以CPU空循环作微秒延时；依赖其时钟/回绕/Stop失效契约。
- 显式恢复关闭PE后释放PB6/PB7，开漏GPIO读取IDR确认SCL真的变高，才计6us高电平；低电平亦6us。SDA低时最多9个恢复脉冲，再在SCL低时拉低SDA、释放SCL并等拉伸结束、释放SDA产生STOP（STOP过程额外一个SCL低/高转换）。不把输出锁存“高”误当总线“高”。确认两线高才回AF6/PE；失败保持PE=0并释放开漏引脚，可能保持GPIO模式。
- 初始化也需要工作TIM2。现有Stop唤醒使TIM2时基失效，所以不能宣称Stop后I2C已恢复；需要完整低功耗时基设计后验证。并发ISR/DMA、其他主机及外部GPIO/RCC改写不在支持范围。

## TIMINGR依据及条件

`0x10A2272F`是本轮手算的保守标准模式候选，**不是CubeMX结果或RM0444表格的直接复制**。PRESC=1、SCLDEL=10、SDADEL=2、SCLH=39、SCLL=47。在16MHz时，tPRESC=125ns，数据建立延时1375ns、保持延时250ns，SCL高/低计数部分为5000/6000ns；同步、滤波、边沿会再增加周期，因此不是精确100kHz，名义常落在约80–90kHz范围。

计算依据为[ST AN4235的时序公式](https://www.st.com/resource/en/application_note/an4235-i2c-timing-configuration-tool-for-stm32f3xxxx-and-stm32f0xxxx-microcontrollers-stmicroelectronics.pdf)，以及[ST官方BSP的SDADEL/SCLDEL计算式](https://raw.githubusercontent.com/STMicroelectronics/stm32wba55g-dk1-bsp/main/stm32wba55g_discovery_bus.c)。AN4235针对F0/F3，BSP针对WBA，这里只引用相同TIMINGR字段的计算方法，不把其时钟树或示例常数当G031配置。

计算假设：SDA/SCL上升≤1000ns，下降≤300ns，模拟滤波50..260ns、DNF=0。G031滤波范围来自[DS12992 Rev4表69](https://www.st.com/resource/en/datasheet/stm32g031y8.pdf)。`validation/i2c/check_timing.py`额外检查15.2/16/16.8MHz（人为±5%计算裕量，不是HSI校准测量）：SCLDEL时间≥1250ns；SDADEL在`max(0,tf-50-3*tclk)`到`3450-tr-260-4*tclk`之间；高低计数自身已超过标准模式要求，最快总计数周期也超过10us。结果存`timing.json`。实际边沿、上拉/总线电容、电压温度与HSI误差须上板测量并按实测重新核算；不据此关闭硬件发布门禁。

寄存器地址、偏移和位域核读[ST G031 CMSIS头](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-g0/master/Include/stm32g031xx.h)；控制/清标志、PE关闭与滤波语义核读[ST G0 LL I2C头](https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/master/Inc/stm32g0xx_ll_i2c.h)，事务流程参考[ST G0 HAL I2C](https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/master/Src/stm32g0xx_hal_i2c.c)。[RM0444](https://www.st.com/resource/en/reference_manual/rm0444-stm32g0x1-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)正文提取未成功，不声称完整核读该手册。

## 验证及复现

```sh
python3 -m unittest discover -s firmware/host/tests -v
python3 -m unittest discover -s firmware/mcu/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/i2c/arm
/opt/homebrew/opt/llvm/bin/clang --analyze --target=arm-none-eabi -mcpu=cortex-m0plus -mthumb -std=c11 -ffreestanding -I firmware/mcu/include -I firmware/mcu/runtime/include firmware/mcu/src/board.c -o firmware/mcu/validation/i2c/board.plist
python3 firmware/mcu/validation/i2c/check_timing.py
```

Host 23/23；MCU原有5项加I2C共6/6，均覆盖AWA/UW。新模型具有地址白名单、CR2 START自清、TC/STOP和AUTOEND序列、TXDR消耗TXIS、RXDR清RXNE、ICR W1C、reset和GPIO BSRR/IDR分离等副作用，不是只固定返回成功位。覆盖1..14/255字节、真实接收图样、寄存器与地址编码、重复START、最终RXNE+STOP、时间回绕、NACK及各错误、TC/TXIS/STOP缺失、BUSY/时钟/微调/时序/时钟源错误、计时失败/停滞/期限超时、读失败输出不变、参数边界、拉伸与恢复成功/失败、无关字段保留。另测0x6A NACK后0x5C成功及NACK+STOP失败/BUSY未清锁存。模型不模拟电气边沿或证明芯片实际工作。

现有TIM2模型的Stop重初始化会调用新后端；只在`tests/tim2_timebase.c`添加I2C MMIO隔离hooks，保留原有TIM2断言，防止宿主访问真实外设地址。该适配不替代独立I2C模型。

本次实际可用的Homebrew LLVM/Clang 23.1.0以`-Wall -Wextra -Werror`生成两变体各10个ARM对象；`validation/i2c/objects.json`记录ELF32 ARM REL检查、SHA256及工具版本。静态分析无诊断。完整日志见同目录`host-tests.log`、`mcu-tests.log`、`arm-objects.log`、`static-analysis.log`。没有最终链接/运行时库验证。本轮未安装或切换工具；“20个对象”是构建产物数量。

修改范围：`src/board.c`仅I2C段、`include/board_revA2.h` I2C常数/契约、`tests/i2c_registers.c`/`test_i2c.py`、TIM2测试隔离、本报告和`validation/i2c/`。无新依赖、工具安装或提交。保留板上波形、所有器件WHOAMI/数据、传感器配置/采样率、低功耗恢复和最终ELF验证为未关闭项。
