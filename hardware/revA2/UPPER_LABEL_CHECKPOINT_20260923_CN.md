# 上部位号处置检查点 · 2026-09-23

正式PCB SHA256 `fec719f8351f73be649e56da19361472f0e54fb38c1620be724f024f35ebc2f6`。官方ERC0错误/0警告，DRC0错误/0未连接/0一致性问题、9警告；NOT_FAB_RELEASED。

仅八个Reference字段变化：U1/U7移至各自器件原点（U1 0°、U7 90°，0.8mm字高/0.12mm笔画）；C10/C15/R2/C9/R12/Y1丝印Reference设为不可见，保留原位F.Fab `${REFERENCE}`。自身体内丝印装配后可能遮挡，六个小器件位号不印刷，检修依赖最终装配图。已导出并查看silk_REVIEW.pdf及assembly_REVIEW.pdf，六个Fab位号均可定位；不将取消印刷说成装配后可见。

剔除八个授权Reference块后PCB逐字节一致，原理图/项目逐字节一致；器件位置、铜、焊盘、规则及Fab原样不变。没有DRC忽略或排除。官方分类silk_overlap11→0、silk_over_copper22→6、missing_courtyard3不变，36→9，无新增项。

实际命令：

- KiCad内置Python执行`validation/revA2_upper_labels/edit.py`，独立副本试验。
- `kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_upper_labels/candidate/drc_revA2_kicad10.json validation/revA2_upper_labels/candidate/smart_apo_common_revA2.kicad_pcb`：0错误/0未连/9警告。
- `python3 validation/revA2_upper_labels/verify.py`：字段不变量及无新增项通过。
- 采用后`bash tools/export_fab_revA2.sh --check-only`：exit0，ERC/DRC上述结果。
- `python3 tools/validate_revA2.py`：exit0，Rev.A1哈希保持，fab_export不存在。

修改正式PCB及报告/交接入口；固件未改未重测。证据`validation/revA2_upper_labels/`含baseline/candidate/final、invariants.json、官方日志、丝印/装配PDF及PNG、visual_verdict.json和9项OPEN队列。

下一组修复J2/J3轮廓及U1/U5方向标志的6项压铜，不能直接删掉全部极性标记。连接工艺courtyard、实际器件/极性、板厂能力、当前3D、最终固件与实机验证仍开放。最终装配图须由最终板导出并复核，不得生产放行。
