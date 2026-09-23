# Flash实时时限与交互检查点（2026-09-23）

**目标仍未完成，NOT_FAB_RELEASED。** 本轮修复Flash正常页编程被固定32轮提前拒绝的缺陷；没有采用PCB新布线。

## Flash实际修改及证据

原厂W25Q256JV RevR §9.7印刷页84（PDF第85页）给出tPP最大3ms。先用NOR模型复现：1ms忙时间、每次状态查询推进10us，旧32轮代码错误返回失败。失败日志已保存；修复后使用实际TIM2名义5ms预算及连续4096次停滞上限，不能把轮询数当时间。

首次RDSR已ready允许无TIM2只读恢复；若BUSY则缺失/坏时基失败。真正PP之前验证两次时基进展和WEL，时间不足不发PP。已占/半写页仍拒写；失去确认后的重试先读回，不重复编程已匹配数据。CS断言失败也尝试释放；这不是物理引脚完好的证明。

修改：`firmware/mcu/src/flash.c`、`board_revA2.h`的Flash常量、`tests/flash_nor.c`、新增`tests/flash_time_cases.h`；host的边界用例最小加入时间mock和CS释放计数。原厂PDF、来源、先失败后通过、边界与故障范围见 `firmware/mcu/VERIFICATION_FLASH_TIME_CN.md` 和 `firmware/mcu/validation/flash_time/`。

主代理执行：

```sh
python3 -m unittest discover -s firmware/host/tests -v
python3 -m unittest discover -s firmware/mcu/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/flash_time_checkpoint/arm
```

host23/23、MCU8/8通过；两变体共20个ARM ELF32 REL对象构建、独立标头及SHA256检查通过。日志 `validation/revA2_interactive/{host_tests,mcu_tests,arm_objects}.log`；对象清单 `arm_objects.json`。仍不是最终ELF或实物写入验证；需要实测电压/温度/CS/SPI/tPP、失钟、断电半写和整航次。

## 工具链及PCB交互检查

只读查找PATH、现有LLVM、rustup、PlatformIO、Arduino15、Android NDK、ST应用和Homebrew lld，未找到可复用的ARM链接器/GNU工具链。没有安装新依赖，安装授权仍待答复。

按computer-use技能通过node_repl/@oai/sky打开KiCad独立副本 `validation/revA2_interactive/candidate/`，设置0.025mm网格和仅铜层视图。当前工具画布定位未能可靠命中目标焊盘，没有保存或采用交互布线结果；不会把打开GUI当作完成布线。

主板和副本的PCB SHA256仍同为：`11a0af492376e9f421871f7b683ed533b008d6664074b2e23b9880d0cb1a1d9f`。截图 `validation/revA2_interactive/pcb_editor_copper.png`、`inspection.json`记录过程及未改动证据。不是独立Gerber/3D制造检查。

本轮未改变PCB文件，因此最近官方ERC0/0、普通DRC0/未连接14/警告119保持，未重复KiCad引擎检查。后续仍须逐网局部布线、官方DRC与显式填铜审查，不能采用被撤回的切割参考地方案。

剩余：PCB14连接、警告/制造规则/精确封装/机械资料；真实Stop/RTC、检测器、最终ELF/栈预算、ADC/时钟/功耗/实物测试。没有生产导出、Git提交或Rev.A1修改。
