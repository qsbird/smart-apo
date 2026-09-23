# 被动元件位号检查点 · 2026-09-23

正式PCB SHA256 `219ca81babca79fb46813d85b972640d5fdb1bb4a3a9a6a60cb268873feeee20`。官方ERC0错误/0警告、DRC0错误/0未连接/0一致性问题、36警告；NOT_FAB_RELEASED。

仅五个Reference字段改动：R8(5.9,28.4)/0°、C5(2.9,18.2)/0°、C3(1,16)/90°、C8(3,1)/0°、R10(8,16.3)/0°，坐标mm，均0.8mm字高/0.12mm笔画，保持原面、镜像和可见状态。剔除五字段后PCB逐字节一致；原理图/项目逐字节一致；铜、焊盘、器件位置、规则和Fab标识不变。

官方分类：silk_overlap18→11、silk_over_copper29→22、missing_courtyard3不变，总50→36。按type/关联UUID比较无新增项。正反面PDF/PNG已查看，位号可辨认、未放到其他器件本体下方。R8等偏置位号准确对应仍由原位Fab装配图提供。

实际命令：

- KiCad内置Python运行`validation/revA2_passive_labels/edit.py`于独立副本。
- `kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_passive_labels/candidate/drc_revA2_kicad10.json validation/revA2_passive_labels/candidate/smart_apo_common_revA2.kicad_pcb`：0错误/0未连/36警告。
- `python3 validation/revA2_passive_labels/verify.py`：字段不变量与无新增项通过。
- 正式采用后`bash tools/export_fab_revA2.sh --check-only`：exit0，ERC/DRC上述结果。
- `python3 tools/validate_revA2.py`：exit0，Rev.A1哈希保持，fab_export不存在。

修改正式PCB及检查报告/交接文档，固件未改未重测。证据`validation/revA2_passive_labels/`含baseline/candidate/final、invariants.json、官方日志、正反面PDF/PNG、visual_verdict.json及36项OPEN队列。此前装配层PDF对应旧板哈希，但本次只改SilkS Reference，Fab几何原样保持；最终交付仍须从最终板重新导出完整图包。

下一步继续上部供电/传感器/LSE区域与连接焊盘轮廓。所购器件/极性、连接装配courtyard、板厂工艺、当前3D与最终固件及实机门槛仍开放。
