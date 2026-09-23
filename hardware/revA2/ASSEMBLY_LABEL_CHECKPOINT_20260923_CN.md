# 装配位号覆盖检查点 · 2026-09-23

正式PCB SHA256 `5c6c6cb8134fcbc620c9eb22a98f85be26f280167b6e134c9233ffcfd164d30d`。官方ERC0错误/0警告、DRC0错误/0未连接/0一致性问题、50警告；NOT_FAB_RELEASED。

U2/U3/SW1/J1/J2/J3缺少Fab `${REFERENCE}`，此次在器件原点补充0.8mm字高/0.12mm笔画标识，保持各自正反面及镜像方向，并同步六个项目封装库。现在43个封装各有一个Fab位号，现有37个标识未改变。PCB除了新增六个Fab文本外内容一致（仅归一化空白），每个库除了一个Fab文本外一致；原理图/项目逐字节一致。制造层丝印、铜、焊盘、走线、规则均未改变。

修改PCB及项目库：PAD_6x1.27mm、LPS28DFW_CCLGA-7L、LGA-14_3x2.5mm_P0.5mm_LSM6DSO、REED_CT05_COMPACT、POGO_7x1.27mm、BATTERY_WIRE_PADS；完整相对路径在证据adopted_files.json。另刷新官方/离线报告和交接入口。

实际工具：

- KiCad内置Python运行`validation/revA2_assembly_labels/inspect.py`、`edit.py`，清点43个封装并在独立副本补齐；首次LIB_ID Format调用不兼容已修正后重跑，失败不计通过。
- `kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_assembly_labels/candidate/drc_revA2_kicad10.json validation/revA2_assembly_labels/candidate/smart_apo_common_revA2.kicad_pcb`：0错误/0未连/50警告；每项type/UUID集合与基线完全相同。
- `python3 validation/revA2_assembly_labels/verify.py`：六项Fab增量、既有内容/库增量/DRC集合检查通过。
- 官方`pcb export pdf`分别输出F.Fab/Edge.Cuts与B.Fab/Edge.Cuts，后者镜像，均exclude-value、scale5；Poppler渲染并查看。front_REVIEW.pdf与back_REVIEW.pdf的新增标识均可辨认。
- 正式采用后`bash tools/export_fab_revA2.sh --check-only`：exit0，官方ERC/DRC上述结果。
- `python3 tools/validate_revA2.py`：exit0，Rev.A1哈希保持，fab_export不存在。

证据`validation/revA2_assembly_labels/`包括baseline/candidate/final、before/after_inventory.json、invariants.json、正反面PDF/PNG、review_manifest.json、官方日志及50项OPEN队列。固件未改未重测。

这次只关闭装配位号缺失。图中原位标签能定位此前不印刷丝印的五个器件，但尚未完成装配变体、所有针脚/极性、实购物料与完整工艺标注核验；不能将位号覆盖当成装配放行或机械干涉通过。仍须处理18项丝印重叠/29项压铜/3项缺courtyard，以及采购、板厂、当前3D、最终ELF和板上验证。
