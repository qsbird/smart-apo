# 板边位号修复检查点 · 2026-09-23

正式板SHA256 `fa38809ccc750336f8503c63c2a48684849fb06323a0fba8f29cd6642cd94c3b`。官方KiCad10.0.6 ERC0错误/0警告，DRC0错误/0未连接/0一致性问题、89警告；NOT_FAB_RELEASED。

## 改动及证据

仅修改正式PCB中的四个Reference字段：U4(6,24.4)、C6(4.2,19.6)、C16(5.5,11.8)、R6(6,31.1)mm，均F.SilkS、0°、0.8mm字高、0.12mm线宽。严格删除四个授权字段块后前后PCB逐字节一致；铜、焊盘、器件位置、规则不变，项目与原理图不变。没有重新生成PCB。

DRC分类：silk_edge_clearance 8→4、silk_over_copper 51→49；silk_overlap30、text_height3、missing_courtyard3不变。95→89，无新增项。每项按type及关联UUID比较，不只是总数下降。

D1在副本中尝试(1.1,28.4)、(1.1,29.0)均被拒绝：分别新增U4阻焊开窗冲突、R9文字重叠。正式D1保留原位；后续需与底部R9及极性轮廓共同调整。try1/try2报告与图保留。

官方PDF导出F.SilkS/F.Mask/Edge.Cuts，Poppler渲染并检查裸板图面，四个位号可辨认。U4和C16位号位于U4/U1器件本体投影内，装配后可能遮挡；本次图面复核不证明装配后检修可视性，需装配图支持。局部visual-verdict通过，不代表全板验收。

## 实际命令

- KiCad内置Python运行 `validation/revA2_edge_labels/edit.py`，只修改副本。
- `kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_edge_labels/candidate/drc_revA2_kicad10.json validation/revA2_edge_labels/candidate/smart_apo_common_revA2.kicad_pcb`：0错误/0未连/89警告/0一致性问题。
- `python3 validation/revA2_edge_labels/verify.py`：字段不变量及无新增DRC通过。
- 采用后 `bash tools/export_fab_revA2.sh --check-only`：exit0，ERC/DRC上述结果。
- `python3 tools/validate_revA2.py`：exit0；Rev.A1哈希保持。未改固件，未重复固件测试。

证据目录 `validation/revA2_edge_labels/` 包含baseline/candidate/final、invariants.json、main_checks.log、validation.log、after_REVIEW.pdf、after.png及逐项warning_queue.csv。正式修改仅PCB，另更新校验报告、检查点和交接入口。fab_export不存在。

## 下一步与阻塞

继续3项文字高度、D1/R9关联布局与其余丝印冲突；3项连接区courtyard仍需实际装配输入。Pogo接触尺寸/定位公差、板厂能力、所购CT05/401020/核心器件后缀/电容资料、当前板壳体3D、最终ELF及实物验证仍开放。旧STEP不作为当前干涉证据。
