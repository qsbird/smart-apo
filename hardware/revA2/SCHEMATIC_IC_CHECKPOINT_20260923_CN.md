# IC原理图可读性检查点 · 2026-09-23

原理图SHA256 `1daefa5f5471e640647fb15b5db2dc9789018def75f4b4cf026661b0c25dbc69`。PCB未改。官方ERC0错误/0警告、DRC0错误/0未连接/0一致性问题、3项courtyard；NOT_FAB_RELEASED。

U1至U7的项目符号和原理图缓存同步扩大：MCU矩形半宽20.32mm，其余IC12.7mm；高度与引脚局部y间距加倍，引脚长度2.54mm保持。实例Reference/Value移到新框外。U1/U4/U5旧中心位于半格点，首轮扩展产生3项endpoint_off_grid，拒绝后连同标签同步对齐1.27mm网格。没有修改电气编号、名称、类型或变体。

75个引脚、69个相连标签/NC同步移动（pin_moves.json）。限定坐标变化后的AST一致；官方网表components/nets XML逐字节一致；PCB与项目逐字节一致。官方PDF/PNG查看，IC完整长引脚名及网络名已分列。剩余阻容Reference/Value、J2小型符号仍需改善；库默认Reference/Value位置尚为旧位置，仅当前实例已排好，新放置实例字段需重排。

实际命令：

- `python3 validation/revA2_ic_readability/edit.py`：从基线副本作限定局部修改，未调用整板生成器。
- 官方`sch erc --format json --severity-all --units mm`、`sch export netlist --format kicadxml`及`sch export pdf`：最终候选ERC0、网表/图面已检查。
- `python3 validation/revA2_ic_readability/verify.py`：限定AST、引脚语义/网络与PCB不变量通过。
- 正式采用后`bash tools/export_fab_revA2.sh --check-only`和XML网表刷新：exit0，ERC/DRC上述结果。
- `python3 tools/validate_revA2.py`、`python3 tools/check_bom_revA2.py --output validation/revA2_ic_readability/bom_consistency.json`：exit0，Rev.A1及43位号一致性通过。

修改正式原理图、项目符号库及报告/交接入口，PCB/固件未改，未重测固件。证据目录validation/revA2_ic_readability保存baseline/candidate/final、首次失败ERC/图、pin_moves.json、verification.json、官方日志与最终PDF/PNG。制造输出仍未生成。其余采购/装配/3D/最终固件/实机门槛开放。
