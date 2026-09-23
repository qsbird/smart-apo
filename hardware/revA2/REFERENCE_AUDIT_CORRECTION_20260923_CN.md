# 参考地验证更正与SPI回退（2026-09-23）

**最新主板：ERC0/0；普通DRC错误0、未连接14、警告119；NOT_FAB_RELEASED。** 本轮未采用SCK试验，并撤回上一轮MISO的PCB局部组；固件I²C等成果全部保留。不是以减少未连接数量替代回流要求。

## 已发现并修复的验证缺陷

旧 `check_analog.py`、`check_reference.py` 和早期 `check_plane_change.py` 直接读取板文件缓存的填充多边形。编辑脚本新增/移动铜后保存的缓存可能过时；CLI `--refill-zones`用于DRC计算，不应据此假定磁盘缓存被更新。此前基于缓存作出的“MISO没有新增参考缺口”结论无效。

官方ERC/DRC一直实际调用`--refill-zones --schematic-parity`，其错误/警告/未连接分类结果仍有效。问题在独立参考地证据，不能用DRC0推定回流通过。

新增 `tools/check_reference_revA2.py`：每次载入后显式执行KiCad `ZONE_FILLER.Fill()`再构建连接；检查LSE和四条桥路信号中心及边缘（间隔不大于0.05mm）、In1地外轮廓数量；若给定基线，两边均重新填铜，对未变更的外层非地走线检查新增缺口。输出绑定板文件SHA256、明确`fresh_zone_fill_before_analysis=true`，发现缺口返回exit2。检查不写板文件；采样通过只证明数字几何，不等于EMC/阻抗/完整回流仿真。

## 实际正反例

| 对象 | 官方普通DRC/未连接/警告 | 新参考地检查 |
|---|---|---|
| 恢复后的正式板 | 0 / 14 / 119 | exit0；In1一个外轮廓，六个敏感网络中心和边缘采样无缺口 |
| MISO候选miso3（已撤回） | 0 / 13 / 115 | exit2；地虽未整体分割，但CS、NRST及部分电源外层铜下新增缺口 |
| SCK候选sck2（未采用） | 0 / 12 / 115 | exit2；In1地变为两个外轮廓，并新增多网参考缺口 |

这说明DRC和参考地检查是不同门槛。缺口坐标/网络/UUID详见 `validation/revA2_sck/test_miso_rejected.json`、`test_sck_rejected.json`。不再将这些候选作为当前已连通生产设计。

实际执行 `python3 validation/revA2_sck/test_fresh_reference.py`：**3/3通过**，两种退化均被拒绝，逐案前后SHA256一致证明只读。日志与结果 `validation/revA2_sck/reference_test_results.json`。脚本使用 `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3`，不依赖系统Python安装pcbnew。

## 回退及正式检查

回退前断言主板与已采用miso3逐字节一致，防止覆盖后续人工工作。只将PCB恢复到 `validation/revA2_spi/baseline/`，保留原MISO板于 `validation/revA2_sck/rejected_main_miso.kicad_pcb`；未恢复Git、未修改Rev.A1、未改固件或已有其他文件。当前主板SHA256：

`2334dc8e5f3a03c4e2c3d4116731e15235ee84176130790a5a5bd0f5c5873ef7`

```sh
bash tools/export_fab_revA2.sh
# 上条实际重跑官方ERC/DRC，exit2正确拦截生产导出
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 tools/check_reference_revA2.py hardware/revA2/smart_apo_common_revA2.kicad_pcb --output validation/revA2_sck/restored_reference_audit.json
python3 tools/validate_revA2.py
python3 validation/revA2_sck/test_fresh_reference.py
```

官方日志 `restored_export_gate.log`；独立参考地结果 `restored_reference_audit.json`；验证汇总 `restored_validator.log`。新审查器、参考检查脚本修正及更正文档是本轮主要改动；未改固件，因此不重复运行此前MCU6/6、host23/23和20个ARM对象的测试来充当新证据。

## 禁布资料与下一步

本轮再次实际核读 [ST TN1383 §3.3/3.4](https://www.st.com/resource/en/technical_note/tn1383-pcb-design-guidelines-for-mems-sensors-stmicroelectronics.pdf)：明确顶层器件下不得走线/放过孔，并讨论背面可以布置供电或信号。现有U2/U3规则作用于F.Cu，未删除或放宽；内层使用仍必须额外检查回流，不能以规则未报错替代证明。

后续SPI重新设计应优先局部布局/信号层衔接，保留LSE与桥路下方地参考，并给所有新缺口明确工程处置；每一候选均调用新审查器。现有SCK副本的数字连接改善不采用。仍剩SCK/MOSI/MISO、IMU_INT、SDA/SCL及U3电源/地共14项连接。

ADC源阻抗/待机功耗、准确CT05及电芯资料、U2/U3采购封装/逃线依据、机械STEP与干涉、板厂孔/阻焊/钢网、固件最终链接和实物测试仍开放。新增工具链授权仍待答复；本轮没有安装依赖。
