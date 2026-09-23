> **已更正：本报告MISO PCB采用与“无新增参考缺口”结论已撤回；缓存填铜验证不足。固件成果保留。当前状态见 `REFERENCE_AUDIT_CORRECTION_20260923_CN.md`。下文仅作历史记录。**

# MISO布线与I²C固件检查点（2026-09-23）

**仍为NOT_FAB_RELEASED，交付未完成。** 正式主板采用 `validation/revA2_spi/miso3`，完整基线及所有试验副本留存。

## 修改与实际结果

接通U5到U1的SPI_MISO。R12从F(10.55,5.0)移至F(10.55,4.4)，相接CS/电源铜同步调整，为Flash引脚逃线让出空间；C9最终未移动。REED_WAKE局部In2走线调整；MISO两端新增0.60/0.30mm过孔，主体走In1右侧。没有改变焊盘网络或规则。

| 官方项目 | 基线重跑 | 主板重跑 |
|---|---:|---:|
| 普通DRC错误（未连接另计） | 0 | 0 |
| 未连接 | 14 | 13 |
| 警告 | 119 | 115 |
| 原理图一致性 | 0 | 0 |
| ERC错误/警告 | 先前0/0 | 0/0 |

警告为压铜53、重叠46、板边9、文字高度6、背面未镜像1，全部仍开放；减少来自R12局部位置变化，没有豁免。miso2的CLI总违规117实际为2错误+115警告，不能把总数误当警告；采用前断言拦住该候选，修正两处间距后才采用miso3。`comparison.json`保留分类计数。

## 平面与回流检查的边界

该方案首次在In1局部使用信号铜。检查证明：In1地仍为单一外轮廓；桥路696点、LSE226点仍覆盖地，原短F层/零过孔输入保持；对几何未改动的F/B非地走线每0.05mm中心采样，未发现新增In1地覆盖缺口。见 `plane_change.json`、`analog_evidence.json`、`lse_reference.json`。43封装、编号焊盘网络、四层/1mm/12×35mm与规则保持，见 `board_invariants.json`。

这些是几何/连通证据，**不是电磁回流或信号完整性证明**；采样没有覆盖全部焊盘面、边缘和修改过的内层信号。MISO及REED的跨层返回路径、邻近参考铜和地过孔距离仍需最终SI/EMC与实物审查，不得仅凭In1仍连通就放行。没有用信号槽穿越LSE/桥路下方。

## 可复现命令

KiCad CLI10.0.6：`/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`；pcbnew用KiCad自带Python3.9。仓库根目录实际执行：

```sh
kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_spi/baseline/drc.json validation/revA2_spi/baseline/smart_apo_common_revA2.kicad_pcb
kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_spi/miso3/drc.json validation/revA2_spi/miso3/smart_apo_common_revA2.kicad_pcb
bash tools/export_fab_revA2.sh
python3 tools/validate_revA2.py
python3 validation/revA2_spi/summarize.py
# 以下使用KiCad Python
python3 validation/revA2_spi/check_invariants.py
python3 validation/revA2_spi/check_plane_change.py
python3 validation/revA2_spi/check_analog.py
python3 validation/revA2_spi/check_reference.py
python3 -m unittest discover -s firmware/mcu/tests -v
python3 -m unittest discover -s firmware/host/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/spi_route_checkpoint/arm
```

导出脚本重跑主文件ERC/DRC后exit2，正确拦截，无生产Gerber；日志`export_gate.log`。分类、网络/坐标/UUID修复队列、前后全项目副本都在`validation/revA2_spi/`。

## 固件与设计复核

I2C1寄存器后端已实现PB6/PB7 AF6开漏、7bit地址、寄存器写/重复START读、清洁NACK可继续探测其他器件、硬故障锁存、尊重SCL拉伸的显式GPIO恢复。读失败保留原缓冲区；最大读255字节的局部暂存需纳入最终RAM/栈预算。TIM2测试仅增加I2C隔离hooks，避免真实MMIO访问宿主。

主代理重跑MCU6/6、host23/23；Clang23.1.0再次构建20个ARM ELF32 REL对象并校验标头/哈希，见`arm_objects.json`。I²C时序为有明确边沿/滤波假设的保守标准模式计算，不是板上波形验证。官方依据、模型和故障范围见 `firmware/mcu/VERIFICATION_I2C_CN.md`。最终ELF、RAM/栈余量、实际传感器应答、Stop恢复仍未完成。

主代理亦实际复核ST数据手册ADC阻抗表，运行分压候选计算；详见 `ADC_DIVIDER_REVIEW_revA2_CN.md`。当前1M/330k尚未修改；180k/59.4k候选在1%容差下Rth45.11kΩ，但4.2V静态电流17.54µA、仅分压30天约12.63mAh，需要与待机预算共同选定，不能只为满足阻抗改变电阻。准确电芯、参考电压/漏电/建立时间和实物误差仍开放。

## 剩余与文件

13项连接：SDA3、SCL3、U3地3、U3电源1、IMU_INT1、SPI_SCK1、SPI_MOSI1。下一组继续SCK/MOSI/中断/I²C，之后处理警告、历史ignored规则、板厂孔/阻焊/钢网、独立查看器、准确器件与机械资料。

CT05所购图纸、电芯/充电限制、采购后缀、U2/U3封装/逃线依据、壳体STEP/干涉和实物仍阻断最终交付。链接器/compiler runtime缺失，新增工具链授权仍待答复；没有安装依赖。

主要改动：正式PCB及官方报告/validation JSON、交接入口、`validation/revA2_spi/`；固件`board.c`的I²C段、`board_revA2.h`、`tests/i2c_registers.c`、`tests/test_i2c.py`、`tests/tim2_timebase.c`隔离hooks与I²C验证报告。新增ADC分压复核文档。无提交、重置或Rev.A1覆盖。
