# D1板边丝印检查点 · 2026-09-23

正式PCB SHA256 `33df907ab6cf1ddd62f012da16388b9dba40117633d571ee1f606bb7e43282dd`。官方KiCad10.0.6 ERC0错误/0警告、DRC0错误/0未连接/0一致性问题、79警告。NOT_FAB_RELEASED。

D1位号移到(0.65,32.1)mm，F.SilkS、90°、0.8mm字高、0.12mm笔画。左侧轮廓从(1.34,31.65)至(1.34,34.335)缩短至(1.34,33.8)；底部横线起点从(1.34,34.335)改为(1.8,34.335)，右侧轮廓完整保留。保留原开放端方向，避开板角；不删除全部方向轮廓。

首轮出现lib_footprint_mismatch，未忽略。建立项目库`LED_0805_2012Metric_RevA2_EdgeSilk.kicad_mod`并同步PCB/原理图D1引用后消除该项。基于当前板标准LED封装派生，仅板框丝印适配，不声称匹配已采购LED。

字段级检查证明PCB除D1 Reference、两段授权fp_line和库ID以外逐字节一致；原理图只变一个Footprint引用；项目不变。铜/焊盘/走线/阻焊/钢网不变。D1仍是pad1=LED_A、pad2=LED_K；此网络对应与标准库方向标识、实际所购LED阴阳极必须在装配前明确核验，不能以DRC通过替代。

官方DRC：silk_edge_clearance 4→1，其他丝印重叠27、压铜48、缺courtyard3不变，82→79，无新增项。剩板边项是J1背面轮廓。官方PDF+Poppler图面显示D1位号可辨认、轮廓在板框内；局部图面通过，不作实物极性验收。

实际命令：

- KiCad内置Python运行`validation/revA2_bottom_silk/edit.py`、`library.py`，独立副本试验；库脚本先修正Duplicate参数和SWIG类型转换，失败日志未作为验证通过。
- `kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_bottom_silk/candidate/drc_revA2_kicad10.json validation/revA2_bottom_silk/candidate/smart_apo_common_revA2.kicad_pcb`：0错误/0未连/79警告。
- `python3 validation/revA2_bottom_silk/verify.py`：授权块以外一致，无新增DRC。
- 采用后`bash tools/export_fab_revA2.sh --check-only`：exit0，ERC/DRC上述结果。
- `kicad-cli sch export netlist --format kicadxml --output hardware/revA2/netlist_revA2_kicad10.xml hardware/revA2/smart_apo_common_revA2.kicad_sch`：exit0，刷新封装引用。
- `python3 tools/validate_revA2.py`：exit0，Rev.A1哈希保持。

修改正式PCB、原理图D1封装引用、新项目封装及库README，刷新网表/校验报告和交接入口。固件未改未重测；未生成fab_export。证据目录包含baseline/candidate/final、invariants.json、日志、PDF/PNG和79项OPEN的warning_queue.csv。

下一步处理J1板边轮廓、底部R8/R9关联丝印及其他剩余警告。采购型号/极性、连接工艺、公差、板厂能力、当前3D与最终固件及实机门槛仍开放。
