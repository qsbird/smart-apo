# 传感器 CTRL 上电写入（手册级）

与 `include/sensors.h`、`dump_decode.py` 的候选量程一致。没有 I2C/HAL 时这些字节**不会**被发到芯片。上电必须先读 WHO_AM_I，ID 不对则不要写 CTRL。

| 器件 | 地址 | 寄存器 | 阿波 | 智能水中 | 含义 |
|---|---|---|---|---|---|
| LSM6DSO | 0x6A（SA0=GND） | WHO_AM_I 0x0F | 读 0x6C | 同 | 识别 |
| LSM6DSO | 0x6A | CTRL1_XL 0x10 | `0x48` | `0x58` | ODR 104/208 Hz，FS ±4 g |
| LSM6DSO | 0x6A | CTRL2_G 0x11 | `0x44` | `0x54` | ODR 104/208 Hz，FS ±500 dps |
| LSM6DSO | 0x6A | CTRL3_C 0x12 | `0x44` | 同 | BDU=1，IF_INC=1，连读 OUT_TEMP_L 起 14 字节。H_LACTIVE=0，INT1 默认高有效推挽 |
| LSM6DSO | 0x6A | INT1_CTRL 0x0D | `0x03` | 同 | INT1_DRDY_XL\|INT1_DRDY_G，接到 MCU PA0 / EXTI0 上升沿。采样仍按时间调度，INT 不闸门读数 |
| LSM6DSO | 0x6A | OUT_TEMP_L 0x20 | 连读 14 B | 同 | 温度 256 LSB/°C（0=25°C），随后陀螺、加速度 little-endian |
| LPS28DFW | 0x5C | WHOAMI 0x0F | 读 0xB4 | 同 | 识别 |
| LPS28DFW | 0x5C | CTRL_REG2 0x11 | `0x08` | `0x48` | BDU=1；阿波 FS_MODE=0（1260 hPa，4096 LSB/hPa）；水中 FS_MODE=1（4060 hPa，2048 LSB/hPa）。15 m 约 2500 hPa，不能用 Mode 1 |
| LPS28DFW | 0x5C | CTRL_REG1 0x10 | `0x2C` | `0x3C` | DS13317 Table 19/20：ODR 50/100 Hz，AVG=64。先写 CTRL_REG2 再写 CTRL_REG1 |
| LPS28DFW | 0x5C | PRESS_OUT_XL 0x28 | 连读 5 B | 同 | 压力 24-bit LE + TEMP_OUT 100 LSB/°C（与样本 0.01°C 相同）。与 IMU 同时到点时用压力温度 |
| NAU7802 | 0x2A | 仅水中 | — | PU_CTRL `0x01`→`0x02`，读 PUR，再 `0x86` | V1.7 §9.1：复位、数字上电、内部 LDO。阿波 DNP，不要初始化 |
| NAU7802 | 0x2A | 仅水中 | — | CTRL1 `0x2F` | VLDO=3.0 V，PGA 128×（候选，梁标定前不当作 gf） |
| NAU7802 | 0x2A | 仅水中 | — | CTRL2 `0x70` | CRS=320 SPS，CH1 |
| NAU7802 | 0x2A | 仅水中 | — | PU_CTRL `0x96` | 置 CS 开始转换，随后 CTRL2=`0x74` 触发内部 offset 校准；限轮询等待 CALS 清零且 CAL_ERR=0，失败不置 strain_ok |

CS 已接 3V3，SDO/SA0 已接地，因此 IMU/压力只走 I2C，不要再配 SPI 模式。

NAU7802 每次读取先检查 PU_CTRL.CR(bit5)；新转换未就绪不置 STRAIN_OK。PUR/校准当前为有限轮询骨架，真实时间超时和板上等待仍未验证；内部 offset 校准不代替梁零点/增益标定。

W25Q256JV（SPI1，`/CS`=PA4）：探测 `0x9F` 期望 `EF 40 19`，再 `0x06` 写使能、`0xB7` 进 4 字节地址、页编程 `0x12`。编程失败时 RAM 页不丢、地址不前进。禁止擦除仍有未读航次的扇区。无 SPI 时 `flash_page_program()` 返回失败。

电池：R4 1 MΩ + R5 330 kΩ，PA1 12-bit ADC，`battery_mv = adc * 13300 / 4095`（VDDA=3.3 V）。无 ADC 时不填写、不为满电。
