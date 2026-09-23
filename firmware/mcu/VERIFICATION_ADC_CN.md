> 启动保护已补充：TIM2开机epoch前100ms拒绝采样、不阻塞、不改输出。BOM增加C14容差≤20%设计条件；RC/温度/时钟裕量计算见 `validation/revA2_divider/consistency.json` 的 `startup_RC`。模型覆盖门槛前后与后续回绕；不是运行中电压阶跃/实物精度验证。

# STM32G031 PA1 ADC1_IN1 验证（2026-09-23）

已实现真实寄存器单次采样后端；返回实际 ADC_DR 的 12 位原始码。仅模型、宿主回归和 ARM 目标文件通过；**没有最终 ELF、烧录或板上成功声明，分压阻抗已作设计修正，但电池毫伏精度尚未实测成立。**

## 实现与边界

- PA1 改为模拟、无上下拉；只读改写 GPIOA MODER/PUPDR 中 PA1 字段。SWD PA13/14、其他GPIO、remap、TIM2/SPI/UART/I2C实现均未改动。
- 每次读独占 ADC1：使能时钟、ADC局部reset、禁IRQ/DMA/连续/外部触发/过采样，固定序列仅IN1、12位右对齐。仅接受HSI16 /1、AHB/APB /1，并检查HSIRDY及微调不变；同步HCLK/4，标称ADC 4 MHz。不改变系统时钟树或异步ADC时钟选择。
- 使用现有 `board_time_us` 测量稳压器启动30 us（官方要求20 us，留HSI与整数计时裕量），校准完成后2 us（官方要求2 ADC周期）。TIM2须先经 `board_start_clocks` 初始化；时基不可用、停止或Stop唤醒后失败，不以空循环伪造延时。TIM2的HSI与时间契约同时适用。
- 等待CHSELR更新CCRDY；启动ADCAL，等待ADCAL清零且EOCAL置位，再清陈旧标志，设置ADEN，等待ADRDY，软件ADSTART。等待EOC和EOS同时成立、ADSTART结束后才读DR。拒绝OVR、配置/时钟漂移及大于4095的DR；任何失败不改调用者输出。NULL立即失败。
- 每段轮询最多4096次，延时段也有相同次数上限；这是终止保证，不是精确墙钟timeout。成功和失败都仅reset ADC取消残留操作/关闭模拟稳压器；下一次调用必须重新校准，没有跨Stop沿用就绪状态。ADC时钟保持使能。要求串行独占ADC，无ISR/DMA/并发RCC或GPIO写者。
- 最大160.5周期采样，在4 MHz下标称40.125 us；12位转换另需12.5周期。返回0表示观察到硬件转换完成和格式正确，不表示模拟误差合格，也不表示电池电压已校准。

## 模拟硬件阻塞条件

初始R4=1 MΩ、R5=330 kΩ，等效源阻抗约248.1 kΩ，超出DS12992 Rev4表59的50 kΩ条件。后续已改为R4=180 kΩ、R5=60.4 kΩ、1%，最坏Rth=45.677 kΩ，关闭该阻抗数值超限；其余误差没有因此验证通过。分压在4.2 V下静态电流17.471 µA，仅此支路30天约12.579 mAh（恒压假设，不是整机续航）。

固件名义换算现为 `adc * 132220 / 41223`，4095码中间乘积不溢出32位。新增宿主机双变体测试逐一检查4096个码与独立物理分压有理数结果，并验证超量程钳位。跨文件证据见 `validation/revA2_divider/consistency.json`。C14名义100nF与新Rth时间常数4.522ms，全阶跃至半个12位LSB约40.75ms；电容偏压/容差、输入漏电、参考电压、上电建立与温度仍须验证，最长ADC采样时间不能代替这些检查。

既有 `board_vbat_mv_from_adc` 仍按VREF+=3.3 V及名义分压比计算。TSSOP20参考连接需按封装电源核对并测量实际VDDA/VREF+；本实现不读取VREFINT校正，不提供12位绝对电压精度承诺。PA1必须始终处于VSSA..VREF+输入范围，检查掉电时电池分压反灌、输入漏电、去耦及建立时间。未测板上ADC码、精度、功耗、启动延迟或SWD保持。

## 官方依据（实际读取）

- [ST STM32G031 CMSIS器件头](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-g0/master/Include/stm32g031xx.h)：ADC地址0x40012400、寄存器偏移、ADCEN/ADCRST位20及状态/控制字段。
- [ST ADC LL头](https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/master/Inc/stm32g0xx_ll_adc.h)：同步HCLK/4、160.5周期、CCRDY要求、20 us稳压启动、校准后2 ADC周期及CR命令位语义。
- [ST ADC HAL实现](https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/master/Src/stm32g0xx_hal_adc.c)：核心/转换时钟、单次采样流程及ADC局部reset清理。
- [DS12992 Rev4，2025-06](https://www.st.com/resource/en/datasheet/stm32g031f8.pdf)：引脚/封装连接、表59/60模拟输入条件。未声称完整核读RM0444。

## 验证与复现

从仓库根目录运行：

```sh
python3 -m unittest discover -s firmware/host/tests -v
python3 -m unittest discover -s firmware/mcu/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/adc/arm
/opt/homebrew/opt/llvm/bin/clang --analyze --target=arm-none-eabi -mcpu=cortex-m0plus -mthumb -std=c11 -ffreestanding -I firmware/mcu/include -I firmware/mcu/runtime/include firmware/mcu/src/board.c -o firmware/mcu/validation/adc/board.plist
```

host 23/23；MCU 5/5（原有runtime/TIM2/SPI/UART四项加ADC），寄存器模型各跑AWA/UW。ADC模型地址白名单，W1C、reset、校准命令完成、ADEN/ADSTART、DR读清EOC；断言稳压和校准后最小延时、校准先于转换、端点0/4095及中间码、重复调用重校准、TIM2回绕、GPIO/RCC非目标位保留。注入校准卡住、ADRDY缺失、转换超时、OVR、时钟丢失、格式改变、微调漂移、CCRDY缺失、计时失败/停滞、DR越界、ADSTART卡住、EOCAL缺失、EOS缺失、ADSTP异常15类故障；均不改输出且下一次显式调用重新初始化可恢复。另测5类初始时钟错误与NULL。

LLVM AWA/UW各10个对象，经 `-Wall -Wextra -Werror`。`validation/adc/objects.json` 保存ELF32 little-endian ARM REL检查与SHA256；静态分析无诊断。日志为 `validation/adc/{host-tests,mcu-tests,arm-objects,static-analysis}.log` 和 `board.plist`。该模型不能替代真实ADC数字时序/模拟电路仿真，也不能证明板上轮询余量。

修改：`src/board.c` ADC函数与专用helpers、`include/board_revA2.h` ADC契约、`tests/adc_registers.c`、`tests/test_adc.py`、本报告及 `validation/adc/`。未加依赖、安装工具或提交。最终链接器/compiler runtime、阻抗数值已修正；参考电压、静态电流预算及实物验证仍未完成。
