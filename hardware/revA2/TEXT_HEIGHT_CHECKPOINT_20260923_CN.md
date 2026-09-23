# 丝印字高修复检查点 · 2026-09-23

正式PCB SHA256 `39bdedc6446b4bd534346a653720c766603e43de0f0e1a4d98228ad0518ef74a`。KiCad10.0.6官方ERC0错误/0警告，DRC0错误/0未连接/0一致性问题、82警告；NOT_FAB_RELEASED。

## 修改范围

仅三个Reference字段，保持原丝印面与可见状态，统一字高/宽0.8mm、笔画0.12mm：

| 位号 | 原字高 | 新位置mm | 角度 |
|---|---:|---|---:|
| U2 | 0.7mm | (2.0,1.6) F.SilkS | 0° |
| SW1 | 0.6mm | (5.0,18.4) B.SilkS | 0° |
| J2 | 0.65mm | (2.9,13.6) B.SilkS | 90° |

位号移入邻近空白区；不移动器件、不调整走线或焊盘、不修改规则。字段块剔除后的PCB逐字节一致，原理图/项目逐字节一致。

## 官方结果与图面检查

独立副本官方DRC：89→82警告。text_height 3→0，silk_overlap 30→27，silk_over_copper49→48；silk_edge_clearance4、missing_courtyard3不变。按type及关联UUID比较，无新增违规。

正反面官方PDF（F/B.SilkS、F/B.Mask、Edge.Cuts）经现有Poppler渲染并查看，三个加大位号可辨认、无开窗重叠。仅本组局部图面通过，其余冲突仍待处理；不宣称装配后全部位号可见。

## 实际命令与证据

- KiCad内置Python运行`validation/revA2_text_height/edit.py`：独立副本调整。
- `kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_text_height/candidate/drc_revA2_kicad10.json validation/revA2_text_height/candidate/smart_apo_common_revA2.kicad_pcb`：0错误/0未连/82警告。
- `python3 validation/revA2_text_height/verify.py`：仅三个Reference改动、无新增DRC，exit0。
- 正式采用后`bash tools/export_fab_revA2.sh --check-only`：exit0，ERC/DRC上述结果。
- `python3 tools/validate_revA2.py`：exit0，Rev.A1哈希未变。

证据在`validation/revA2_text_height/`：baseline/candidate/final、invariants.json、main_checks.log、validation.log、正反面PDF/PNG、visual_verdict.json、82项OPEN的warning_queue.csv。未修改固件，未重复固件测试，fab_export不存在。

## 下一步及阻塞

文字高度类别已关闭。继续D1/R9/底部极性轮廓的相关丝印组，随后其余重叠/压铜；J1/J2/J3 courtyard需实际连接与装配输入。Pogo接触公差、板厂能力、所购器件与电芯/电容资料、当前板壳体3D干涉、最终ELF及实物验证仍开放。
