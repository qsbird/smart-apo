# 桥路输入与TIM2检查点（2026-09-23）

**目标继续活动，未完成交付，NOT_FAB_RELEASED。** 本轮解决桥路主差分输入的几何不对称，不能将此视为整个模拟性能或PCB放行已经验证。

## 当前实际结果

| 检查 | 改动前快照重跑 | 当前主文件重跑 |
|---|---:|---:|
| 普通DRC错误 | 0 | **0** |
| 未连接 | 25 | **22** |
| 警告 | 111 | **119** |
| 原理图一致性 | 0 | **0** |
| ERC | 先前0/0 | 本轮 **0/0** |
| host/native回归 | 23 | **23项通过** |
| MCU模型/runtime回归 | 1 | **2项通过** |
| Cortex-M0+对象构建 | 两变体 | 本轮重建 **20个对象通过** |
| 最终ELF链接 | 未完成 | 两变体 **exit 2** |
| 生产导出 | 拒绝 | **exit 2** |

警告增加来自重排后的丝印：压铜56、重叠47、板边9、文字高度6、背面文字未镜像1，全部仍开放；未更改规则严重性或关闭检查。普通错误0不含22项未连接，不能宣称DRC通过。

## 桥路布局及数字验证

U4横向置于F(6.0,24.4)，旋转90°；J3仍在F(7.4,32.6)，旋转180°。R8/R9在F(4.095,30.0)/(2.825,30.0)，C13在F(3.46,28.6)。C5/C6分别在F(2.825,19.6)/(1.555,19.6)，C7在F(7.905,29.5)。R10移至B(8.0,17.7)，D1移至F(2.3,32.65)。

所有受影响铜都先显式移除并重建，包括输入、参考、激励、DRDY、LED_GATE及去耦/上拉局部线。移动D1时同步焊盘内过孔和跨层相接铜，未只改坐标。中间候选曾发现跨层端点重复移动造成断线，已从原候选重做；失败副本 `finish1` 未采用。

| 输入网络 | 原铜长 / 过孔 | 当前铜长 / 过孔 |
|---|---:|---:|
| BRIDGE_A+ | 17.150mm / 0 | **2.670mm / 0** |
| BRIDGE_A− | 15.500mm / 2 | **2.670mm / 0** |
| AIN_P_FILT | 3.250mm / 0 | **2.770mm / 0** |
| AIN_N_FILT | 7.150mm / 0 | **2.770mm / 0** |

四网全部F.Cu、0.15mm宽。滤波总长包含0.155mm差分电容支路，电阻到ADC主路径各2.615mm。长度为CAD中心线去重铜段总长，不代表加工公差或噪声验证；也不是受控阻抗差分对。

- 独立只读复核确认14/16等器件焊盘网络映射没有被调换，C13仍跨AIN_P_FILT/AIN_N_FILT，未改接地。
- 主任务复核所有编号焊盘网络与基线一致。沿四条网络的中心及两侧边缘共696个采样点均有In1地覆盖，In1地为单一轮廓。
- C5/C6到U4电源脚各1.845mm；C7到VBG为2.145mm。针对复核意见补近端回流后，C5/C6地焊盘到最近接地过孔各0.72mm，C7约0.913mm，U4数字地约0.980mm。均在可追溯的接地连接组件中。
- S+参考线仍为约15.33mm/2过孔，S−约8.01mm/0过孔，参考线路并未获得主差分对同等对称性。此项及充电器附近的热/噪声影响、样机ADC噪声与标定继续开放。

**J3物理左右顺序已变化**：正面从左到右为6、5、4、3、2、1；必须使用 `BRIDGE_INTERFACE_revA2_CN.md` 的当前接线表，不能照旧图接线。

## LED供电补充

R6原位旋转180°，LED_A重新短接，过孔和相接铜同步调整，补0.25mm的3V3馈线。初次同名铜区仍未实际接主电源，官方连通性检查发现后，增加明确的F.Cu桥接至已连接的3V3网络，最终消除LED供电缺口。`led_supply`和`led_supply_finish`是未闭合的中间副本，最终采用`led_supply_bridge`。电池/LDO总链仍有未连接，不能称LED已运行。

## TIM2固件进展

`board_start_clocks()` 现在初始化寄存器级TIM2后端。它验证HSI16、分频、实际时钟源和CNT进展，PSC=15、ARR=0xffffffff；不使用循环次数伪造时间。配置变化、停转、超范围间隔和Stop唤醒后失败闭合。LSE、其余总线/ADC/低功耗驱动仍未完整实现。

宿主寄存器模型覆盖两变体的初始化、保留其他RCC位、自然回绕、配置损坏、停转、重复初始化和Stop失效；20个真实ARM目标文件编译及ARM静态分析已执行。**模型不等于真实APB/振荡器，不证明HSI精度或板上运行。** 详情与ST官方来源见 `firmware/mcu/VERIFICATION_TIM2_CN.md`。

仍无完整ELF：现有Clang可编译，但缺ARM链接器和compiler runtime。工具链安装授权问题尚未收到答复，未安装依赖。主机时间展开仍需明确的单次不中断采集条件，不会补缺测或自动完成异步重采样。

## 实际命令和证据

主任务重新运行：

```sh
python3 -m unittest discover -s firmware/host/tests -v
python3 -m unittest discover -s firmware/mcu/tests -v
make -B -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang
python3 firmware/mcu/tests/verify_arm_objects.py /opt/homebrew/opt/llvm/bin/llvm-nm
make -C firmware/mcu all CC=/opt/homebrew/opt/llvm/bin/clang VARIANT=0
make -C firmware/mcu all CC=/opt/homebrew/opt/llvm/bin/clang VARIANT=1
python3 tools/validate_revA2.py
git diff --check
bash tools/export_fab_revA2.sh
```

前四项通过，两次链接exit2，结构检查和diff检查通过，导出exit2。每组官方DRC使用 `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity`；主文件另加`--save-board`，另重跑错误级报告。ERC由导出门控重跑。

证据目录 `validation/revA2_analog/`：`baseline/`、`cluster/`、`finish1/`、`finish2/`、`ground_returns/`、`final/`，各有实际板/工程与DRC；`.changes.json`保存对象级修改；`analog_evidence.json`绑定主板哈希；`review.md`为补近端地过孔前的独立复核，相关意见已在最终候选处理；`commands.json`、`export_gate.log`、`comparison.json`、`repair_queue.csv`供复现。

本轮改变主PCB、官方报告/交接文档、`board.c`与`board_revA2.h`、新增TIM2寄存器模型测试及报告。Rev.A1、板框/层数/板厚/项目DRC规则和已有未涉及工作保留，未提交/重置分支。

## 下一步与仍开放门槛

优先完成SPI、I²C、NRST、IMU_INT、电池采样以及剩余电源连接，并审查参考线回流和所有丝印。U3专用引出/PAD2LID方案、原厂land/钢网复核仍有资料阻塞。所购CT05、电芯允许充电电流及尺寸、采购后缀、Rev.A2装配STEP/3D干涉和全部实物试验未通过。

完整交付目标未缩小。当前不能导出生产Gerber，也不能把ARM对象称可烧录固件。
