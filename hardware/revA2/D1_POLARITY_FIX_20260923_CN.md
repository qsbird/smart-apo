# D1极性修复检查点 · 2026-09-23

正式PCB SHA256 `6399dd180a5b50c9931cfed0662c3caf641f06213e151ca5037d261392fa9602`。D1内部数字极性约定冲突已修正，所购LED实际外形/标记核验仍开放。官方ERC0错误/0警告，DRC0错误/0未连接/0一致性问题、3项courtyard警告；NOT_FAB_RELEASED。

## 最终修复

D1不再使用PASSIVE2。新增项目符号LED_AK_REVA2，从本机KiCad Device:LED派生镜像图形、延长引脚到既有±7.62mm端点，保持原理图导线/标签位置：左侧2=A接LED_A，右侧1=K接LED_K。原理图嵌入定义与项目库一致，LED图形明确显示二极管方向。

PCB D1旋转180°（90°→270°，API规范化为-90°），新项目封装LED_0805_2012Metric_RevA2_K1。上下焊盘的物理网络保持：上方(2.3,31.7125)mm现在为1/K/LED_K，下方(2.3,33.5875)mm为2/A/LED_A。阴极丝印与Fab端标、3D模型方向随封装同步旋转。位号保持原位置。没有重新布线。

独立geometry.py按物理坐标比较两焊盘：位置、尺寸、边界框、圆角比、层集、阻焊裕量与网络完全一致，仅编号互换；模型局部旋转未变、全局随封装转180°。PCB剔除D1封装块后逐字节一致；原理图除新增符号与D1两个引用外一致；网表只变D1编号，所有其他网络节点保持。确认R6.2→D1.2/A、D1.1/K→Q1.3漏极。

旧EdgeSilk封装作为历史保留，不能用于当前D1。工作BOM已同步K1封装。历史生成脚本仍可能重建PASSIVE2/旧极性，未执行；不要在已修复工程上运行重新生成。

## 实际检查

- 独立候选`kicad-cli sch erc --format json --severity-all`：0违规；`sch export netlist --format kicadxml`成功。
- 独立候选`kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity`：0错误/0未连/3项courtyard。
- `python3 validation/revA2_led_polarity_fix/verify.py`：电路修改范围与网表一致性通过；KiCad内置Python运行geometry.py：物理焊盘/网络不变量通过。
- 官方PCB与原理图PDF经Poppler渲染并查看，D1符号与阴极侧一致；并非全图视觉验收。首轮候选符号重命名错误曾导致加载失败，修正后重新执行所有检查；未把失败当通过。
- 正式采用后`bash tools/export_fab_revA2.sh --check-only`及官方XML网表导出：exit0，ERC/DRC上述结果。
- `python3 tools/validate_revA2.py`：exit0，Rev.A1保持。
- `python3 tools/check_bom_revA2.py --output validation/revA2_led_polarity_fix/bom_consistency.json`：43位号一致性及新D1 K_1/A_2语义通过。
- `python3 -m unittest discover -s tools/tests -v`：17项通过，新增两项极性回归拒绝编号颠倒及无极性PASSIVE语义退化。

工具输出在validation/revA2_led_polarity_fix/：baseline/candidate/final、verification.json、geometry.json、PDF/PNG、日志、tests.log。修改PCB/原理图/项目符号库、新K1封装、工作BOM、库README、BOM检查工具与测试、官方/离线报告及交接文档。固件未改未重测，fab_export不存在。

## 后续与边界

采购准确LED型号及实际K/A外观、光学和额定电流仍未核验；本次仅关闭设计内部冲突。旧STEP及装配图对应旧D1旋转，必须从最终板重导出并审核。原理图整页PDF暴露既有器件越页和标签拥挤，完整可审核图面需修整，不得仅凭ERC0称为完成。三个连接区courtyard、准确采购/工艺、3D、最终ELF和实机门槛仍开放。
