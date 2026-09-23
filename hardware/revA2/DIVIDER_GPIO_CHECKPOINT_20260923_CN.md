# 分压修正、GPIO与U3资料审查（2026-09-23）

**NOT_FAB_RELEASED，完整交付未完成。** 本轮没有改变PCB布线，保留已经恢复的连续In1地设计，不采用先前MISO/SCK参考地退化副本。

## 分压设计修正

R4=180kΩ、R5=60.4kΩ，均1%、0402，替代原1MΩ/330kΩ。名义Thevenin阻抗45.225kΩ、同向1%最坏45.677kΩ，低于已实际核读的DS12992表59中50kΩ条件。选择较100k/33k更低的静态电流并保留原封装/器件数；没有凭电容或慢采样豁免原来的248kΩ。

代价：4.2V下17.471µA；恒压30天仅此支路约12.579mAh，不是整机续航预测。名义C14=100nF的RC常数4.522ms；上电/阶跃建立、参考电压、漏电、容差/温漂、掉电反灌与实际待机预算仍需验证。这里只关闭阻抗数值超限，**不宣称ADC精度或整机功耗合格**。标准阻值候选不等于采购后缀/供应商已审核。

原理图、PCB值、工作BOM、官方网表和固件已同步；固件换算为`adc * 132220 / 41223`，4095码乘积在32位范围内，过量程仍钳位。已有生成器仅更新其值覆盖逻辑，**没有运行build或重生成任何正式文件**。逐字核对PCB/原理图本轮差异仅两个Value字段，编号焊盘/网络和布局不变。

`tools/check_divider_revA2.py`核验这五类文件、换算有理数、最坏阻抗、导出网表所有节点与生成器值函数。实际PASS，证据`validation/revA2_divider/consistency.json`；基线文件完整保存在该目录baseline内。

## 官方及独立实际检查

| 检查 | 结果 |
|---|---|
| 官方ERC | 0错误 / 0警告 |
| 官方DRC普通错误 / 未连接 / 警告 | 0 / 14 / 119 |
| 原理图一致性 | 0 |
| 新显式填铜参考审查 | exit0，单一In1地外轮廓，六个敏感网络中心/边缘采样无缺口 |
| 生产导出 | exit2，正确拦截，无生产文件 |
| MCU回归 | 7/7通过，模型含AWA/UW |
| host回归 | 23/23通过 |
| ARM构建 | 两变体20个ELF32 ARM REL对象，标头/哈希核对通过 |

参考检查是数字几何范围，不能替代电磁和实物验证。旧缓存审查缺陷的更正仍有效，见`REFERENCE_AUDIT_CORRECTION_20260923_CN.md`。119警告及原有ignored规则仍开放。

实际命令（KiCad CLI绝对路径 `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`）：

```sh
kicad-cli sch export netlist --format kicadxml -o hardware/revA2/netlist_revA2_kicad10.xml hardware/revA2/smart_apo_common_revA2.kicad_sch
bash tools/export_fab_revA2.sh
python3 tools/check_divider_revA2.py
python3 tools/validate_revA2.py
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 tools/check_reference_revA2.py hardware/revA2/smart_apo_common_revA2.kicad_pcb --output validation/revA2_divider/reference_audit.json
python3 -m unittest discover -s firmware/mcu/tests -v
python3 -m unittest discover -s firmware/host/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/divider_gpio_checkpoint/arm
```

主代理重跑以上集成回归；新增ADC换算测试遍历所有4096码，使用独立物理分压公式并验证钳位。日志为`validation/revA2_divider/{adc_test,mcu_tests,host_tests,arm_objects,export_gate}.log`，对象清单`arm_objects.json`。没有新增工具依赖。

## GPIO与U3

GPIO后端实现真实初始化、PA9磁簧/PA0中断电平读取，PA4预置高、PB0预置低，PA9/10 remap顺序检查；1.5s闭合计时利用EXTI9释放pending识别轮询间松开。IMR/EMR屏蔽，无NVIC/ISR或Stop唤醒声明。失败/配置漂移/计时故障会清零资格；GPIO/SWD无关位保留。详见`firmware/mcu/VERIFICATION_GPIO_CN.md`。LED只有启动关闭，实际闪烁及低功耗集成仍未完成。

只读U3审查见`U3_ROUTING_REVIEW_20260923_CN.md`：DS13317明确中央金属盖允许接地或浮空；当前仍选择GND，未改网络。外围焊盘方向与通用TN1383“平行长边”表述存在适用性问题，不能照搬U2径向通道声称原厂验证。一次已授权官方Gerber只读下载返回HTTP567，未取得文件；不重复试探或凭类似器件关闭。

## 剩余与文件

继续SPI/I²C/IMU和U3共14项连接，采用候选前必须重新填铜并审查新增参考缺口；之后处理警告、制造层/孔/阻焊/钢网、独立查看器及3D干涉。CT05和准确电芯、封装采购资料仍开放。固件LSE、Stop/RTC补偿、LED控制、ADC建立/VREF校准、最终ELF/栈预算和板上测试未完成。链接器/compiler runtime缺失，安装授权待答复。

主要改动：正式.sch/.pcb仅R4/R5值；工作BOM与官方网表/官方报告；`board_revA2.h`、`board.c`的GPIO段；ADC/GPIO测试；生成器的值覆盖逻辑；新增分压校验器和上述验证文档/证据。原有人工工作、Rev.A1均保留，没有Git提交或重置。
