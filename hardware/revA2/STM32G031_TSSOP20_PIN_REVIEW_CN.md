# STM32G031F8P6 TSSOP20 引脚复核

复核日期：2026-09-08。

## 结论

Rev.A1 自定义 MCU 符号把逻辑功能错误地按 1-20 顺序映射到了并不对应的物理脚。Rev.A2 已依据 ST DS12992 Rev 4 Figure 5 重建物理脚顺序；原有功能选择大部分可以保留，但必须使用下面的新物理脚号。

| 物理脚 | ST 封装脚 | Rev.A2 功能/网络 | 必要配置 |
|---:|---|---|---|
| 1 | PB7/PB8 | PB7 / I2C_SDA | I2C1 SDA AF6 |
| 2 | PB9/PC14-OSC32_IN | PC14 / LSE_IN | LSE 模式 |
| 3 | PC15-OSC32_OUT | PC15 / LSE_OUT | LSE 模式 |
| 4 | VDD/VDDA | 3V3 | 电源 |
| 5 | VSS/VSSA | GND | 地 |
| 6 | PF2-NRST | NRST | 保持复位功能 |
| 7 | PA0 | IMU_INT | GPIO/EXTI |
| 8 | PA1 | VBAT_SENSE | ADC 输入 |
| 9 | PA2 | UART_TX | USART2_TX AF1 |
| 10 | PA3 | UART_RX | USART2_RX AF1 |
| 11 | PA4 | FLASH_CS | GPIO 输出；外加 R12 10 kΩ 上拉 |
| 12 | PA5 | SPI_SCK | SPI1_SCK AF0 |
| 13 | PA6 | SPI_MISO | SPI1_MISO AF0 |
| 14 | PA7 | SPI_MOSI | SPI1_MOSI AF0 |
| 15 | PB0/PB1/PB2/PA8 | PB0 / LED_GATE | GPIO 输出 |
| 16 | PA11[PA9] | PA9 / REED_WAKE | `SYSCFG_CFGR1.PA11_RMP=1` 后作为 PA9 |
| 17 | PA12[PA10] | PA10 / STRAIN_DRDY | `SYSCFG_CFGR1.PA12_RMP=1` 后作为 PA10 |
| 18 | PA13 | SWDIO | SWD |
| 19 | PA15/PA14-BOOT0 | PA14 / SWCLK | SWD；检查 BOOT0 选项状态 |
| 20 | PB3/PB4/PB5/PB6 | PB6 / I2C_SCL | I2C1 SCL AF6 |

## 固件强制要求

- 初始化任何 PA9/PA10 外设或 EXTI 之前，先开启 SYSCFG 时钟并设置 `PA11_RMP`、`PA12_RMP`。
- CubeMX 中需先在 SYS 页面启用 PA11/PA12 到 PA9/PA10 的 remap，再分配相应功能。
- 调试阶段不得关闭 PA13/PA14 的 SWD 功能。
- LSE 启动失败必须有超时和内部时钟降级路径，避免设备无法启动。

## 官方依据

- ST DS12992 Rev 4，Figure 5 `STM32G031Fx TSSOP20 pinout`。
- ST RM0444 Rev 6，`SYSCFG_CFGR1` bit 3 `PA11_RMP`、bit 4 `PA12_RMP`。

本机当前未发现 STM32CubeMX，因此已完成数据手册/参考手册级复核，但 CubeMX 工程生成与实际编译验证仍是后续门槛。
