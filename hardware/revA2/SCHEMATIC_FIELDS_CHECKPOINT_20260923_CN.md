# 原理图字段与J2排版检查点 · 2026-09-23

原理图SHA256 `86ee643ee4eeb41a695799a4e04cd8326cfbf73297e3f66c30735fcbef4c81fa`。PCB未改。官方ERC0错误/0警告，DRC0错误/0未连接/0一致性问题、3项courtyard；NOT_FAB_RELEASED。

29个阻容共58个Reference/Value字段：字高1mm，分别位于中心下/上4.8mm，显示文本与元件值不变。J2的CONN7框半宽10.16mm，高度和引脚间距加倍，7个外部标签同步，网格对齐。七个IC及CONN7的库默认Reference/Value同步移到当前框外，原理图缓存一致；上阶段记录的新放置默认字段问题已关闭。

限定坐标/显示字段的AST对比通过；引脚编号/名称/类型、元件值、封装、Population及官方网表components/nets XML逐字节一致。PCB/项目逐字节不变。官方整页PDF与300dpi阻容局部渲染已查看：字段无行间重叠，J2引脚清楚分列。

实际命令：

- `python3 validation/revA2_schematic_fields/edit.py`：独立副本修改。
- 官方`sch erc --format json --severity-all --units mm`、`sch export netlist --format kicadxml`、`sch export pdf`：候选ERC0、网表一致、PDF保存。
- `python3 validation/revA2_schematic_fields/verify.py`：限定AST/网络/PCB不变量通过。
- 采用后`bash tools/export_fab_revA2.sh --check-only`和官方XML网表刷新：exit0，ERC/DRC上述结果。
- `python3 tools/validate_revA2.py`、`python3 tools/check_bom_revA2.py --output validation/revA2_schematic_fields/bom_consistency.json`：exit0，Rev.A1及43位号BOM一致性通过。

修改正式原理图、项目符号库及导出报告/交接文档，PCB和固件未改。证据validation/revA2_schematic_fields包含baseline/candidate/final、field_changes.json、pin_moves.json、verification.json、日志、after_REVIEW.pdf、整页/局部PNG和visual_verdict.json。无生产制造导出。

下一步刷新D1旋转后过期的装配/3D审查件，汇总最终数字交付门槛与实际外部阻塞。仍缺连接工艺courtyard、准确采购及模型/壳体、ARM链接器/运行库和样机验证，不能FAB_RELEASED。
