# 两端 SCL 焊盘内孔修复 · 2026-09-23

当前PCB SHA256 `598d81277ade894bb31da66b5833054f37bb52f5e2322747a937ee7d5041009d`。NOT_FAB_RELEASED。

## 两组分别采用

ADC组：原U4 pad13内SCLvia(5.365,21)移至(6.05,19.4)，B端缩短，F经(6.05,20)→(5.365,20.685)接ADC。焊盘内中心5→4。全SCL五器件实际铜连通，1776点新铜参考检查仅自身via局部缺口，最大0.45mm。

MCU组：原U1 pad20内SCLvia(9.55,10.25)移至(9.95,10.3)；相邻NRSTvia(10.2,11)微移(10.25,11)并同步线端。为避让，C17地via(9.8,9.5)移至(9.55,9.4)，显式地线从(10.8,9.92)经(10.6,9.92)接新位置。移除NRST连动后收缩的零长度线段。焊盘内中心4→3。全SCL、C17信号至复位脚、C17地至主地BFS通过；1341点变更铜按实际线宽采样，局部同网via缺口最大0.451169mm（按0.45mm反焊盘加0.01mm离散容差审查）。

两组均未移动器件或改网络/原理图/库/规则；只是过孔及其关联铜线。四层1mm、12×35mm、43封装不变。未覆盖Rev.A1。

## 官方与工具证据

| 检查点 | 普通DRC错误 | 未连接 | 警告 |
|---|---:|---:|---:|
| 本轮起点 | 0 | 2 | 122 |
| ADC组采用后 | 0 | 2 | 122 |
| MCU stage1，拒绝 | 1 | 2 | 122 |
| MCU stage2，拒绝 | 3 | 2 | 122 |
| MCU stage3，含零长线未采用 | 0 | 2 | 122 |
| MCU stage4及主板复检 | 0 | 2 | 122 |

stage1为C17地线间距，stage2为新地孔与R11/NRST间距和孔间距；只有解决后版本采用。两组均分别执行 `bash tools/export_fab_revA2.sh`：官方KiCad10.0.6 ERC0错误/0警告，一致性0，脚本exit2拒绝生产Gerber/钻孔/CPL。

分别用KiCad Python执行check_invariants.py、check_new_copper.py、tools/check_reference_revA2.py（显式Fill）、validation/revA2_via_pad_audit/audit.py；候选最终结果通过限定几何/连接审查，六敏感网与未改外层铜无新增参考缺口。两处SCL焊盘在审查中均不再出现铜环/包围框重叠。几何报告不证明EM/工艺/板上性能。

另运行 `python3 tools/validate_revA2.py`、`python3 tools/check_divider_revA2.py --output validation/revA2_mcu_scl_via/divider_consistency.json` 及两组summarize.py。Rev.A1哈希保持，跨文件分压一致。完整baseline/final、逐阶段官方报告、分类/坐标队列在validation/revA2_adc_scl_via和validation/revA2_mcu_scl_via；主板复检日志main_gate.log可审计。

## 未采用的IMU试验

独立validation/revA2_imu_candidate中尝试U2移动及IMU跨层；官方新增14 items_not_allowed、10短路、5间距；254新线采样56点缺参考。尽管两个端点连接成立，候选仍不可采用，正式板未合入。后续必须整体重建U2对应径向逃逸并协调相关供电/地孔和U1侧NRST，不能原样重试只移动封装/端点的策略。

## 仍开放

实际未连接仍为IMU_INT和MOSI各1处。焊盘内中心剩D1.2（LED焊接）及J2.7/J2.5（Pogo接触）共3处，处置表validation/revA2_via_pad_audit/open_pad_center_items.csv已更新；此前5项基线另存pre_scl_via_repairs文件。近焊盘铜环还需阻焊/装配审查。

122警告、5类忽略检查、最终ELF/板上测试、所购器件电芯资料及壳体/3D仍未完成。现有STEP散列对应更早版本，不是本轮位移后的装配快照。固件本轮未改未重测。制造状态不变。
