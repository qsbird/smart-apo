# 原理图网络标签对齐 · 2026-09-23

原理图SHA256 `b60133886bdf6764acd328d4abbb64ebc09090178012ca96b16b557319c8f1fb`。148个网络标签统一角度0°：原左侧180°标签改为right bottom，原右侧0°标签改为left bottom，使文字朝器件外侧展开。锚点、文本、UUID、其他内容不变。PCB逐字节不变，库/固件未修改。

官方候选ERC0；候选/基线官方网表components与nets XML段逐字节一致。verify.py将且仅将标签的角度/justify归一化后，原理图逐字节一致。官方PDF+Poppler渲染查看，外部网络标签不再挤进器件内部。本阶段局部视觉通过；IC内部长引脚名及相邻阻容Reference/Value仍需修整，整张图尚未宣称审核完成。

实际命令：

- `python3 validation/revA2_label_alignment/edit.py`：独立副本，仅文本对齐。
- 官方`sch erc --format json --severity-all --units mm`、`sch export netlist --format kicadxml`、`sch export pdf`：候选ERC0，网表/图面输出保存。
- `python3 validation/revA2_label_alignment/verify.py`：148标签锚点/文本/UUID、网表及PCB不变量通过。
- 正式采用后`bash tools/export_fab_revA2.sh --check-only`：exit0，ERC0错误/0警告；DRC0错误/0未连/0一致性问题、3项courtyard。
- 官方网表刷新、`python3 tools/validate_revA2.py`、`python3 tools/check_bom_revA2.py --output validation/revA2_label_alignment/bom_consistency.json`：exit0，Rev.A1保持、43位号BOM一致。

修改原理图与报告/网表/交接入口；证据目录validation/revA2_label_alignment含baseline/candidate/final、verification.json、PDF/PNG、官方日志和visual_verdict.json。fab_export不存在，NOT_FAB_RELEASED。采购、装配、3D、最终固件与实机门槛仍开放。
