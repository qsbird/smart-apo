# 上部 I²C 与 C2 布局检查点 · 2026-09-23

已采用stage7，主板SHA256 `1a1a7fcad2d150ee43c46b6f7101dc1ba2a8e248c48ab6936936ded90dc67e78`。NOT_FAB_RELEASED。

## 已改文件与行为

正式PCB连接U2/U3的SDA与SCL：SDA为F.Cu，SCL以两个0.60/0.30mm过孔转In2。未在In1放置信号。

C2从F(2.5,3.2),0°移动/旋转至F(3.1,3.3),90°，旧供电线先移除再重接。pad1到U2 pad12的同面中心线由2.295317mm缩至1.5575mm，无过孔；地端显式连接1.207401mm至GND via(4.15,3.2)，同时接入F地铜。新增供电via(3.7,3.95)和B电源桥恢复原供电区域连接；另一地via由(8.8,3)移到(9,2.8)。源脚本、变更清单、候选及前后完整副本均在validation/revA2_i2c；未重新生成整板、未改Rev.A1、原理图、封装库、网络或制造规则。固件未改。

## 实际验证

| 阶段 | 普通DRC错误 | 未连接 | 警告 |
|---|---:|---:|---:|
| baseline | 0 | 8 | 119 |
| stage1 | 1 | 7 | 119 |
| stage2 | 1 | 6 | 119 |
| stage3（未采用） | 0 | 6 | 119 |
| stage4 | 3 | 6 | 117 |
| stage5（未采用） | 0 | 6 | 117 |
| stage6 | 1 | 6 | 120 |
| stage7与正式复检 | 0 | 6 | 120 |

stage1–2存在间距/供电问题；stage3和stage5虽然普通错误0，但去耦绕行或余量仍需改善，未采用。stage6的C2地热焊盘连接不足，通过新增实际地支路修复。stage7经独立只读审核采用，不以最少DRC数量选择牺牲供电的方案。

实际执行：

```sh
bash tools/export_fab_revA2.sh
python3 tools/validate_revA2.py
python3 tools/check_divider_revA2.py --output validation/revA2_i2c/divider_consistency.json
python3 validation/revA2_i2c/summarize.py
```

官方KiCad10.0.6 ERC0错误/0警告；DRC一致性0；制造脚本exit2正确拒绝Gerber/钻孔/CPL。validate确认Rev.A1哈希未变；分压跨文件一致性通过。

使用KiCad自带Python运行check_invariants.py通过：43封装、四层、1mm、12×35mm、焊盘网络和项目规则保持。tools/check_reference_revA2.py主板对baseline显式重新填铜，exit2、GEOMETRY_REVIEW_REQUIRED：六敏感网完整、In1地单轮廓，但7个原3V3支路边缘点落入新供电via自身反焊盘，最大半径0.450694mm。独立检查真实离散轮廓最大半径0.454388mm，按局部供电转换单独接受；检查器未改弱，见reference_disposition.json/independent_review.md。这不是整板参考检查无条件PASS或EM验证。

独立新线检查：SDA全段线心/两边缘0.01mm采样无缺口；SCL仅自身via反焊盘附近缺口，In2主段完整。全部via铜环对U2本体最小0.100mm、U3本体0.100mm、U5最大物理EP0.165026mm。供电连通覆盖C2、U2所有供电脚、U3和U5。

警告120：压铜55、重叠49、板边9、字高6、背面未镜像1。C2旋转造成与U2参考文字的两项新丝印重叠，同时消失一项旧压铜，详见warning_delta.json；全部仍OPEN。

## 下一步和未完成项

剩余6个缺口：SDA2、SCL2、IMU_INT1、MOSI1。优先将上部总线接到MCU/上拉及ADC分支，每组继续隔离副本/官方DRC/填铜参考检查，再处理MOSI与IMU_INT。

尚未完成警告与忽略项审查、最终生产文件/独立查看器、实际器件/电芯资料、壳体STEP与干涉。C2缩短路径不代表传感器噪声、去耦或EM实测通过。固件本轮没有新构建证据；前次MCU8/8、host23/23、20ARM对象仍不能代替最终ELF及板上验证。
