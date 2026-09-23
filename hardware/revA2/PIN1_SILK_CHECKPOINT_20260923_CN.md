# 1脚方向丝印检查点 · 2026-09-23

正式PCB SHA256 `5d1f8a7a330c3bbbf86d8e15930d2b26694e2a207ddf2a994f410223839efa94`。官方KiCad10.0.6 ERC0错误/0警告、DRC0错误/0未连接/0一致性问题、3警告；NOT_FAB_RELEASED。

## 方向标记修复

U1三角形整体(0,-0.43)mm平移，尖端由(2.14,10.27)到(2.14,9.84)，仍右向、处于1脚左上方；U5整体(+0.55,0)mm平移，尖端由(10.81,3.94)到(11.36,3.94)，仍左向指示1脚。顶点逐一比对：三顶点采用同一位移，形状/尺寸/方向保持。距尖端最近的同封装编号焊盘均为1；U5独立钢网开口无编号，初次检查误计为空编号“焊盘”，已修正为检查编号电气焊盘，未改实际几何或DRC规则。

U1首轮上移0.57mm与Y1丝印冲突，被拒绝；本轮下修0.14mm后通过。try1报告与图保留。正反面官方PDF/PNG均查看，标记可辨认，无新增冲突。不替代所购物料封装1脚外观与实际贴装核验。

U1建立项目变体TSSOP-20_4.4x6.5mm_P0.65mm_RevA2_Pin1，原理图/PCB引用同步；U5原项目WSON库同步。标准全局库未改。板内除两处授权多边形和U1库ID外逐字节一致；原理图只改U1 Footprint ID，项目不变。铜/焊盘/走线/器件位置/钢网/阻焊不变；官方库一致性通过。

## 实际验证

- KiCad内置Python运行`validation/revA2_pin1_silk/inspect.py`、`edit.py`、`geometry.py`；geometry.json记录逐顶点位移与1脚位置。
- `kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_pin1_silk/candidate/drc_revA2_kicad10.json validation/revA2_pin1_silk/candidate/smart_apo_common_revA2.kicad_pcb`：0错误/0未连/3警告。
- `python3 validation/revA2_pin1_silk/verify.py`：修改范围及无新增type/UUID违规通过。
- 正式采用后`bash tools/export_fab_revA2.sh --check-only`：exit0，ERC/DRC上述结果。
- 官方`sch export netlist --format kicadxml`刷新netlist_revA2_kicad10.xml：exit0。
- `python3 tools/validate_revA2.py`：exit0，Rev.A1哈希保持，fab_export不存在。

silk_over_copper2→0，剩missing_courtyard3，总5→3。所有丝印DRC类别清零，无规则忽略/排除。证据目录`validation/revA2_pin1_silk/`包含baseline/candidate/final、invariants.json、geometry.json、日志、PDF/PNG、visual_verdict.json和3项OPEN队列。

修改PCB、原理图U1封装引用、新TSSOP项目库、WSON库与库README，刷新网表/官方报告/校验报告和交接入口。固件未改未重测。

## 下一步/未放行理由

J1/J2/J3缺courtyard仍OPEN：需实际电池线径/焊接与应力释放、Pogo探针和定位公差、桥路线束装配输入，不能凭丝印矩形推定占用。继续核验数字制造/装配文件准备、所有极性、实际采购资料、当前板壳体3D及固件构建/实物验证。当前不是FAB_RELEASED；即使电气与丝印检查通过，也不自动导出生产文件。
