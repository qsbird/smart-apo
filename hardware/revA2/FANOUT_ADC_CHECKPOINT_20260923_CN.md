# MCU局部逃线与电池ADC检查点（2026-09-23）

**NOT_FAB_RELEASED，目标未完成。** 正式主板采用 `validation/revA2_fanout/sense5`；baseline完整快照可回退，所有失败候选留存且未采用。

## 改动和官方结果

先单独验证UART局部整理，再验证Flash片选折返铜整理，最后连通VBAT_SENSE。没有移动封装；UART_RX、STRAIN_DRDY和LED_GATE过孔移动时同步所有相接层的端点。保留原网络、板框和规则。补新分割地铜的接地过孔。

| 项目 | 基线重跑 | 主文件重跑 |
|---|---:|---:|
| 普通DRC错误（未连接另计） | 0 | 0 |
| 未连接 | 15 | 14 |
| 警告 | 119 | 119 |
| 原理图一致性 | 0 | 0 |
| ERC错误/警告 | 先前0/0 | 0/0 |

警告仍为压铜56、重叠47、板边9、文字高度6、背面未镜像1；没有豁免或降低严重性。五项历史ignored规则仍需审查。

UART_RX从3过孔/7铜段/10.750mm变为1过孔/5铜段/9.993mm；FLASH_CS仍2过孔，40段/21.500mm降为25段/19.657mm。UART_TX仍1过孔，长度4.500→4.644mm，以释放MCU左侧空间。VBAT_SENSE全部铜段总长15.596mm、2过孔，包含原有分压/滤波支路；现在实际连通，不能以此证明ADC精度或噪声。

43封装、编号焊盘网络、四层、1mm板厚、12×35mm板框、项目规则不变；全部过孔0.60/0.30mm。模拟输入696点、LSE226点仍全部覆盖In1地，In1单一外轮廓；桥路长度/F层/零过孔未变。

## 实际命令及证据

KiCad 10.0.6 CLI绝对路径 `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`。仓库根目录：

```sh
kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_fanout/baseline/drc.json validation/revA2_fanout/baseline/smart_apo_common_revA2.kicad_pcb
kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_fanout/sense5/drc.json validation/revA2_fanout/sense5/smart_apo_common_revA2.kicad_pcb
bash tools/export_fab_revA2.sh
python3 tools/validate_revA2.py
python3 validation/revA2_fanout/summarize.py
# pcbnew脚本使用KiCad自带Python 3.9
python3 validation/revA2_fanout/check_invariants.py
python3 validation/revA2_fanout/check_analog.py
python3 validation/revA2_fanout/check_reference.py
python3 validation/revA2_fanout/route_metrics.py
python3 -m unittest discover -s firmware/mcu/tests -v
python3 -m unittest discover -s firmware/host/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/fanout_checkpoint/arm
```

正式导出脚本重跑ERC/DRC后exit 2，正确拦截，无生产Gerber。`comparison.json`记录每轮分类计数；`repair_queue.csv`保存剩余类别/网络/坐标/UUID；`route_metrics.json`记录长度/过孔。`board_invariants.json`和参考地JSON绑定板文件或几何结果，`export_gate.log`记录拦截。

主代理重跑host23/23、MCU5/5（新增ADC寄存器模型，模型均含AWA/UW）。两变体20个ARM ELF32 REL对象构建并独立检查标头/哈希，见`arm_objects.json`。尚无最终ELF和板上运行证据。

## ADC功能与新发现的硬件阻塞

真实PA1/ADC1_IN1后端完成：只改对应GPIO/RCC位，固定12位单次采样，每次校准，使用TIM2测量稳压和校准后等待；CCRDY/ADRDY/EOC/EOS等有界轮询，失败不改调用者输出。原始码来自ADC_DR，成功后也reset关闭模拟稳压器。详见 `firmware/mcu/VERIFICATION_ADC_CN.md` 的官方来源、15类故障及模型范围。

**R4=1MΩ、R5=330kΩ的等效源阻抗约248.1kΩ，超出DS12992表59外部源阻抗50kΩ条件。** C14和最长采样时间不能代替合规及误差验证。名义3.3V参考、输入漏电/掉电反灌、RC建立、温度/批次和功耗均未验证；此项列为电气设计开放项。修改分压、缓冲或开关方案需要同时复核静态电流与既有换算，不能只让模型测试变绿。

## 未完成项与下一步

14项连接：SDA3、SCL3、U3地3、U3电源1、IMU_INT1、SPI_SCK/MISO/MOSI各1。下一步继续SPI/中断/I²C，并处理上述电池分压设计。U3禁布/PAD2LID逃线仍需准确源资料。

其余开放：119警告及ignored规则、板厂阻焊/孔/钢网独立复核、所购CT05图纸、电芯规格/充电限制、封装采购后缀、壳体和STEP干涉、实物试验。固件I²C/唤醒等仍未完成，最终链接缺链接器/compiler runtime；安装授权待答复，未安装依赖。

主要改动文件：正式PCB、ERC/DRC及validation报告、交接入口、`validation/revA2_fanout/`；固件`board.c` ADC段、`board_revA2.h`契约、`tests/adc_registers.c`、`tests/test_adc.py`及ADC报告/日志。未提交、重置或覆盖Rev.A1。
