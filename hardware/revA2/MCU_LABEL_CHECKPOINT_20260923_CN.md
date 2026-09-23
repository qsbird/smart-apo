# MCU区域标识处置 · 2026-09-23

正式PCB SHA256 `e62f55cb4d6c187d1a66acfcdf15ef2b8469bff6e81309c88e2d757f687e717f`。官方ERC0错误/0警告，DRC0错误/0未连接/0一致性问题、50警告；NOT_FAB_RELEASED。

## 处置理由与范围

第一候选将R11/C17/C1/C14移至MCU内部空白铜区，虽DRC70→50，但图面显示标识堆叠于U1本体投影内，装配后遮挡/归属不清，拒绝采用。try1板、DRC及图保留。

最终仅修改六个Reference字段：R11/C17/C1/C14/C16的丝印Reference设为不可见，保留各自封装原位的F.Fab `${REFERENCE}`，没有删除器件标识。R4位号移至(8.8,17.5)mm、0°、0.8mm字高/0.12mm笔画并保持可见。C16此前位于U1本体投影内，随本次纠正。物理PCB不再印刷上述五个位号，检修/装配依赖随板装配图，必须在交付包中提供该图；不能把隐藏位号说成装配后仍可见。

官方`assembly_FRONT_REVIEW.pdf`（F.Fab/Edge.Cuts，exclude-value）已渲染查看：R11(10.55,8.4)、C17(10.8,10.4)、C1(10.55,12.4)、C14(10.75,14.4)、C16(1.1,10.6)mm均在实际本体中心标识，可放大定位。此PDF仅证明本组标识保存；U2/U3等项目封装装配标识不完整，不能声称全板装配图已完成。

授权六个Reference块剔除后PCB逐字节一致，原理图/项目逐字节一致；铜、焊盘、器件位置、规则和既有Fab标识不变。没有DRC忽略/排除。

## 实际验证

- KiCad内置Python运行`validation/revA2_mcu_labels/edit.py`于独立副本。
- `kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_mcu_labels/candidate/drc_revA2_kicad10.json validation/revA2_mcu_labels/candidate/smart_apo_common_revA2.kicad_pcb`：0错误/0未连/50警告。
- `python3 validation/revA2_mcu_labels/verify.py`：仅六字段变化、无新增项通过。
- 正式采用后`bash tools/export_fab_revA2.sh --check-only`：exit0，ERC/DRC上述结果。
- `python3 tools/validate_revA2.py`：exit0，Rev.A1哈希保持，fab_export不存在。

分类silk_overlap25→18、silk_over_copper42→29、missing_courtyard3不变。减少20项；每项按type与关联UUID比较，无新增项。候选与正式结果一致。

修改正式PCB和检查报告/交接文档；固件未改未重测。证据`validation/revA2_mcu_labels/`包含baseline/candidate/final、invariants.json、官方日志、两种PDF/PNG、visual_verdict.json及50项OPEN队列。

下一步继续上部供电/传感器区与底部丝印冲突，补齐完整装配标识/输出。courtyard、采购型号/极性、Pogo/板厂工艺、当前3D与最终固件及实机门槛保持开放。
