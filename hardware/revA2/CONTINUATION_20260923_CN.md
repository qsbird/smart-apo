# Rev.A2 后续开发检查点（2026-09-23）

> **活动目标最新检查点**：ERC **0/0**；普通DRC错误 **0**，仍有 **25未连接、111警告**，一致性0，**NOT_FAB_RELEASED**。LSE已同面无过孔；host/native 23项＋runtime 1项测试通过，两变体ARM目标文件可编译，最终ELF/HAL/板上仍未完成。详见 [完整目标检查点](GOAL_CHECKPOINT_20260923_CN.md)。下方旧数字为历史。


**官方 DRC 仍未通过，NOT_FAB_RELEASED。** 本轮将普通 DRC 错误从 12 降到 0，未连接从 59 降到 40；不能把“普通错误 0”说成“整板 DRC 通过”。108 项警告尚未逐项关闭。

| 实际检查 | 本轮开始 | 最终主文件 |
|---|---:|---:|
| KiCad | 10.0.6 | 10.0.6 |
| DRC 普通错误 | 12 | **0** |
| 未连接项目 | 59 | **40** |
| DRC 警告 | 108 | **108** |
| 原理图一致性问题 | 0 | **0** |
| ERC | 上轮 0/0 | 本轮重跑 **0/0** |
| native 回归 | 15 | **17 项通过** |
| ARM 构建 | 未通过 | **exit 2：缺 arm-none-eabi-gcc** |
| 生产导出 | 拒绝 | **exit 2：仍有未连接，拒绝导出** |

## PCB 改动与依据

- U2 原矩形禁布将正常焊盘引出也拦截。依据 [ST TN1383 §3.2–3.5](https://www.st.com/resource/en/technical_note/tn1383-pcb-design-guidelines-for-mems-sensors-stmicroelectronics.pdf) 的等宽、长轴向外引出及本体下保护要求，改成两层规则：**完整本体仍禁过孔和覆铜；走线只开放 14 个径向 0.20 mm 通道，实际引线 0.15 mm**。0.20 mm 是工程实现尺寸，不是 ST 给出的推荐数值；不代表原厂 Gerber/装配认证。
- 14 个焊盘位置、铜尺寸、编号和网络未改。通道彼此隔离，不形成横穿本体的路径；错误网络仍由正常铜间距/短接检查约束，规则本身不是按网络的白名单。
- 完成 U2 五个地脚及局部供电连接。地通过普通短线引出，不把地平面直接铺入本体。
- REED_WAKE 原来在顶层向上绕行后再向下，切断右侧去耦附近的地连接。改为局部逃线进入 In2.Cu，保留 In1.Cu 地参考；未通过的路径副本已弃用。
- 用实际地线连接 C16/C5/U6/U7，关闭余下热焊盘错误，未降低最少热引线规则或设置错误豁免。
- 接通 Flash 供电、CS 上拉供电、压力去耦的 3V3；调整阻挡供电的 FLASH_CS 局部段；接通电池分压与滤波节点。所有新增过孔仍为 0.60/0.30 mm。

U3 **未修改**：其外围焊盘与中央 PAD2LID 不能机械套用 U2 径向规则。原厂允许金属盖接地或悬空，但本项目保留原接地选择，未擅自改网。评估板 Gerber 下载仍失败，中央接地/其他引出方式继续待审。访问证据在 `validation/revA2_continue/sources/mems_source_access_20260923.json`；没有宣称取得或重新校验历史 ZIP。

## 正反例与回退证据

本轮所有候选先写 `validation/revA2_continue/` 的独立子目录，再运行 KiCad 官方 DRC；主板只合入最终通过局部检查的 `battery_sense` 候选。

- `u2_rule_evidence.json`：2000 个确定种子的本体采样点检查；完整投影仍禁 via/pour；只开放径向通道；原焊盘几何/网络不变。
- `negative_inner_track`：本体内线路触发 `items_not_allowed`。
- `negative_body_via`、`negative_escape_via`：本体或逃线通道里的过孔均触发 `items_not_allowed`。
- `negative_short`：将不同电源/地实际连在一起，触发 `tracks_crossing ×2`、间距和阻焊桥错误。不是 `shorting_items` 类别，不混淆统计。
- `negative_wrong_net`：只标错一条孤立线的网络，KiCad 连通性重建后没有新增错误；**此试验不计作有效反例**。
- `reed`、`reed2`、`flash_power`、`mcu_power` 均有失败报告。尤其 MCU 电源试接碰到旧 LSE/I²C 铜及 UART 净空，未合入，下一轮需先调整这些网络。
- `comparison.json`：每一阶段完整分类计数；`repair_queue.csv`：当前所有缺口和警告的网络、坐标、UUID；`unconnected_by_net.json`：逐网数量。
- `baseline/` 和 `final/` 保存完整工程快照；`board_invariants.json` 证明所有编号焊盘网络、12×35 mm 板框、四层/1.0 mm 及工程规则文件保持不变。未提交、未 reset、未动 Rev.A1。

独立子代理已只读复核规则几何和上述官方报告。规则可作为当前工程实现采用，land/钢网、传感器偏置及实际装配仍未认证。

## 固件改动与实际测试

移除 CPU 每循环自增 1000 µs 的伪时间，新增 `board_time_us()` 契约；没有真实 HAL 时基时失败闭合。调度改用整数相位，支持 uint32 回绕和 104/208/320 Hz 非整数微秒周期；迟到只读取当前一次，记录跳槽数，不伪造补采。

本轮主任务实际运行：

```sh
python3 -m unittest discover -s firmware/host/tests -v
make -C firmware/mcu
python3 tools/validate_revA2.py
bash -n tools/export_fab_revA2.sh
git diff --check
bash tools/export_fab_revA2.sh
```

结果：17 项通过；ARM 构建 exit 2；结构检查通过但保留 PCB 门槛；shell 语法与 diff 检查通过；导出 exit 2。两变体各模拟三小时、1 ms 轮询，验证累计名义次数和多次计数回绕。另实际对 8 个 C 源文件×2 变体执行 `clang --analyze`，全部退出 0，但 `board.c` 仍有合计 4 条已知 MMIO 固定地址警告，不能写成零警告。

完整命令/stdout/stderr/退出码在 `validation/revA2_continue/commands.json`；测试日志 `native_tests.log`；详细固件边界见 `firmware/mcu/VERIFICATION_TIMING_CN.md`。没有新增依赖，没有 ARM 映像或板上运行通过结论。真实 HAL 时钟、DRDY/FIFO、总线吞吐、Stop 连续性仍缺验证；主机仍拒绝跨 71.6 分钟的原始时间戳回绕，尚需显式时间重建。scipy、样机和测量设备缺失状态未改变。

官方 PCB 最终命令（CLI 绝对路径 `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`）：

```sh
kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --save-board --schematic-parity -o hardware/revA2/drc_revA2_kicad10.json hardware/revA2/smart_apo_common_revA2.kicad_pcb
kicad-cli pcb drc --format json --severity-error --units mm --refill-zones --schematic-parity -o hardware/revA2/drc_revA2_errors_only_kicad10.json hardware/revA2/smart_apo_common_revA2.kicad_pcb
```

实际执行使用绝对路径；ERC 由导出门控中的 `sch erc --format json --severity-all` 重跑，报告位于 Rev.A2 目录。不能仅看错误级报告的 0 项而忽略另列的 40 项未连接。

## 剩余工作与下一步

1. 成组重新安排 LSE 的同面短连接，调整阻挡 MCU 电源的旧 I²C/LSE/UART 局部铜，不能仅移动晶体而保留旧线。
2. 完成余下 40 个连接缺口：3V3 11、GND 7、I²C SDA/SCL 各3、NRST 3、VBAT 3、LSE_OUT 2、SPI三线各1、IMU_INT/VBAT_SENSE/BRIDGE_S+/VBG/CHARGE_IN 各1。优先电源与回流，再模拟/LSE及总线；已连通桥路仍需成对/长度/回流质量审查。
3. U3 引出/中央焊盘方案、U2 land/钢网原厂交叉验证仍需资料。CT05所购图纸、电芯允许充电电流、采购后缀、Rev.A2装配 STEP、3D干涉及全部实物试验仍开放。
4. 108项丝印/文字警告逐项处理。原工程忽略的5类检查也仍需恢复适用检查或写明处置依据，不能视为已完成审核。
5. 所有布线和制造门槛关闭后再生成/独立查看 Gerber、钻孔、最终 BOM/CPL；当前没有生产输出。

## 本轮主要改动文件

- `hardware/revA2/smart_apo_common_revA2.kicad_pcb`、U2 `.kicad_mod`、官方报告与状态/来源文档。
- `tools/validate_revA2.py`：适配 KiCad 格式化后的封装，检查两层保护规则名称/属性，标明评估板资料仍阻塞。
- `firmware/mcu/src/{main,board,app,sensors}.c`、对应头文件、`tests/app_errors.c`、新 `tests/sensors_timing.c`、README/时基报告及备份。
- `firmware/host/tests/test_firmware_contract.py`、`validation/revA2_continue/` 和交接状态。
