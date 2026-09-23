# Rev.A2 开发与验证检查点（2026-09-23）

> **2026-09-23 后续实测**：ERC **0/0**；普通 DRC 错误 **0**，仍有 **40 个未连接、108 个警告**，原理图一致性 0，**仍未通过 DRC / NOT_FAB_RELEASED**。U2 径向逃线规则已实现并通过正反例检查；固件 **17 项 native 回归通过**，ARM/板上未验证。详见 [后续开发记录](CONTINUATION_20260923_CN.md)。下方早期数字保留为历史；勿重新生成整板。


本轮推进了 PCB 与固件，**完整布线和发行目标尚未完成，仍为 NOT_FAB_RELEASED**。以下为本轮实际工具证据，不以历史记录代替验证。

## 当前结果

| 检查 | 开始时实测 | 本轮主文件最终实测 |
|---|---:|---:|
| KiCad 版本 | 10.0.6 | 10.0.6 |
| 官方 ERC 错误 / 警告 | 0 / 0 | 0 / 0 |
| 官方 DRC 错误 | 104 | **12**（全部 starved_thermal） |
| 官方 DRC 警告 | 133 | **108** |
| 官方未连接项目 | 74 | **59** |
| 短路 | 24 | **0** |
| 普通间距 / 孔间距 | 15 / 7 | **0 / 0** |
| 封装 courtyard 重叠 | 10 | **0** |
| 铜到板边 / 阻焊桥错误 | 7 / 25 | **0 / 0** |
| 禁布违规 | 0 | **0** |
| 原理图一致性 | 开始的基线命令未启用 | **0**（显式启用） |
| 固件 native 回归 | 未建立本轮证据 | **15 项通过** |
| ARM 可启动构建 / 板上运行 | 未验证 | **未完成 / 未验证** |

`violations` 的错误/警告与 `unconnected_items` 分开计数，不能把 12 项错误误称整个 DRC 只剩 12 项。原理图中的 9 个明确 NC 引脚也不等于 PCB 的 59 个未连接。

Git 保持 `cursor`，`cursor/codex/main` 均从 `830e5a6` 起步；未 reset、清理或提交已有工作。Rev.A1 哈希检查通过，所有编号焊盘的网络映射与开始时完全相同。板仍为四层、1.0 mm，43 个封装，所有过孔为 0.60/0.30 mm。详见 `../../validation/revA2_20260923/board_invariants.json`。

## 已改变的 PCB 与原因

1. C8 离开背面 J2 Pogo 触点，移开两个冲突地过孔，消除 Pogo/充电/复位短路。
2. 修正 U2：ST 图中的 L/W 被旧记录误读为 X/Y。顶视投影现在为 X=3.0、Y=2.5 mm，项目库改名并同步原理图、网表；保留脚号、网络和焊盘 UUID。改动前确认 U2 没有相接走线。**0.625×0.35 mm 是候选 land，不是已获 LSM6DSO 原厂装配认证**，见 `LSM6DSO_FOOTPRINT_SOURCE_CN.md`。
3. U7/C9/C10 移出底部桥接口；充电器 U6/R3/C11/C12 移到背面，单独重接 CHG_PROG。充电器接近模拟区的热/噪声影响仍需布局复审和实测，不能据 DRC 判定模拟性能通过。
4. 调整 Q1/R7、D1/R6、C3/J1 及局部过孔；修改相接走线端点，移动焊盘内过孔时同步跨层相接走线。LED_A 的旧连接单独拆除并重接，未运行迷宫或全板生成器。
5. 接通 LDO 输入/输出去耦和充电器电容短连接；补 LDO→3V3 内层平面、J1→VBAT 平面馈线，消除孤立电源铜区和悬空过孔警告。删除一个同网同尺寸同位置的重复磁簧过孔。
6. 外层热引线宽度、热间隙、铜区最小厚度一致设置为 0.15 mm，仍符合当前候选线/隙规则，未降低最少热引线数。实际板厂能力和焊接工艺仍需确认。
7. 根据官方网表同步 43 个 `Population` 字段；原理图一致性从首次扩展检查的 43 项字段警告降为 0，双装配表未改变。

所有几何试验先写独立副本，再跑官方 DRC。主板只合入最终经过检查的链条，没有把失败试验的铜直接留在主板。

## 回退与每组计数

完整副本、分类计数和对象级修改日志位于 `../../validation/revA2_20260923/`：

- `baseline/`：开始时 PCB/原理图/工程、官方 ERC/DRC、已有 tracked 改动补丁及项目库。旧错误 U2 mod 保存在此处用于回退，不能作为当前封装选型。
- `stage*/`：每次候选 PCB、工程、原理图、库和官方 `drc.json`；`smart_apo_common_revA2.changes.json` 记录移动前后位置、调整端点 UUID 及明确局部路径。
- `comparison.json`：所有阶段错误/警告/未连接与按类型计数；`repair_queue.csv`：每一个仍开放问题的网络、坐标、UUID 和处置状态。
- `final/`：本轮最终板及报告；`local_repairs.py` 只向不存在的输出文件写入，拒绝覆盖输入。不是全板自动布线器，也不是下轮应盲跑的生产脚本。

明确不采用：stage04 充电组前移使旧铜产生新短路；stage06 背面层识别不完整，已由 stage06b 纠正；stage07 背面中部与已有 SWD/UART/SPI 铜冲突；stage13 热引线小于铜区最小厚度，虽错误归零却导致未连接升至 85，已拒绝；stage14_probe 仅作禁布诊断，未合入。stage08–11 是连续 LED/板边修复的中间副本，不能单独作为已通过板。

## 尚未解决的硬件工作，按执行顺序

1. **先审查 U2/U3 逃线与禁布规则的可实现性。** U2 候选禁布为整个本体投影，而焊盘也在投影内。stage14_probe 从 U2 pad2 `(1.1375,6.35)` 向外接到 `(0.65,6.35)`，0.15 mm 线宽、0.4875 mm 长，官方新增 `items_not_allowed`；已撤回，保留原规则。必须以原厂布板/焊接指南、评估板铜/钢网证据区分端子接线通道与其余本体下禁布区，不能简单关闭规则。U3 PAD2LID 接地逃线也需一并复核，当前还未接通。ST STEVAL-MKI196V1 页面有 Gerber，但本次下载接口失败，尚未取得用于交叉核对的压缩包。
2. **补接地与 12 个热焊盘连接。** 位置见 CSV；包括 U2 的 1/2/3/6/7，U6/U7 地脚，C1/C5/C14/C16/C17。保持最少热引线规则，局部增接地走线/过孔与调整间隙后逐组跑 DRC，不以 direct-connect 或规则豁免掩盖工艺问题。
3. **完成模拟与 LSE。** 尚有 BRIDGE_S+、VBG 未接；已接通的桥输入也没有完成短、并行、少过孔及连续回流审查。Y1 在背面、MCU 在正面，现有布置不满足 LSE 同面无过孔目标，需成组重排 Y1/C15/C16 并同步铜；不能只勾“网络已通”。
4. **剩余电源/信号逐网完成。** 数量见 `unconnected_by_net.json`，优先地和电源、NRST，再 SPI、I²C、IMU_INT/VBAT_SENSE；59 是连接缺口数，不是 59 个独立网络。保持 U2/U3 规则和连续 In1 回流，不能以铺铜覆盖或修改网络名清零。
5. **警告逐条审查。** 当前 108 项为丝印压铜 55、丝印重叠 39、丝印板边 7、文字高度 6、背面文字未镜像 1。CSV 全部保持 OPEN，没有进行空泛整体豁免。原工程还忽略了 5 类检查（含 missing_courtyard、track_not_centered_on_via），完整键列在 validation_report；这不等于这些项目已经合格，放行前应恢复适用检查或逐项写明依据。
6. **资料/机械/实物阻塞继续开放。** 所购 CT05 精确后缀及焊盘图；所购带保护 401020 的尺寸、公差、保护板、允许充电电流和温度范围；LSM6DSO land/钢网；W25Q256JVEIQ 中央焊盘工艺；其余采购后缀；Rev.A2 壳体/电池/Pogo/器件 STEP、压力口与 O 形圈装配。50 mA 仍只是候选，未用相似电芯推定通过。15 m 压力、盐水、梁标定及首件装配均无样机证据。

## 实际复核命令与结果

在项目根目录运行，`KICAD` 表示 `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`：

```sh
"$KICAD" version
"$KICAD" sch erc --format json --severity-all -o hardware/revA2/erc_revA2_kicad10.json hardware/revA2/smart_apo_common_revA2.kicad_sch
"$KICAD" sch export netlist --format kicadxml -o hardware/revA2/netlist_revA2_kicad10.xml hardware/revA2/smart_apo_common_revA2.kicad_sch
"$KICAD" pcb drc --format json --severity-all --units mm --refill-zones --save-board --schematic-parity -o hardware/revA2/drc_revA2_kicad10.json hardware/revA2/smart_apo_common_revA2.kicad_pcb
"$KICAD" pcb drc --format json --severity-error --units mm --refill-zones --schematic-parity -o hardware/revA2/drc_revA2_errors_only_kicad10.json hardware/revA2/smart_apo_common_revA2.kicad_pcb
python3 tools/validate_revA2.py
python3 -m unittest discover -s firmware/host/tests -v
bash -n tools/export_fab_revA2.sh
bash tools/export_fab_revA2.sh
```

ERC 0/0；DRC 12/108/59、一致性 0；结构检查为 PASS_WITH_PCB_AND_PHYSICAL_TEST_GATES，Rev.A1 哈希未变；15 测试通过；shell 语法通过；实际导出脚本 **exit 2 并打印 REFUSING**，没有生产 Gerber/钻孔/CPL。本次增强导出门控：先 ERC，再包含一致性的 DRC；未来 BOM 使用官方 CSV 导出且失败不再被 `|| true` 吞掉。通过导出仍不等于 FAB_RELEASED，须完成独立查看和 3D 审查。

本机 DRC 最初在沙箱中 SIGABRT；崩溃栈为 macOS `_RegisterApplication`/wx 调用。经受控沙箱外运行同一官方 CLI 后得到报告；不是 KiCad 对板文件“通过”或“失败”的替代判断。Fontconfig 版本警告另保留在日志，未改系统设置。

## 固件与改动文件

固件详见 `../../firmware/mcu/VERIFICATION_20260923_CN.md`，含实际 ARM 构建失败、16 个 C 单元检查、4 条已说明 MMIO 静态分析警告、15 个 native 模拟测试及其边界。仍是代码骨架与宿主机可编译逻辑，缺 ARM 工具链、startup/linker/时钟树/HAL；没有可烧录发行包、没有板上运行结论。主机完整 autotune 仍缺 scipy，异步日志重采样/真实时基/回绕/实物标定仍未完成。

本轮改动入口：

- PCB/原理图/库：`smart_apo_common_revA2.kicad_pcb`、`.kicad_sch`、新 `SmartApoRevA2.pretty/LGA-14_3x2.5mm_P0.5mm_LSM6DSO.kicad_mod`；删除现用目录中的旧错误尺寸 mod，备份保留。
- 工程证据：官方 ERC/DRC 两种报告、netlist、validation_report；本文件、来源文档、README/放行清单/历史检查点/挪位清单及 CONTEXT_HANDOFF 的最新状态说明。
- 工具：`tools/validate_revA2.py`、`tools/export_fab_revA2.sh`、`tools/generate_revA2.py`（新封装引用并修正既有 CT05 str.replace 第三参数类型错误；**未运行生成器**）。
- 固件：`firmware/mcu/Makefile`，`include/{board_revA2,app,datalog,flash,sensors}.h`，`src/{board,app,datalog,flash,sensors}.c`，README、SENSOR_CTRL_INIT、验证报告、`tests/` 和 `validation/`；`firmware/host/dump_decode.py`、README 及 `tests/`。
- 可回退检查点和分类清单：`validation/revA2_20260923/`。

不要重新运行 `generate_pcb_revA2.py`、`route_explicit_revA2.py` 或旧挪位脚本覆盖本板；生成器的历史布局不是当前已审核局部修改的输入源。
