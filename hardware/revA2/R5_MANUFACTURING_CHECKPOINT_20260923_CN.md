# R5焊盘内孔修复已采用 · 2026-09-23

当前PCB SHA256 `863e7861d7c7f443bb61643b22afbcb1abd0bf48b0ee2f91ddb16c7f69ef6d36`。NOT_FAB_RELEASED。

## 审批状态与改动

先前审批服务额度错误确实使命令未执行。本轮读取账户状态显示普通使用允许后，沿相同require_escalated审批路径重试成功；未换执行路径或通过别的代理绕过审批。该临时工具阻塞现已解除，不能继续把旧错误写成当前状态。

采用validation/revA2_r5_via/stage3：R5移至F(10.45,19.25)，VBAT_SENSE连接端点同步；地via保留(10.7,18.1)，通过0.20mm显式引线连接R5地焊盘。REED via从(11.15,19.9)微移到(11.25,19.9)，连接铜同步。移除连动中收缩成零长度的REED线段。未改R5阻值、焊盘网络、原理图、封装库、板框或规则。

72个过孔的只读焊盘审查：中心在焊盘内的项6→5，R5已无任何铜环/焊盘包围框重叠。剩余3处元件焊接焊盘（U4.13、U1.20、D1.2）和2处Pogo接触焊盘（J2.7、J2.5），均保持开放，不能推定已具备填孔/盖孔或接触工艺。更新清单validation/revA2_via_pad_audit/report.json和open_pad_center_items.csv，旧6项基线以pre_r5文件保留。

## 实际检查

- KiCad内置Python运行edit.py生成独立stage3、check_invariants.py、check_new_copper.py、tools/check_reference_revA2.py及via-pad audit，均退出0。零长度变更线段已为0。
- R5分压到MCU、R5地到MCU地、SW1到MCU及上拉电阻的实际铜BFS全通过；1821个实际线宽中心/双边采样的缺口仅局部同网via，最大半径0.45mm。六敏感网、In1连续轮廓及原外层增量参考检查通过。
- 采用后运行 `bash tools/export_fab_revA2.sh`：官方KiCad10.0.6 ERC0错误/0警告；普通DRC错误0、2未连接、122警告、一致性0。脚本退出2，拒绝生产Gerber/钻孔/CPL。
- `python3 tools/validate_revA2.py`与`python3 tools/check_divider_revA2.py --output validation/revA2_r5_via/divider_consistency.json`完成，Rev.A1哈希保持、分压跨文件一致。
- `python3 validation/revA2_r5_via/summarize.py`保存分类/位置队列及final快照。baseline为采用前完整回退点，main_gate.log为本轮主板复检证据。

stage1因错误地让地孔随R5移动产生1项clearance；stage2普通错误0但含收缩零长线；仅stage3采用。普通DRC计数前后不变，本组解决的是普通DRC不会阻止的焊盘内孔制造问题，不把此改动误称为关闭未连接。

## 剩余任务

仍需完成IMU_INT、MOSI两个连接，5个焊盘/接触孔与122警告/忽略项审查。已有STEP导出绑定R5移动前的板散列，尚不是当前装配快照，且仍缺7个模型/Y1路径失效；不能用于宣称当前3D干涉通过。

最终ELF、运行库及板上栈水位/总线/模拟性能未验证；所购CT05、电芯和Rev.A2壳体输入仍开放。本轮未改固件源代码，未重跑其行为测试。目标未完成。
