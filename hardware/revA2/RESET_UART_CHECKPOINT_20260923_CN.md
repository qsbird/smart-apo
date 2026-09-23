# 复位布线与 UART 检查点（2026-09-23）

**目标仍活动，NOT_FAB_RELEASED。** 正式主板采用 `validation/revA2_reset/reset9`，其余候选仅为可回退试验记录。

## 本组修改

连接 J2、U1、R11、C17 的 NRST 三个原始断点。C17 从 F(10.55,10.4) 移到 F(10.8,10.4)，原来没有显式相接走线（脚本断言）；新建 NRST 与地连接，没有将焊盘压到旧铜。新增复位主线走 In2，信号宽0.15 mm；地层 In1 未布置信号。增加 U1/C1 地过孔，以及 C2 到传感器上方电源区的0.25 mm短跨接，修复新线造成的铜面分割。全部过孔仍0.60/0.30 mm。

试验 reset4 曾把过孔置于小电容焊盘内；未采用。最终 C17/C1 的钻孔位于这些小焊盘外。C1 地过孔邻近同网焊盘，后续仍须检查阻焊桥、盖油和板厂公差，不能把数字 DRC 当作钢网/焊接确认。J2复位焊盘的层间连接也纳入最终阻焊/探针接触审查。

| 实际检查 | 基线重跑 | 正式主板重跑 |
|---|---:|---:|
| 普通 DRC 错误（未连接另列） | 0 | 0 |
| 未连接 | 18 | 15 |
| 警告 | 119 | 119 |
| 原理图一致性 | 0 | 0 |
| ERC 错误/警告 | 先前0/0 | 0/0 |

119条警告仍未豁免：压铜56、重叠47、板边9、文字高度6、背面未镜像1。原有五项 ignored 检查未改变，仍需审查；未放宽规则。

## 实际验证与证据

KiCad CLI 10.0.6 路径 `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`。从仓库根目录执行：

```sh
kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_reset/baseline/drc.json validation/revA2_reset/baseline/smart_apo_common_revA2.kicad_pcb
kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity -o validation/revA2_reset/reset9/drc.json validation/revA2_reset/reset9/smart_apo_common_revA2.kicad_pcb
bash tools/export_fab_revA2.sh
python3 tools/validate_revA2.py
python3 validation/revA2_reset/summarize.py
# 下列 pcbnew 检查用 KiCad 自带 Python 3.9
python3 validation/revA2_reset/check_invariants.py
python3 validation/revA2_reset/check_added_copper.py
python3 validation/revA2_reset/check_analog.py
python3 validation/revA2_reset/check_reference.py
python3 -m unittest discover -s firmware/mcu/tests -v
python3 -m unittest discover -s firmware/host/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/reset_checkpoint/arm
```

- `comparison.json` 包含 baseline、reset1..9、final 的逐类计数；`repair_queue.csv` 包含网络/位置/UUID；保存了全项目前后快照。
- 所有43个封装的编号焊盘网络、四层/1mm/12×35mm板框与项目规则保持不变。15组新增铜线/过孔的保存后网络逐项核对通过，证据 `added_copper.json`。
- 桥路696点、LSE226点全部覆盖In1地，In1仍单一外轮廓；原差分输入长度、F层、零过孔保持。仅数字几何，不证明噪声、阻抗、振荡或复位波形。
- 正式生产脚本重跑ERC/DRC后 **exit 2，正确拒绝导出**；没有生产Gerber。日志 `export_gate.log`。
- 主代理重跑host **23/23**、MCU **4/4**（runtime、TIM2、SPI、UART；模型含两变体），日志 `host_tests.log`、`mcu_tests.log`。再次构建20个ARM ELF32 REL对象并验证标头/哈希，证据 `arm_objects.json`；不是最终ELF。

UART实现PA2/PA3 AF1、HSI16/PCLK限定、115200标称8N1 TX-only、有限等待与错误锁存，不改变帧协议。完整官方依据、模型范围和修改清单见 `firmware/mcu/VERIFICATION_UART_CN.md`。没有RX消费、主机ACK、Stop后自动恢复或板上成功证据；I2C/ADC/唤醒等仍有桩。

## 剩余与下一组

15项未连接：SDA3、SCL3、U3地3、U3电源1、IMU_INT1、VBAT_SENSE1、SPI_SCK/MISO/MOSI各1。继续逐网处理SPI/采样和总线；U3禁布及PAD2LID逃线需要准确官方资料。完成连接后处理丝印警告、被忽略的检查、阻焊/孔/钢网/器件方向和独立查看器复核。

外部阻塞仍包括：所购CT05图纸、401020电芯规格和充电限制、采购后缀/封装审查、原厂焊盘资料核对、整机STEP与壳体、实物测试。最终链接仍缺链接器/compiler runtime，新增工具链授权待答复；未安装依赖。

主要修改：正式PCB、ERC/DRC与validation JSON、交接文档；`validation/revA2_reset/`；固件 `board.c` 的USART段、`board_revA2.h`契约、`tests/uart_registers.c`、`tests/test_uart.py`及UART报告/证据。无Git提交或重置，Rev.A1校验不变。
