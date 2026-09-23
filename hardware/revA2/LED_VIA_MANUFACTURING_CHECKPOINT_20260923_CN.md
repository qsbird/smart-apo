# LED 焊盘内孔修复与Pogo几何审查 · 2026-09-23

当前正式PCB SHA256 `290b73010d86ac8cf7f375690e45750d0bc05c6421a7d25c55932fa7b0851a81`。NOT_FAB_RELEASED。

## 已采用改动

D1阴极via由(2.3,31.7)移至(1.6,30.7)，0.60/0.30mm。F从D1 pad2(2.3,31.7125)接新via，B从Q1 pad3(1.2625,29.6)经(1.2625,30.3625)接新via，线宽0.25mm。删除原B层绕行的两段铜。器件、焊盘、网络、原理图、库、四层1mm、12×35mm及规则不变。

第一版向右移动碰到B电池焊盘J1.2，官方报clearance/shorting_items/hole_clearance/solder_mask_bridge各1项，拒绝。读取完整焊盘边界和In2桥路激励铜后构造stage2，通过再采用；没有改桥路或LSE。

## 实际工具证据

- KiCad Python edit.py、check_invariants.py、check_new_copper.py、tools/check_reference_revA2.py与via-pad audit均已运行。新LED铜756个真实线宽中心/双边采样，缺口仅自身via局部反焊盘，最大半径0.450220mm（离散几何）；D1.2到Q1.3的实际铜BFS连通。六敏感网、In1单轮廓、原外层铜无新增参考缺口。
- stage2审查不再有D1铜环/焊盘包围框重叠。72个via中，焊盘内中心3→2；剩余均为J2 Pogo接触孔。当前没有元件焊接焊盘内中心，但近焊盘铜环/阻焊/盖油工艺审查并未因此全部关闭。
- 采用后 `bash tools/export_fab_revA2.sh`：官方KiCad10.0.6 ERC0错误/0警告，普通DRC错误0、2未连接、122警告、一致性0；exit2拒绝Gerber/钻孔/CPL。
- `python3 tools/validate_revA2.py`与`python3 tools/check_divider_revA2.py --output validation/revA2_led_via/divider_consistency.json`完成，Rev.A1哈希保持、分压跨文件一致。
- `python3 validation/revA2_led_via/summarize.py`保存分类、位置修复队列和final快照。baseline为完整回退点；main_gate.log为官方主板结果。

## Pogo仍开放

当前J2.5 UART_TX及J2.7 NRST仍有偏置孔。新增只读pogo_geometry.py/json，直接从正式PCB读取pad/via中心和钻孔直径，在“有效接触区是以焊盘中心为中心的整圆”这一假设下，计算接触区与孔刚好相切时的直径：2×(中心距−孔半径−总径向定位误差)。该值没有制造余量，不是合格门槛；真实接触形状、中心、孔公差、镀层/磨损和治具误差未知，不能据此判定接触可靠。

已向用户异步询问所购Pogo型号/头部直径/治具定位公差；尚未收到资料，不作替代假设。更新处置表validation/revA2_via_pad_audit/open_pad_center_items.csv，旧3项以pre_led文件保留。

## 下一步

继续处理IMU_INT、MOSI两个实际开路，需相关扇出/局部铜成组重建，不能采用前次失败试验。其余122警告、忽略规则、Pogo接触、阻焊工艺、最终ELF/板上试验、采购器件电芯及壳体/3D资料仍未完成。既有STEP绑定旧版，不是本轮移动后的装配快照。固件本轮未改未重测。
