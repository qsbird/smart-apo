# Flash原厂封装修正检查点（2026-09-23）

**仍为NOT_FAB_RELEASED，完整交付未完成。** 本轮已采用`validation/revA2_flash_package/land6`。目的为纠正原厂焊盘不匹配；未连接仍14项，不能将此说成SPI已完成。

## 来源与发现

实际读取并渲染 Winbond W25Q256JV RevR（2026-05-06）PDF第7/88/92页，核对E封装8×6mm、节距1.27mm、裸露金属区3.4×4.3mm及E/I/Q后缀。原KiCad库`WDFN-8-1EP_8x6mm_P1.27mm_EP6x4.8mm`描述直接引用Microchip图纸；中央6×4.8mm和外围0.9×0.4mm不是本次Winbond指南的land。

原厂文档库列出[AN0000009](https://www.winbond.com/hq/support/documentation/?__locale=en)，当前下载页转向levelOne页面，未取得该入口的PDF。实际采用的是公开会议站点发布的[Winbond原著Rev2.1副本](https://site.eettaiwan.com/events/iot2021/download/%5BWinbond%5DSpiFlashPCBLayoutGuideline.pdf)，不是第三方重新绘制；第21页给出精确land/stencil。其金属区尺寸与最新RevR器件图交叉一致。文档存档、URL和SHA256见`source_manifest.json`，不把旧版副本说成原厂网站最新指南。

[Winbond官方FAQ](https://www.winbond.com/hq/support/faq/technical/index.html)允许SON中央结构焊盘浮空或接器件地，并要求避免裸露过孔位于其下。保留原pad9浮空选择，不更改电气网络。官方Q后缀固定QE=1仍支持标准SPI；现有单线SPI命令不依赖Quad模式。

LCSC [C97522](https://www.lcsc.com/zh-CN/product-detail/NOR-FLASH_Winbond-Elec-W25Q256JVEIQ_C97522.html)及[C5334276](https://www.lcsc.com/zh-CN/product-detail/C5334276.html)当前目录均列W25Q256JVEIQ，目录核对不等于实际来料/封装版本/包装形式已验收。没有采购或替用户确认库存。

## 采用的几何

新增项目封装`SmartApoRevA2:WSON-8_W25Q256JV_8x6mm_AN0000009`，对原著第21页旋转90°后：

| 项目 | 候选实现 |
|---|---|
| 外围铜焊盘 | 1.50×0.80mm，行中心X=±4.15mm，Y=±1.905/±0.635mm |
| 外围钢网 | 1.40×0.70mm，行中心X=±4.20mm |
| 中央PCB铜焊盘 | 3.25×4.05mm；不是机械金属区3.4×4.3mm |
| 中央钢网 | 5个直径0.65mm圆；中心及X=±0.65/Y=±0.9mm四角 |
| 指南钢网厚度 | 0.10mm，仍需贴片厂工艺确认 |
| Courtyard | 最大本体和焊盘外扩0.25mm的阶梯轮廓，未豁免重叠 |
| 3D | 删除错误Microchip模型，尚无已核验替代模型 |

U5仍B面180°，中心从(6.2,6.2)移到(6.2,5.85)；pad1=(10.35,3.945)。库规范化为F面pin1左上，独立复核通过。C8移至B(1.15,2.3)、C4移至F(10.4,2.0)，相关供电、片选、复位过孔与走线同步调整；补地铜岛及局部供电跨接，未仅改坐标。所有编号焊盘网络保持，过孔仍0.60/0.30mm。

## 实际官方与独立验证

| 项目 | 基线重跑 | 正式主板重跑 |
|---|---:|---:|
| 普通DRC错误（未连接另计） | 0 | 0 |
| 未连接 | 14 | 14 |
| 警告 | 119 | 119 |
| 原理图一致性 | 0 | 0 |
| ERC错误/警告 | 先前0/0 | 0/0 |

警告分类变为压铜57、重叠46、板边9、文字高度6、背面未镜像1；全部仍开放，无规则放宽。每轮分类见`comparison.json`，剩余网络/位置/UUID见`repair_queue.csv`。

显式重新填铜后In1地单一外轮廓，六个敏感网络中心和边缘采样均覆盖；独立审查见`independent_review.md/json`。新参考审查器仍报告REVIEW_REQUIRED/exit2：一条/3V3未变更线有8个样点落入移动后同网供电过孔的反焊盘，最远0.43744mm，小于0.45mm清空半径；附近地过孔中心距0.75048mm且连到In1地。此局部换层点经明确几何处置接受，**未修改检查器门槛，也不是EM/PI、去耦效果或实物验证通过**。不是先前被撤回的跨线地面槽。

`check_final.py`进一步核对外围/中央铜与paste、库pin1、编号网络、规则/四层1mm、过孔规格；所有过孔铜环不进入最大3.45×4.35mm金属EP投影，错误3D及厂家tags均已移除。`final_invariants.json`绑定正式板及参考报告哈希。

实际命令（KiCad CLI为`/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`10.0.6，pcbnew用其自带Python3.9）：

```sh
kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_flash_package/baseline/drc.json validation/revA2_flash_package/baseline/smart_apo_common_revA2.kicad_pcb
kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_flash_package/land6/drc.json validation/revA2_flash_package/land6/smart_apo_common_revA2.kicad_pcb
kicad-cli sch export netlist --format kicadxml -o hardware/revA2/netlist_revA2_kicad10.xml hardware/revA2/smart_apo_common_revA2.kicad_sch
bash tools/export_fab_revA2.sh
python3 tools/validate_revA2.py
python3 tools/check_divider_revA2.py --output validation/revA2_flash_package/divider_consistency.json
# 以下两项使用KiCad Python
python3 tools/check_reference_revA2.py hardware/revA2/smart_apo_common_revA2.kicad_pcb --baseline validation/revA2_flash_package/baseline/smart_apo_common_revA2.kicad_pcb --output validation/revA2_flash_package/main_reference.json
python3 validation/revA2_flash_package/check_final.py
```

生产脚本重跑ERC/DRC后exit2，正确拒绝导出；没有生产Gerber。分压核对通过；该工具的历史“只改两个值”检查改为显式`--check-value-only`，避免以后合法布线被误判。历史值迁移证据保留，本轮采用前也运行该模式通过。未运行生成器build。

## 修改文件和剩余

正式PCB、原理图U5 Footprint字段、新项目封装、官方网表/报告、工作BOM、生成器映射、分压校验器及本报告/证据。MCU代码未改，本轮未重复固件测试；先前8/8、23/23和20ARM对象结果不作为新证据。

原始不匹配封装及全部候选可从baseline/land1..6回退。14未连接、制造警告/ignored检查、其他核心封装与U3逃线、实际CT05/电芯/来料、正确3D/STEP与干涉、最终固件链接、低功耗及实物验证仍开放。未覆盖Rev.A1、未提交或重置已有工作。
