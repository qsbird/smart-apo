# 工作BOM跨文件一致性检查 · 2026-09-23

本阶段不修改PCB、原理图或固件。板SHA256 `5d1f8a7a330c3bbbf86d8e15930d2b26694e2a207ddf2a994f410223839efa94`保持；此前官方ERC0/0、DRC0错误/0未连/3项courtyard仍适用于同一板。NOT_FAB_RELEASED。

## 已修正的工作BOM差异

- C7原列在1µF组，正式原理图/PCB/网表为100nF。拆为独立100nF X7R行，AWA0、UNDERWATER1；1µF组变为C6/C9/C10，AWA2、UNDERWATER3。
- C11/C12工作BOM历史标注0603，正式设计为0402；纠正封装引用并明确4.7µF有效容量/充电稳定性仍未由准确MPN证明。
- 全部BOM封装字段使用正式网表的完整库ID，包括已修正的U2几何、U1/D1项目变体及其余项目封装，消除简写/过期名称歧义。
- 不改变设计器件值、板上封装尺寸、数量或装配变体；只是工作BOM与当前正式设计一致。

新增`tools/check_bom_revA2.py`读取工作BOM、ASSEMBLY_VARIANTS_revA2.csv、官方网表：检查唯一位号与43器件覆盖、阻容标称值、完整Footprint ID、Population与变体状态、分组数量。MANUAL/PCB_ONLY计数表示存在的线焊接口/PCB焊盘组，不是应采购的SMT连接器数量。该工具不验证供应商编号、准确MPN适配、容差、电压/温度降容或极性。

## 实际命令及结果

```sh
python3 tools/check_bom_revA2.py --output validation/revA2_bom_audit/consistency.json
python3 -m unittest discover -s tools/tests -v
```

一致性PASS_DESIGN_CONSISTENCY_ONLY，43/43、issues为空。15项工具测试通过，其中新增6项覆盖当前数据以及C7错误值、C11/C12错误封装、错误变体数量、重复/缺失位号、Population冲突的拒绝。旧工作BOM回放检测到44条不一致（多数为简写封装ID，并非44个电路错误），包括C7实际值差异。未重复运行无改动的PCB/ERC或固件测试。

改动文件：BOM_revA2_WORKING.csv、tools/check_bom_revA2.py、tools/tests/test_check_bom_revA2.py及本报告/交接入口。证据目录含BOM_before/after.csv、before_consistency.json、consistency.json（输入哈希）、tests.log。未输出最终生产BOM/CPL或Gerber。

## 仍开放的采购阻塞

- U5工作BOM LCSC列C97522，但备注另列C5334276，不能将两者当已确认相同采购项；下单前需要所购/批准目录项与W25Q256JVEIQ核对。
- Q1仍有2N7002/DMN1019USN-7替代选择；D1无准确MPN、极性/光学规格未闭合。
- SW1所购CT05图纸、Y1准确晶体CL/驱动规格、C15/C16匹配仍开放。
- C9/C10、C11/C12等MLCC的准确MPN与有效容量未闭合；纠正0402字段不证明0402的4.7µF能满足稳压/充电条件。
- 401020保护电芯规格/允许充电电流、Pogo/线焊实际占用、核心采购后缀、壳体与3D、ARM链接器/运行库及样机仍缺。

下一步继续核对极性与实际采购输入，保持装配及制造放行门槛。
