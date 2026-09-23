# Rev.A2 固件实际验证记录（2026-09-23）

状态：**代码骨架；宿主机 C 检查/模拟接口测试通过；ARM 可启动构建未完成；板上运行未验证。** 未生成可烧录发行包。

## 已修复

- `include/sensors.h` 的宏后多余 `*/` 导致 app/main/sensors 全部无法通过 C 预处理；已删除。
- `Makefile` 中 `CC ?=` 被 GNU make 内置 `CC=cc` 覆盖，原来误调用 Apple clang 并报 Cortex-M0+ 不支持。仅在默认来源时指定 ARM 编译器，仍尊重用户显式 CC。
- `include/board_revA2.h` / `src/board.c`：RCC APBENR2 地址由 `0x4002104C` 更正为 `0x40021040`；原地址是 APBSMENR1，不能完成预期的 SYSCFG/SPI1 时钟使能。实际指针复用头文件常量，减少重复。依据 [ST 官方 STM32G031 CMSIS 头文件 RCC_TypeDef](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-g0/master/Include/stm32g031xx.h)，APBENR2 offset=0x40，APBSMENR1 offset=0x4C（本次在线读取）。此文档校核不等于寄存器实测。
- `src/datalog.c`：JEDEC/读取失败拒写；重启检测到已有 APO2 航次则只读，未知/损坏头拒写。保留 RAM 页和被拒样本；禁止日志地址越过 32 MiB；append 在隐式刷新后再次检查容量，满盘拒绝 RAM 尾写入，由 app 保留未接受样本。`src/flash.c` 检查全页空白、WEL、写后读回；已写入完全相同数据的重试仅确认，半写页拒绝重新编程。不提供擦除/历史航次自动复用。
- `src/app.c`：新增 APP_ERROR 与粘滞错误位；init/append/flush/read 失败传播，日志异常停止采样。全航次按页检查样本 CRC 并转储，包含 RAM 尾和未成功 append 样本；UART 失败缓存同一记录重试。host 去除连续完全相同帧。移除前三个调度点伪造同步敲击标记。
- 新增 native C 模拟夹具 `tests/{log_lifecycle,log_capacity,flash_nor,app_errors,sensors_config}.c`，由无第三方依赖的 `firmware/host/tests/test_firmware_contract.py` 编译运行，保留原有未提交文件，不改 Rev.A1。

## 实际工具证据

完整命令/退出码/stdout/stderr：`validation/commands_20260923.json`。测试原始输出：`validation/native_tests_20260923.log`。

| 实际命令 | 结果及边界 |
|---|---|
| `python3 -m unittest discover -s firmware/host/tests -v` | 15 个测试通过；测试内部使用 clang 编译执行模拟接口，另对 8 个 C 源文件、两个装配变体运行 `-std=c11 -Wall -Wextra -Werror -fsyntax-only` |
| `make -C firmware/mcu` | exit 2：`arm-none-eabi-gcc` 不在 PATH；未声称 ARM 构建通过 |
| `python3 firmware/host/dump_decode.py firmware/host/example_data/uart_dump_fixture.bin -o firmware/mcu/validation/uart_fixture_raw.csv` | exit 0，解码 1 条现有夹具；另测试直接生成真实 C 打包帧，验证 Python 解码、负数、小端、外层 CRC 破损重同步及截断帧 |
| `clang --analyze ...`（具体 16 条见 JSON） | 全部退出 0；board.c 在两个变体各有 2 个 `core.FixedAddressDereference` 警告，为实际 MMIO 地址访问。其余无诊断。不能把 exit 0 写成零警告 |
| 默认 `python3 firmware/host/autotune.py ...` | exit 1，缺 numpy |
| App bundled Python 执行同一 autotune | exit 1，numpy 可用但缺 scipy；未安装新依赖，未改写现有示例结果 |

测试覆盖：UART C→Python 协议；Flash 越界先于 SPI 拒绝；Flash 探测/读取失败不写；满页失败不溢出、重试地址及数据保留；模拟 NOR 的重启存储逐字节不变、WEL 拒绝、半写/占用页拒写、写后读回、同数据响应丢失重试；跨部分页的全航次+RAM尾、样本CRC损坏；DUMP 同记录重试和重新进入、错误状态停止采样；不伪造同步事件；ST RCC 地址契约。没有在宿主机执行 board.c 的 MMIO 初始化。

引脚头文件与 `hardware/revA2/STM32G031_TSSOP20_PIN_REVIEW_CN.md` 的 20 脚表对应：PB6/PB7 AF6 I2C，PA2/PA3 AF1 USART2，PA5/6/7 AF0 SPI1，PA4 CS，PA9/10 remap 后磁簧/DRDY，PA13/14 保持 SWD。该结论是文件交叉检查；CubeMX/芯片验证仍开放。

## 剩余阻塞与后续优先级

1. **非可启动固件**：未找到 ARM 工具链；`/Applications` 未找到 CubeMX。缺 startup/vector、linker script、时钟树/HAL 或完整 LL 驱动。现 Makefile 即使补工具链也不构成经过验证的可启动映像。GPIO/总线/ADC/LSE/Stop 大多数函数仍只有注释与失败返回；禁止烧录骨架。
2. **日志保护已实现软件模拟，仍需实物验证**：保持原 APO2 16-byte header / 34-byte sample / FF 页填充；已有航次一律只读，缺可用空白页拒写，未提供多航次目录、用户确认擦除或自动续写。断电损坏样本会明确报错，不跳过伪装成功；复杂损坏的原始存储抢救尚未实现。完整空白页作为顺序日志终点，不扫描任意稀疏历史片段。当前方案优先保护存量数据，不宣称断电自动恢复全部记录。
3. **全航次读取/错误传播已通过模拟验证**：增加 READ4=0x13、逐页 CRC、RAM 尾、UART 单记录重试、APP_ERROR/错误位。仍未传输航次头/设备ID/量程元数据；主机需显式选择 awa/uw。无主机 ACK、持久化确认或端到端完成帧，不把 UART 成功等同于主机已保存。实际 SPI/UART 尚无 HAL 驱动。READ4 依据 [Winbond W25Q256JV Rev.Q §8.2.11（TI 托管原厂 PDF）](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/908/W25Q256JV-SPI-RevQ-02072025-Plus.pdf)：始终使用 4 字节地址；BUSY 时不读取，代码先轮询。
4. **定时与同步（软件未完成）**：main 使用循环自增伪时间；sensors deadline 比较没有 uint32 回绕处理（约 71.6 min），1 ms 步长不保证 104/208/320 Hz。尚无真实敲击检测/事件输入；标志保持未置位。
5. **主机数据安全门槛已实现，重采样未实现**：raw 保留原始计数/flags；`--autotune` 逐条拒绝缺测，要求 AWA IMU/PRESS 有效、UW 再加 STRAIN；拒绝 AWA 携带 strain-valid、样本内 CRC 错误、非递增时间戳及 sequence 缺口/乱序（允许正常 16 位回绕）。外 CRC 丢弃中间帧后不会静默输出缺失航次。UW 必须提供有限非零梁标定斜率及显式有限零点，不能把 counts 命名 gf。拒绝时不覆盖输出 CSV。当前异步 MCU 日志需要明确定义重采样后才可进入调参；时间戳回绕展开、头部变体/量程自动验证仍未实现。
6. **传感器寄存器补充模拟验证**：依据 [ST 官方 lsm6dso_reg.h](https://raw.githubusercontent.com/STMicroelectronics/lsm6dso-pid/master/lsm6dso_reg.h) 将 CTRL3_C 配成 BDU|IF_INC=`0x44`；依据 [ST 官方 lsm6dso_reg.c](https://raw.githubusercontent.com/STMicroelectronics/lsm6dso-pid/master/lsm6dso_reg.c) 修正 host 敏感度为 0.000122 g/LSB 和 0.0175 dps/LSB（原 500/32768 错误）。依据 [Nuvoton NAU7802 V1.7 原厂表](https://www.nuvoton.com/resource-files/NAU7802%20Data%20Sheet%20V1.7.pdf) 增加 PUR 有限轮询、CTRL2.CALS 内部 offset 校准并检查 CAL_ERR、PU_CTRL.CR 门控新转换。两变体模拟测试覆盖 BDU 实际写值、AWA 不访问 DNP NAU、校准失败/超时/未就绪不置有效位。NAU 和 Flash 仍使用限次数轮询，需真实毫秒时基；没有板上回读证据。内部 offset 不代表 gf 梁标定通过。
7. **设备条件**：需样机、调试器、串口/逻辑分析仪，验证 remap、总线、寄存器回读、Flash 完整性、LSE 失败降级、磁簧唤醒、ADC、高阻分压采样误差和梁标定。当前没有任何板上验证通过结论。
8. **主机调参运行依赖**：已检查 `.pydeps`，含 numpy 2.5.2 的 cp312 扩展、不含 scipy；默认 Python3.14 ABI 不兼容，但 App bundled Python3.12 实际可导入该 numpy。系统 Python3.9、KiCad Python3.9、bundled Python3.12 的 scipy 均缺失。完整探测见 `validation/python_dependencies_20260923.json`；本次未安装依赖，未运行通过 autotune，未更新候选参数，仍需 scipy 环境和真实独立航次。

不影响硬件放行状态：保持 NOT_FAB_RELEASED，由主任务官方 ERC/DRC 决定 PCB 数字检查结果。

末轮独立审查修复证据：`log_capacity.c` 实际模拟填满 131072 页/917504 条记录，额外追加触发最终页刷新后被拒绝，重复追加仍拒绝且不增加编程次数。主机回归人为破坏中间帧外 CRC，raw 恢复序号 0、2，严格调参拒绝该缺口，并单独证明 65535→0 连续回绕可通过。
