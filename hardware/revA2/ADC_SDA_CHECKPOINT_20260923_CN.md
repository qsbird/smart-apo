# ADC SDA完成与3D缺件审查 · 2026-09-23

正式PCB SHA256 `07bc3e6bfeb425158fc84a676e46575252e4cc9e3bb62b5befcbbb1a239b4ae7`；I²C两条总线已全部接通，NOT_FAB_RELEASED。

## 改动

R1由B(3.8,10.4)移至(3.7,10.15)，关联线端同步。SCK In2原四段改为(4.8,11.2)→(5,11.2)→(7.55,13.75)→(7.55,15.475)，为SDA的B跨层桥让出空间。SDA从R1 pad1经B铜至via(5.8,12.85)，In2向下至via(4.825,19.525)，F经(4.825,20.1)→(4.095,20.83)接U4 pad14。线宽0.15mm、via0.60/0.30mm，不增加In1信号。

独立子任务初候选把ADC端via置于SMT pad内；主任务没有采用此端点，在隔离副本将其移至焊盘外。最终两个新via的铜环到最近焊盘包围框净距分别1.625mm、0.159619mm，不要求据此使用未经确认的填孔/盖孔工艺。

只改PCB铜及R1位置；原理图/封装库/焊盘网络/四层1mm/12×35mm板框保持。未修改Rev.A1或运行整板生成器。IMU_INT与MOSI本轮未采用改动，固件未改。

## 实际验证证据

子任务独立候选stage1：1项tracks_crossing；stage2：21 clearance、5 hole_clearance、1 solder_mask_bridge；均拒绝。stage3官方普通错误0/2未连接/122警告，随后主任务另改ADC端换层点。完整探索证据在validation/revA2_adc_sda_candidate；主任务采用前baseline、接收候选stage1、焊盘外修正版stage2、最终final在validation/revA2_adc_sda_adopt。

实际执行：

```sh
bash tools/export_fab_revA2.sh
python3 tools/validate_revA2.py
python3 tools/check_divider_revA2.py --output validation/revA2_adc_sda_adopt/divider_consistency.json
python3 validation/revA2_adc_sda_adopt/summarize.py
```

主板KiCad10.0.6 ERC0/0，普通DRC错误0、未连接3→2、警告122、一致性0。制造导出exit2拒绝Gerber/钻孔/CPL。validate确认Rev.A1哈希不变，分压一致性通过。详见main_gate.log、comparison.json、repair_queue.csv。

使用KiCad Python显式Fill的check_reference_revA2主板对baseline退出0：In1单轮廓、六敏感网和未变外层铜无新增缺口。check_invariants.py通过。

独立BFS确认SDA五器件U2.14/U3.1/U1.1/R1.1/U4.14连通，SCK与R1供电仍连通。主任务对端部修改后再次BFS，并按各段实际线宽采样全部变更铜中心/双边，共6549点，缺口距同网via最大0.456015667mm，按0.45mm反焊盘加0.01mm离散几何容差归类，不声称严格≤0.45mm或EM通过。证据在stage2/supplement.json和review.md。

## 本轮3D实际工具输出

新增validation/revA2_3d_audit，官方执行：

```sh
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb export step --output validation/revA2_3d_audit/revA2_POST_ADC_SDA_REVIEW_ONLY_INCOMPLETE_MODELS.step hardware/revA2/smart_apo_common_revA2.kicad_pcb
```

退出0，生成1,665,009字节审查STEP，但日志报告Y1模型无法添加。实际清单43器件中35个有可解析的通用模型文件；J1/J2/J3/U2/U3/U5/SW1共7个未绑定模型，Y1绑定路径不存在。已有文件并不证明所购器件外形正确。current_export_manifest.json将STEP散列与当前PCB散列绑定；旧导出另行保留，不能混作当前板。

没有Rev.A2壳体装配STEP，未做独立3D查看器或完整干涉验证。只生成明确标记模型不完整/非生产的审查件，未勾选机械放行。Downloads按CT05/401020等相关名称检索未找到所购资料，阻塞未关闭。

## 剩余工作

电气连接剩IMU_INT和MOSI各1处。继续逐网隔离修复，随后审查122项警告、5类忽略规则和全板回流/制造细节。3D缺模型、所购器件/电芯资料、Rev.A2壳体、最终制造包/独立查看器与实物验证仍开放。固件已有8/8 MCU、23/23 host及20 ARM对象仅是前次证据，最终ELF/板上未通过。
