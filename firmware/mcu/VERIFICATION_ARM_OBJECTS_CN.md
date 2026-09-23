# ARM 构建基础验证（2026-09-23）

## 结论与状态边界

已从“仅宿主语法/模拟回归”推进到 **AWA/UW 两变体真实 Cortex-M0+ ARM 目标文件可编译**。每变体 10 个 ELF32 little-endian `ET_REL` / `EM_ARM` 文件，共 20 个；`-Wall -Wextra -Werror` 编译退出 0。**未产出已链接固件 ELF，不可烧录，不是发行固件，不代表 HAL 或板上运行通过。**

已有 Clang 23.1.0 可用；PATH 无 arm-none-eabi-gcc、arm-none-eabi-ld、ld.lld、rust-lld、rustc、zig。扫描 `/Applications`、`/Library/Developer`、`/usr/local`、`/opt/homebrew`、`~/.codex` 未找到相应 ELF linker 或 ARM compiler-rt/libgcc；`~/.rustup` 不存在。未安装依赖。

## 本次文件与设计

- `Makefile`：保留默认 GNU ARM 编译入口，新增显式 LLVM cross-compile、两变体独立输出、object-only 目标、依赖跟踪、启动/链接基础。原文件备份 `validation/arm_20260923/Makefile.before`。
- `runtime/include/string.h` / `runtime/string.c`：当前源码所需 memcpy/memset/memcmp 的真实逐字节实现，使用编译器提供的 `stddef.h`，无假 typedef、无空实现；`-fno-builtin` 防止编译器将自身循环重新转成库调用。
- `runtime/startup.c`：独立实现 .data 复制、.bss 清零、进入 main、意外中断默认停驻；47 项向量顺序对应 ST G031 模板。只保留 reset 时钟状态，不声称替代 SystemInit/HAL，不支持 C++ 静态构造。
- `runtime/stm32g031f8.ld`：Flash 0x08000000/64 KiB，RAM 0x20000000/8 KiB，MSP 候选 0x20002000；保留 2 KiB 栈与向量大小断言。**因 linker 不存在，地址放置、容量断言、load/run 地址及栈预算尚未通过实际链接验证。**
- `tests/test_runtime.py`：宿主执行真实 string runtime，覆盖零长度、1/3/4/7/34/255/256/513 字节、非对齐地址、目标前后 guard、填充截断和 unsigned 比较。1 项参数化回归通过；不是 MCU 指令运行测试。
- `tests/verify_arm_objects.py`：读取每个目标文件 ELF header 并用 llvm-nm 核对跨目标文件符号；防止把宿主 object 或未解析依赖称为发行 ELF。

未修改既有 `src/`、`include/`、host 或传感器算法。

## 实际命令与证据

在仓库根目录运行：

```sh
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang
python3 firmware/mcu/tests/verify_arm_objects.py /opt/homebrew/opt/llvm/bin/llvm-nm
python3 -m unittest discover -s firmware/mcu/tests -v
make -C firmware/mcu all CC=/opt/homebrew/opt/llvm/bin/clang VARIANT=0
make -C firmware/mcu all CC=/opt/homebrew/opt/llvm/bin/clang VARIANT=1
```

前三项退出 0；后两项退出 2，实际报错 `invalid linker name in argument '-fuse-ld=lld'`。日志保存在 `validation/arm_20260923/`：`build-objects.log`、`object-audit.json`、`runtime-tests.log`、`link-variant0.log`、`link-variant1.log`。

`llvm-readelf -h/-S/-A/-s` 检查全部 20 个目标文件，完整结果分别为 `elf-headers.txt`、`sections.txt`、`attributes.txt`、`symbols.txt`。startup 的 `.isr_vector` 长度 0xBC（188 字节）、对齐 256；`vector-relocations.txt` 显示首项 `_estack`、第二项 Thumb `Reset_Handler`，EXTI0_1/EXTI4_15/SysTick 等顺序对应官方表。目标文件中这些是重定位关系，**不是已确认的最终向量地址**。

用 llvm-nm 将所有对象定义符号与引用符号做集合核对，两个变体残留完全相同：

- 编译器运行时：`__aeabi_uidiv`、`__aeabi_lmul`、`__aeabi_uldivmod`。
- linker 应提供的边界：`_ebss`、`_edata`、`_estack`、`_sbss`、`_sdata`、`_sidata`。

memcpy/memset/memcmp 已由本项目 runtime 定义，未用虚假 stub 隐藏符号。Arithmetic AEABI 没有自行伪造；需对应 ARM compiler-rt 或 libgcc。只有 linker 仍不足以消除这一阻断。

## 官方依据

- [ST DS12992 Rev 4](https://www.st.com/resource/en/datasheet/stm32g031k8.pdf)：STM32G031F8 的 64 KiB Flash、8 KiB SRAM。
- [ST CMSIS G031 设备头](https://github.com/STMicroelectronics/cmsis-device-g0/blob/master/Include/stm32g031xx.h)：FLASH_BASE/SRAM_BASE，内存地址。
- [ST G031 GCC startup](https://github.com/STMicroelectronics/cmsis-device-g0/blob/master/Source/Templates/gcc/startup_stm32g031xx.s)：异常/IRQ 顺序与保留槽。本地未复制 ST 代码，仅按硬件表独立实现。

## 尚未关闭

1. 提供 ARM ELF linker 及适配 Cortex-M0+ 的 compiler runtime 后，实际链接两个变体，再验证 entry、vector、LOAD sections、Flash/RAM/栈余量和零 undefined。
2. CubeMX/官方时钟配置、完整 GPIO/总线/ADC/时基/Stop 驱动仍缺。当前 `board_time_us()` 失败闭合，不能记录真实采样。
3. 没有模拟器/实物上的复位、异常入口、栈深度、外设通信或 Flash 运行证据；不得把 object 编译改写成“可启动”或“板上运行通过”。
