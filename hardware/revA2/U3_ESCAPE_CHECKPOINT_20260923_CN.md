# U3 原厂证据恢复与电源接地检查点 · 2026-09-23

主板已采用stage2，SHA256 `bc4752a050596e0526e141b44952985f73ba22a37cbd0cb3ce27c962ae53531a`，保持NOT_FAB_RELEASED。

## 找回的依据

从用户Downloads找回STEVAL-MKI225A原包，60158字节、27文件、ZIP CRC通过，SHA256 `3ada96e8f5379a3faae7fded4939724d4bf06484e59954bf688c2410324ce10f` 与历史记录完全一致。项目证据在 `validation/revA2_u3_recovered/`，包含原包、可重现Gerber解析脚本、整板及局部铜层图、钻孔核对与连通检查。此前失效HTTP响应没有用于验证。

原厂中央pad7以约0.199898mm顶层折线接pin5 GND，再外引至去耦地端、地铜与本体外过孔。外围六脚径向外引，原厂线宽约0.25/0.35mm；31孔均不碰本体。pin4原厂功能为INT_DRDY，本项目选择no-connect，不能称其原厂NC。原厂GBL本体下有无铜窗口，与本项目四层结构不是同一布局。

## 正式改动

- PCB与项目 `LPS28DFW_CCLGA-7L.kicad_mod`：保留完整F.Cu本体禁过孔/禁铺铜，另设track guard，仅开放五个在用外围脚的径向通道和中央pad7→5通道。pin4不开放。
- 所有通道宽0.25mm并有端点方块，实际铜线0.20mm。中央路径有原厂直接依据；通道宽度与外围0.20mm为本项目工程选择，不能称ST对本项目批准或原厂原样复制。
- pad7→5→GND via(6.575,0.6)；pad6→3V3 via(5.425,0.6)；pad2向外至GND via(4.05,3.75)。未移动器件、未改焊盘网络，所有过孔0.60/0.30mm。
- 43封装、12×35mm板框、四层、1mm板厚、项目全局规则不变。新规则是几何通道，不是按网络授权；不覆盖未来不经过F.Cu的埋孔。

## 实際工具结果

| 阶段 | 普通DRC错误 | 未连接 | 警告 | 一致性 |
|---|---:|---:|---:|---:|
| baseline | 0 | 12 | 119 | 0 |
| stage1，拒绝 | 1 | 8 | 119 | 0 |
| stage2，采用 | 0 | 8 | 119 | 0 |
| 主板复检 | 0 | 8 | 119 | 0 |

stage1地孔与已有3V3铜间距不足，stage2仅调整该地孔及其相连铜后清除。完整前后副本 baseline/final、各候选DRC、分类comparison.json和逐项repair_queue.csv均在 `validation/revA2_u3_escape/`。

实际命令：

```sh
bash tools/export_fab_revA2.sh
python3 tools/validate_revA2.py
python3 tools/check_divider_revA2.py --output validation/revA2_u3_escape/divider_consistency.json
python3 validation/revA2_u3_escape/summarize.py
```

官方KiCad10.0.6 ERC0/0；门禁exit2拒绝Gerber/钻孔/CPL，未生成生产文件。另使用KiCad自带Python运行 `check_invariants.py`、`check_rules.py` 和 `tools/check_reference_revA2.py`（主板对本组baseline），均退出0。显式填铜：In1地单轮廓，六条敏感网络完整，无原有外层线新增参考缺口；不代表EM/压力偏移/应力验证。

规则证据：10000个本体随机点核验、每zone1000个库/板一致性点、所有过孔避开U3本体与U5最大物理EP。正例SDA/SCL向外引线普通错误0；内部横穿、本体过孔、逃线处过孔各触发1项items_not_allowed。真实3V3→GND短路反例触发6项错误（含tracks_crossing）。重复重叠错网线负例未触发错误，明确不当作有效短路测试；该限制已记录。独立只读审查同意作为续布线基线，见independent_review.md。

## 剩余工作

剩余8个缺口：SDA3、SCL3、IMU_INT1、MOSI1。本轮MOSI仅读取实际阻挡铜，未采用新的MOSI候选；U3原始资料恢复使其电源地修复先具备了可审查依据。下一组优先连接U3/U2总线和MCU/ADC分支，再处理MOSI与IMU_INT，仍逐组独立验证。

119项丝印/文字警告和5类忽略检查未完成逐项放行。原厂Gerber获取阻塞已解除；四层布局下的压力偏移、回流与板上实测仍开放。CT05所购图纸、401020电芯/充电规格、采购后缀与3D壳体干涉仍未闭合。固件本轮未改未重测；已有MCU8/8、host23/23、20ARM对象不是最终ELF或板上运行证据。
