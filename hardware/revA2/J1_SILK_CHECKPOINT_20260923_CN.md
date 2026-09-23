# J1丝印修复检查点 · 2026-09-23

正式PCB SHA256 `b4cd28a221e775204be5104304cd2ad4cf78ea957d4ed6505ae8f0710cd50a16`。官方KiCad10.0.6 ERC0错误/0警告、DRC0错误/0未连接/0一致性问题、75警告。NOT_FAB_RELEASED。

J1矩形轮廓改为三条B.SilkS线：顶边(3.4,31.2)→(9.6,31.2)，左边(2.8,31.6)→(2.8,34.6)，右边(9.6,31.2)→(9.6,34.6)，0.15mm线宽。左上断开以避让Q1，底边开放以避开板框。J1 Reference改为(9.9,30.3)、0°、0.8mm字高、0.12mm笔画，原B面镜像属性保持。BATTERY_WIRE_PADS项目库同步相同本地几何。

改动文件为正式PCB、`SmartApoRevA2.pretty/BATTERY_WIRE_PADS.kicad_mod`、官方报告/离线报告及交接文档。检查脚本验证除J1 Reference与丝印图形外所有PCB内容一致（只归一化空白），库除丝印图形外一致；原理图和项目逐字节一致。焊盘、走线、阻焊、钢网不变。

首轮候选与Q1及J1自身位号冲突，未采用，try1_drc.json/try1.png保留。修订版官方DRC：silk_edge_clearance1→0、silk_overlap27→26、silk_over_copper48→46、missing_courtyard3不变，79→75；按type/关联UUID核对无新增项。PDF/PNG背面图检查确认间隔与位号可辨认；不证明实际焊线和应力释放空间。

实际命令与结果：

- KiCad内置Python运行`validation/revA2_j1_silk/edit.py`：独立副本调整。
- `kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_j1_silk/candidate/drc_revA2_kicad10.json validation/revA2_j1_silk/candidate/smart_apo_common_revA2.kicad_pcb`：0错误/0未连/75警告。
- `python3 validation/revA2_j1_silk/verify.py`：修改范围、库一致性范围、无新增DRC通过。
- 正式采用后`bash tools/export_fab_revA2.sh --check-only`：exit0，ERC/DRC上述结果。
- `python3 tools/validate_revA2.py`：exit0，Rev.A1哈希保持，fab_export不存在。

证据目录`validation/revA2_j1_silk/`包含baseline/candidate/final、invariants.json、官方日志、PDF/PNG、visual_verdict.json与75项OPEN警告队列。固件未改未重测。

板边和文字高度两类警告已清零。下一步继续26项丝印重叠与46项压铜；3项连接区courtyard须实际装配输入。所购LED极性、CT05/电芯与充电/MLCC资料、Pogo及板厂能力、当前板壳体3D、最终ELF和板上验证仍开放。
