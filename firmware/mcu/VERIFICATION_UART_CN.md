# STM32G031 USART2 TX 验证（2026-09-23）

USART2 TX 已替换为寄存器后端，UART v1 帧结构及 host 解码协议不变。**仅寄存器模型、宿主回归及 ARM 目标文件验证；没有最终 ELF、烧录或板上成功声明。**

## 行为边界

- GPIOA/USART2 时钟使能及 USART2 reset 只改对应 RCC 位；PA2/PA3 配 AF1、推挽、低速、无上下拉，保留 PA13/14 SWD、PA9/10 remap、SPI 及其他引脚。初始化不更改系统时钟树。
- 只接受 HSI16 开启并就绪、HSIDIV=/1、SW/SWS=HSISYS、AHB/APB=/1；保存并检查 ICSCR 微调。G031 USART2 使用 PCLK，不存在其他型号的 USART2SEL 配置。PRESC=/1、OVER8=0、BRR=139，标称约 115108 baud（相对115200约 -0.08%，另有 HSI 容差）。
- 8N1、仅 TE|UE，关闭 RX/FIFO/IRQ/DMA/流控。PA3 仍配置 AF1，但不提供收包或主机 ACK；避免无人读取 RDR 引起 ORE。未来双向协议必须另行实现 RX 消费和错误恢复。
- 初始化等待 TEACK/TXE/TC；每个字节写 TDR 前等待 TEACK/TXE，最后等待 TEACK/TC。每次最多256次轮询并复核时钟、BRR、控制寄存器、GPIO及RCC。次数是终止上限，不是校准微秒数；实物须测定是否足够覆盖整字节/初始化延时。
- PE/FE/NE/ORE、超时、配置变化和非法非空长度指针返回 -1，清 UE（时钟可访问时）并锁存失败，直到显式 init。init 通过 reset 放弃既有传输，不自动重试。初始化前 write 不碰 MMIO。len=0 仍检查就绪及 TC，可传 NULL。
- 返回0只表示最后停止位对应的 TC 已观察到，不能证明线缆完好、主机收到或持久化。返回-1可能已经发出帧前缀，甚至整帧；调用者不能将失败解释为无副作用。host CRC/同步和连续相同帧去重保持现状。重试需显式重新初始化并遵循既有记录级策略。
- 要求独占并串行调用；禁止 ISR/DMA 或其他代码修改相关配置。瞬态失钟后恢复、引脚电气故障、Stop期间经过的时间等不能据此检测；Stop后使用UART前需显式init，本次未实现Stop集成。

## 官方依据

实际读取的 ST 资料：

- [stm32g031xx.h](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-g0/master/Include/stm32g031xx.h)：地址、寄存器布局、TEACK/TXE/TC 及 RCC 位。
- [USART LL header](https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/master/Inc/stm32g0xx_ll_usart.h)：TDR 32位寄存器写入8位数据、状态定义与配置。
- [USART LL source](https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/master/Src/stm32g0xx_ll_usart.c)：没有 USART2SEL 的器件使用 PCLK，以及禁用状态配置和复位方式。
- [DS12992 Rev4](https://www.st.com/resource/en/datasheet/stm32g031f8.pdf) 表13：PA2/3 AF1；PA13/14 SWD。

RM0444 官方 PDF 请求返回 Internal Error，未声称完整读取参考手册。实现未引入 CMSIS/HAL 或新依赖。

## 验证与复现

仓库根目录：

```sh
python3 -m unittest discover -s firmware/host/tests -v
python3 -m unittest discover -s firmware/mcu/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/uart/arm
/opt/homebrew/opt/llvm/bin/clang --analyze --target=arm-none-eabi -mcpu=cortex-m0plus -mthumb -std=c11 -ffreestanding -I firmware/mcu/include -I firmware/mcu/runtime/include firmware/mcu/src/board.c -o firmware/mcu/validation/uart/board.plist
```

host 23/23，MCU 4/4（runtime、TIM2、SPI、UART；寄存器模型各跑AWA/UW）。UART模型使用地址白名单，真实模拟RCC reset、UE取消、TEACK延迟、单字节TDR与独立移位寄存器、TDR写清TXE/TC及最后停止位延迟。覆盖GPIO/RCC字段保留、非就绪调用、五种坏时钟、传输中时钟/微调改变、TXE/TC/TEACK卡住、四类错误位、配置破坏、部分/完整帧后失败及显式恢复。不是完整芯片或模拟电路仿真。现有TIM2/SPI测试没有调用UART初始化，不需要修改其hooks或实现。

20个Cortex-M0+对象经 `-Wall -Wextra -Werror` 构建；独立解析ELF头确认为ELF32 little-endian ARM REL，清单及SHA256在 `validation/uart/objects.json`。clang静态分析无诊断。日志：`validation/uart/{host-tests,mcu-tests,arm-objects}.log`；静态分析结果 `board.plist`。

修改：`src/board.c` 仅USART2段，`include/board_revA2.h` 新增API契约；新增 `tests/uart_registers.c`、`tests/test_uart.py` 和本报告。修改前备份 `validation/uart_before/`。未安装工具、增加依赖或提交。

尚需：最终链接器/compiler runtime；板上测PA2 idle/波特率/8N1/TC时序、长帧及长航次转储、错误与重初始化、SWD保持、实际线缆和主机重同步。I2C及其他桩不因此获得支持。
