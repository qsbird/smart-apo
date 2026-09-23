# ADC SCL 连接检查点 · 2026-09-23

已采用stage3，主板SHA256 `1b107b735467401e9e3c740cd033305a7a1a90b10bf3aedef7c3753b80e3ccb6`；NOT_FAB_RELEASED。

## 正式改动

PCB完成MCU/U1 pad20、R2 pad1与ADC/U4 pad13的SCL连接，经过F/In2/B/F，新增0.60/0.30mm过孔(9.55,10.25)、(9.1,19.4)、(5.365,21.0)，线宽0.15mm。没有In1信号。

相关REED B铜改为明确的折线路径，保留R10上拉、SW1信号脚和MCU输入连接；In2下段向右绕行避让SCL。正式版本没有移动器件、过孔或修改焊盘网络/封装/制造规则。独立文本审核除segment/via/zone外均保持，四层、1mm、12×35mm、43封装不变。

初版误将SW1连接支路当作可移除铜，并碰到已有过孔，产生短路/开路；官方检查检出后拒绝，没有进入主板。补读全部焊盘后恢复SW1完整路径并逐点修复。前后回退副本baseline/final以及每次候选和变化清单在validation/revA2_adc_bus。

## 实际工具证据

| 检查点 | 普通DRC错误 | 未连接 | 警告 |
|---|---:|---:|---:|
| baseline | 0 | 6 | 120 |
| stage1，拒绝 | 13 | 7 | 121 |
| stage2，拒绝 | 1 | 5 | 120 |
| stage3与主板复检 | 0 | 5 | 120 |

stage1分类：shorting_items5、clearance6、solder_mask_bridge2；stage2为REED支路碰3V3via的shorting_items1，stage3局部绕开后清零。采用前后警告type/UUID集合无变化。

实际执行命令：

```sh
bash tools/export_fab_revA2.sh
python3 tools/validate_revA2.py
python3 tools/check_divider_revA2.py --output validation/revA2_adc_bus/divider_consistency.json
python3 validation/revA2_adc_bus/summarize.py
```

官方KiCad10.0.6 ERC0/0，DRC普通错误0、5未连接、120警告、一致性0。制造脚本退出2，未导出生产文件。validate确认Rev.A1哈希不变；分压跨文件一致性通过。详细日志main_gate.log、validation.log及分类/位置清单comparison.json、repair_queue.csv。

另以KiCad自带Python运行check_invariants.py和tools/check_reference_revA2.py（主板对本组baseline，输出main_reference.json），均退出0；显式填铜后In1地单轮廓，六敏感网及原有外层铜无新增参考缺口。本项只比较本轮增量，不取消既有局部供电过孔的历史审查说明。

独立复核通过实际连通图确认REED的SW1.1/R10.2/U1.16及原有两via连通；SCL的U1.20/R2.1/U4.13及三个新via连通。REED新12段1962点、SCL新9段2598点，以≤0.02mm步长采样中心和双边，缺失点仅在自身via反焊盘（铜半径+0.15mm净空+0.01mm离散容差）内，未发现其他缺口。详见independent_review.md；不等于电磁回流、阻抗、I²C上升时间或实物验证。

## 剩余工作

5个缺口：SDA2（上部至MCU、MCU至ADC）、SCL1（上部传感器至MCU/上拉）、IMU_INT1、MOSI1。下一组继续I²C主干，随后IMU_INT/MOSI。

警告120与5项忽略规则仍需逐项审查。制造文件/独立查看器、采购器件与电芯资料、壳体STEP/3D、实物仍未完成。固件本轮未改也未重测；前次MCU8/8、host23/23、20ARM对象不代替最终ELF/板上验证。没有更改制造放行状态。
