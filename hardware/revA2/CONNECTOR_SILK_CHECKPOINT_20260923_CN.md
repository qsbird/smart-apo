# J2/J3丝印轮廓检查点 · 2026-09-23

正式PCB SHA256 `146b85a298fe51a1330474656d7318dcf9f9357f232ff399242d1a810aaf2057`。官方ERC0错误/0警告、DRC0错误/0未连接/0一致性问题、5警告；NOT_FAB_RELEASED。

J2/J3丝印矩形长轴两端各外移0.25mm。J2局部x范围±4.25→±4.5mm；J3±3.62→±3.87mm，宽轴±0.8mm、线宽0.12mm保持。正式板及POGO_7x1.27mm/PAD_6x1.27mm两个项目库同步。剔除两处授权矩形后PCB逐字节一致，库除对应矩形外逐字节一致；原理图/项目不变。铜、焊盘、钢网、阻焊、位号和Fab标识不变。

官方silk_over_copper6→2，missing_courtyard3不变，总9→5，无新增type/UUID违规。正反面PDF/PNG已查看，轮廓与开窗有间隔且位于板内，不改变连接器方向。丝印边界不代表焊线/接触工艺空间通过。

实际命令：

- KiCad内置Python执行`validation/revA2_connector_silk/edit.py`，独立副本试验。
- `kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_connector_silk/candidate/drc_revA2_kicad10.json validation/revA2_connector_silk/candidate/smart_apo_common_revA2.kicad_pcb`：0错误/0未连/5警告。
- `python3 validation/revA2_connector_silk/verify.py`：修改范围、项目库增量与无新增项通过。
- 正式采用后`bash tools/export_fab_revA2.sh --check-only`：exit0，官方ERC/DRC上述结果。
- `python3 tools/validate_revA2.py`：exit0，Rev.A1哈希保持，fab_export不存在。

改动PCB、两个库、报告及交接入口，固件未改未重测。证据`validation/revA2_connector_silk/`包括baseline/candidate/final、invariants.json、日志、正反面PDF/PNG、visual_verdict.json及5项OPEN队列。

下一步单独核对U1/U5方向多边形的2项压铜，不直接删掉方向标记。J1/J2/J3 courtyard、采购型号/极性、工艺公差、当前3D及固件/实物验证仍开放。
