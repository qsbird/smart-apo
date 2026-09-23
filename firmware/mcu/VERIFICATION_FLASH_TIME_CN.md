# Flash BUSY 实时时限验证（2026-09-23）

已移除32次状态轮询作为页编程超时的做法，改用现有 TIM2 `board_time_us()` 的5000µs预算；连续4096次时间不前进终止，属于故障防停滞上限。未增加依赖、提交、链接最终ELF或烧录；以下不是板上成功证明。

## 原厂依据

实际下载的 [Winbond W25Q256JV SPI Rev R PDF](https://www.winbond.com/resource-files/W25Q256JV%20SPI%20RevR%2005042026%20Plus.pdf)，内页发布日期 May 6, 2026，§9.7 印刷页84（PDF第85页）：tPP典型0.4ms、最大3ms。5000µs预算包含2000µs裕量，仅服务页编程等待，不覆盖扇区/整片擦除。不能将别的版本或其他料号参数混用。

原始PDF及该页文本保存在 `validation/flash_time/W25Q256JV_RevR.pdf`、`datasheet-timing.txt`。下载链起于 Winbond 官方文档库的 W25Q256JV SPI Data Sheet，下载页解析出的resource-files地址即上述链接。

## 修复及边界

- 每次读状态都结束CS事务；等待计时包含SPI状态读取时间。首次已ready允许只读恢复，即使TIM2无效；首次BUSY必须有有效时基才能继续，不以CPU循环假装微秒。
- 一旦观察BUSY，后续状态ready也需有效时间，超过5000µs不接受ready。恰在5000µs观察ready可成功，恰在5000µs仍BUSY失败。无符号时间差支持一次32位自然回绕；倒退或大跳变失败。
- 真正PP之前采集时基、WREN、验证WEL，再采集时基并验证实际进展与预算。无时基或停滞不得授权新写。返回0仍要求读回一致；已经匹配的数据可幂等确认，无需重新PP。
- 继续拒绝已占/半写页，没有隐藏program重试。失败可能已编程，调用者不能把失败当作未发生写入；显式重试先读回，半写页仍拒绝。
- CS断言失败也调用释放；传输/状态读取/时间故障路径均结束事务。物理CS损坏不可能由软件证明释放，测试证明的是release调用及模型中的非选中状态。
- 依赖SPI与TIM2 API自身的有界失败、独占同步调用。时间预算不是线程调度/异常中断下的硬实时保证，长暂停或坏时间戳会保守失败。停滞上限不是正常页编程期限。

## 先复现，再验证

修改前快照在 `validation/flash_time/baseline/`。`baseline/flash_nor_reproduction.c` 建立状态模型：每次RDSR推进10µs，PP保持BUSY 1000µs；原32轮代码在合法1ms编程尚未结束时失败。`before.log` 保存该成功预期断言的失败（exit=-6）。修复后同一情形完成100轮以上状态查询并读回成功。

专用 `tests/flash_time_cases.h` 由现有 `flash_nor.c` 运行，覆盖3ms、4990/5000/5010µs、BUSY后6000µs才采到ready拒绝、UINT32回绕、首次/等待中时基失败、倒退、永久BUSY、停滞、SPI错误、CS失败、PP后失时基以及显式重试只读确认。原有WEL拒绝、NOR按位写、读回失配、断写、已占页、重复确认断言保留。新增ready且无TIM2可读、BUSY且无TIM2失败、无TIM2不发PP断言。

验证命令（仓库根）：

```sh
python3 -m unittest discover -s firmware/host/tests -v
python3 -m unittest discover -s firmware/mcu/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/flash_time/arm
```

host 23/23、MCU 8/8通过。20个AWA/UW Cortex-M0+目标对象在 `-Wall -Wextra -Werror` 下编译，并独立检查ELF32 little-endian ARM REL头、保存SHA256；LLVM 23.1现有工具链，无安装。Flash两个变体clang静态分析均无诊断。具体命令、日志和对象清单为 `validation/flash_time/{host-tests.log,mcu-tests.log,arm-objects.log,static-analysis.json,objects.json}`；`source-hashes.json`记录本轮源码快照哈希。

修改文件：`src/flash.c`、`include/board_revA2.h`仅FLASH_BUSY常量、`tests/flash_nor.c`、新增`tests/flash_time_cases.h`；host `test_flash_bounds_reject_before_spi`只加入时间mock及CS释放对应调用数1→2。未修改其他测试。

仍需板上验证：实际SPI/CS时序、温压边界tPP、TIM2/SPI失钟、断电半写、长航次页持久化，以及真实硬件下的超时裕量。尚未建立最终ELF或板上证据。
