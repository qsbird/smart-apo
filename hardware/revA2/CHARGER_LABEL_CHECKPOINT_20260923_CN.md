# 充电区域位号检查点 · 2026-09-23

正式PCB SHA256 `94066e22c2fb98ba4b941ccdb95fd8ff4e4b268be3cedd7140fdf393a44213fe`。官方ERC0错误/0警告，DRC0错误/0未连接/0一致性问题、70警告；NOT_FAB_RELEASED。

只修改三个B.SilkS Reference字段，保持镜像/可见属性：U6(7.8,22.1)mm/0°、R3(1,22)mm/90°、C11(1,24.6)mm/90°，字高0.8mm、笔画0.12mm。剔除三个授权字段后PCB逐字节一致，原理图/项目逐字节一致，铜/焊盘/器件位置/规则不变。

官方分类：silk_overlap26→25、silk_over_copper46→42、missing_courtyard3不变，总75→70。按type/关联UUID比较无新增项。背面官方PDF经Poppler渲染并查看，三个位号清楚，局部图面通过；不是整板或实物通过。

实际命令：

- KiCad内置Python运行`validation/revA2_charger_labels/edit.py`，只修改独立候选。
- `kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_charger_labels/candidate/drc_revA2_kicad10.json validation/revA2_charger_labels/candidate/smart_apo_common_revA2.kicad_pcb`：0错误/0未连/70警告。
- `python3 validation/revA2_charger_labels/verify.py`：字段不变量和无新增项通过。
- 采用后`bash tools/export_fab_revA2.sh --check-only`：exit0，官方ERC/DRC上述结果。
- `python3 tools/validate_revA2.py`：exit0，Rev.A1哈希保持，fab_export不存在。

修改正式PCB，刷新ERC/DRC/校验报告、检查点与交接入口。固件未改未重测。证据`validation/revA2_charger_labels/`含baseline/candidate/final、invariants.json、官方日志、PDF/PNG、visual_verdict.json和70项OPEN队列。

下一步处理正面MCU与上部去耦密集区域25项重叠/42项压铜。3项连接区courtyard、采购型号/极性、Pogo/板厂工艺、当前板壳体3D、最终ELF与板上验证仍开放。
