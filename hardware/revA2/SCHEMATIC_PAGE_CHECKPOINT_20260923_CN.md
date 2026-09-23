# 原理图页面与遗留NC标记检查点 · 2026-09-23

原理图SHA256 `bf6beebad431a6f4aeb95cebcc88d191e6233e9195328fe1e88f587395871628`；PCB未改，仍为D1修复后的`6399dd180a5b50c9931cfed0662c3caf641f06213e151ca5037d261392fa9602`。官方ERC0错误/0警告，DRC0错误/0未连接/0一致性问题、3项courtyard。NOT_FAB_RELEASED。

## 实际修改与发现

原图内容延伸至y=292.1mm，A4横向页裁掉下部器件。改为A3纵向，43器件进入页框。43个Population字段仅隐藏显示，BOTH/AWA/UNDERWATER值及导出数据完整保留，避免其与Reference重叠。

隐藏字段后的候选ERC可重复出现no_connect_connected；paper-only候选和基线ERC0，fields-only重复出现该警告。没有据此宣称KiCad随机出错：独立解析符号引脚坐标和官方网表，发现6个真实矛盾的遗留NC叉号：U2.13 SCL=/I2C_SCL、U2.12 CS=/3V3、U3.1 SDA=/I2C_SDA、U4.15 DVDD=/3V3、U4.14 SDIO=/I2C_SDA、U7.5 OUT=/3V3。删除上述错误叉号，不删网络、不更改引脚类型、不禁用检查。保留U6.1 STAT、U4.4 VIN2N、U4.5 VIN2P的3个有效叉号。未进一步确认字段显示为何影响官方ERC检出，不作原因推断。

## 证据与命令

- `python3 validation/revA2_schematic_page/edit.py`：独立副本改纸张/显示；该初始脚本生成的中间态仍包含旧NC，正式采用的是后续修正后的candidate/final快照。
- `python3 validation/revA2_schematic_page/audit_nc.py`：逐一匹配NC坐标、符号引脚、官方网表，before_no_connect_audit.json/removed_stale_nc.json及最终no_connect_audit.json保留证据。
- 官方`sch erc --format json --severity-all --units mm`、`sch export netlist --format kicadxml`：修正后ERC0，组件值/符号/封装/Population及全部网络节点、pinfunction、pintype与基线一致。
- `python3 validation/revA2_schematic_page/verify.py`：逐项语义及限定文本增量、PCB逐字节不变通过。
- 官方`sch export pdf`及Poppler：after_REVIEW.pdf/after.png已查看。仅页面范围和字段重叠阶段通过，IC内部文字仍拥挤。
- 正式采用后`bash tools/export_fab_revA2.sh --check-only`与官方XML网表刷新：exit0，ERC/DRC上述结果。
- `python3 tools/validate_revA2.py`、`python3 tools/check_bom_revA2.py --output validation/revA2_schematic_page/bom_consistency.json`：exit0，43位号一致性、D1极性语义及Rev.A1哈希通过。

修改原理图与导出报告/网表、交接入口；PCB、库和固件未改，未重复固件测试。baseline/candidate/final及两项分离实验保留在validation/revA2_schematic_page。fab_export不存在。

下一步处理IC内部引脚名/网络标签拥挤，继续保证网络不变。采购、courtyard、当前3D/装配图、最终链接和实机门槛仍开放。
