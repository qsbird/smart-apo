# 电源与 SPI 检查点（2026-09-23）

仍为 **NOT_FAB_RELEASED**，总体目标未完成。正式主板已经采用 `validation/revA2_power/chain_fix7`；此前候选均为试验副本，不能生产。

## 修改与结果

本组完成电池 J1、充电器 U6/C12、LDO U7/C9、分压 R4 的 VBAT 连接，以及 J2 到 U6/C11 的 CHARGE_IN。供电新线宽 0.25 mm，新增过孔全部 0.60/0.30 mm。LED_GATE 的 F/In2 走线局部重布并同步移动源过孔，未移动封装。补 J2 地焊盘到已有地过孔的实连接、F.Cu 孤岛地过孔，以及被新走线分割的 3V3 铜岛跨接。

| 官方检查 | 修改前快照重跑 | 采用后主文件重跑 |
|---|---:|---:|
| 普通 DRC 错误（不含未连接） | 0 | 0 |
| 未连接 | 22 | 18 |
| 警告 | 119 | 119 |
| 原理图一致性问题 | 0 | 0 |
| ERC 错误 / 警告 | 先前 0/0 | 0/0 |

所有警告仍开放：silk_over_copper 56、silk_overlap 47、silk_edge_clearance 9、text_height 6、nonmirrored_text_on_back_layer 1。项目原有五项 ignored 检查未修改，仍需放行审查；普通错误为 0 不代表 DRC 已通过。

保留了本轮输入全项目快照 `validation/revA2_power/baseline/` 和每个候选。`comparison.json` 记录逐轮分类计数；`repair_queue.csv` 记录剩余问题的网络、位置和 UUID。试验曾出现间距、热连接、地铜分割及过孔贴到异网铜后被 KiCad 重新归网的问题，未采用这些候选。最终新增 VBAT/GND 过孔的保存后网络已复核。无规则放宽，无全板再生成，无 Rev.A1 修改。

43 个封装、焊盘网络、四层叠层、1.0 mm 板厚、12×35 mm 板框及项目规则不变。桥路原始双输入约 2.670/2.670 mm，滤波双输入约 2.770/2.770 mm，均 F.Cu 零过孔；696 个中心/边缘采样点仍覆盖连续 In1 地。LSE 226 个采样点也全部覆盖 In1 地。以上仅为数字几何检查，不证明噪声、回流阻抗、振荡启动或板上性能。

## 实际执行命令

在仓库根目录执行，KiCad CLI 为 `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` 10.0.6，pcbnew 脚本使用 KiCad 自带 Python 3.9（需要桌面会话访问）。

```sh
kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_power/baseline/drc.json validation/revA2_power/baseline/smart_apo_common_revA2.kicad_pcb
kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_power/chain_fix7/drc.json validation/revA2_power/chain_fix7/smart_apo_common_revA2.kicad_pcb
bash tools/export_fab_revA2.sh
python3 tools/validate_revA2.py
python3 validation/revA2_power/summarize.py
# 以下三项使用 KiCad 自带 Python
python3 validation/revA2_power/check_invariants.py
python3 validation/revA2_power/check_analog.py
python3 validation/revA2_power/check_reference.py
python3 -m unittest discover -s firmware/mcu/tests -v
python3 -m unittest discover -s firmware/host/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/power_checkpoint/arm
```

生产导出脚本重新执行正式 ERC/DRC 后 **exit 2，正确拦截**，日志 `validation/revA2_power/export_gate.log`；没有生产 Gerber。固件 MCU 3/3、host 23/23；本轮又编译出两变体共 20 个 ARM ELF32 ET_REL 对象，独立检查 ELF 标头并存哈希于 `arm_objects.json`。目标文件不是最终固件。

SPI1 已有真实寄存器实现与故障模型测试，见 `firmware/mcu/VERIFICATION_SPI_CN.md`；I2C、UART、ADC、唤醒等仍未完成。最终 ELF 尚未链接，缺链接器和 ARM compiler runtime；工具链安装授权待答复。没有烧录或板上测试证据。

## 下一组与阻塞

剩余 18 项连接：I2C_SDA 3、I2C_SCL 3、NRST 3、U3 GND 3、U3 3V3 1、IMU_INT 1、VBAT_SENSE 1、SPI_SCK/MISO/MOSI 各 1。先处理不依赖 U3 资料的复位、采样与 SPI/I2C 支路，再处理 U3 禁布与 PAD2LID 的源资料审查，最后丝印及制造审查。不得以缩小禁布区或修改网络来规避尚未证实的封装约束。

所购 CT05 图纸、401020 电芯准确规格/充电限制、采购后缀/核心封装、U2 原厂焊盘钢网交叉核对、U3 逃线依据、壳体及整机 STEP/干涉、实物测试仍开放。VBAT/充电铜线连通并不等于充电电流已对所购电芯验证。

本组主要改动文件：正式 `.kicad_pcb`、官方 ERC/DRC JSON、`validation_report_revA2.json`、本报告和交接入口、`validation/revA2_power/` 检查点。SPI 文件与测试的具体变更清单见其验证报告。没有提交或重置已有 Git 工作。
