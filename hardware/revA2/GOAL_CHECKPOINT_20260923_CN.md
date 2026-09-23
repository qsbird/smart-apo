# 完整交付目标检查点（2026-09-23）

> **活动目标最新桥路检查点**：ERC **0/0**；普通DRC错误 **0**，仍有 **22未连接、119警告**，一致性0，**NOT_FAB_RELEASED**。主差分输入已成对、同面、零过孔；J3物理顺序已旋转。TIM2寄存器后端模型测试通过，23项host＋2项MCU测试通过，最终ELF/板上未完成。详见 [桥路与时基检查点](ANALOG_CHECKPOINT_20260923_CN.md)。下方旧数字为历史。


目标仍活动，**未交付、NOT_FAB_RELEASED**。本轮属于实质进展，不能标记完成或仅因尚有阻塞而停止独立工作。

## 本轮实测结果

| 项目 | 本轮开始 | 当前主文件 |
|---|---:|---:|
| 官方普通 DRC 错误 | 0 | **0** |
| 未连接 | 40 | **25** |
| DRC 警告 | 108 | **111** |
| 原理图一致性 | 0 | **0** |
| ERC | 先前0/0 | 本轮重跑 **0/0** |
| host/native 合同测试 | 17 | **23项通过** |
| 自有 string runtime 测试 | 未有 | **1项参数化测试通过** |
| ARM 编译 | 无实际目标证据 | **两变体各10个真实ARM目标文件** |
| ARM 最终链接 | 未完成 | **两变体均exit 2** |
| 生产导出 | 拒绝 | **exit 2，25个未连接拦截** |

0 项普通错误不含另列的25个未连接，因此官方DRC仍未通过。警告增加来自器件重排后的丝印，未隐藏：丝印压铜59、丝印重叠38、丝印板边7、文字高度6、背面文字未镜像1。

## LSE与PCB

精确courtyard检查发现Y1最小宽度2.2mm，MCU左侧只有2.15mm，不能直接挪入空隙。独立副本中成组调整：U2上移0.65mm；C2移至F(2.5,3.2)；C3至F(5.2,8.7)；R1至B(3.8,10.4)；Y1至F(2.0,8.6)、180°；C15至F(4.0,8.6)；C16至F(1.05,10.8)。所有受影响的旧LSE、SDA和U2局部铜先移除/重建；保留其他人工铜，C3相接端点同步调整。

- LSE_IN / LSE_OUT 均全F.Cu、零过孔，MCU→晶体中心线分别 **4.489165 / 4.8125mm**，晶体及两电容连接闭合。
- 官方填铜后，226个沿线采样点均覆盖于In1地；In1为单一地铜轮廓。MCU地与C15/C16地的连通性可追溯至接地过孔。证据 `validation/revA2_goal/lse_reference.json`；这是几何参考检查，不是启动裕量、抖动或EMC实测。
- 局部独立审查见 `lse_feed_finish/review.md`；courtyard之外额外空隙Y1–C15约0.04mm、Y1–U2约0.05mm，需装配能力与公差复核。背面UART投影及附近SDA仍需振荡可靠性实测。
- 完成MCU、上拉和去耦的上部3V3；完成ADC/磁簧上拉/去耦电源。为避免过孔贴近不同网铜，调整LED_GATE局部段，将桥激励的一段移入In2并保持In1参考。
- 定位并用三个0.60/0.30mm过孔接入表层地岛；最后一个地过孔间距失败后已调整并重跑，主板不含失败位置。
- 所有编号焊盘网络、尺寸和板框保持，四层/1.0mm/12×35mm不变；工程规则文件未改。新U2保护区随封装整体移动，未删除保护规则。

本轮最终采用 `ground_stitch_finish`，中间失败副本 `lse_cluster`、`lse_finish`、`adc_power`、`ground_stitch` 的官方报告保留。每组坐标/端点/路径在 `.changes.json`；分类变化在 `comparison.json`。`baseline/`、`final/` 是完整回退快照，不得用旧全板生成器覆盖当前板。

## 桥路不能误报完成

实际测得去重后铜段总长：BRIDGE_A+ 17.15mm/0过孔，BRIDGE_A− 15.50mm/2过孔；AIN_P_FILT 3.25mm，AIN_N_FILT 7.15mm；BRIDGE_S+尚无连接。数据在 `bridge_metrics.json`，是全网铜段总长，不是端点最短路径或SI认证。

下一轮优先围绕U4/R8/R9/C13及激励/参考去耦评估局部重排，使桥路更短、更成对，不能仅补最后飞线。现有U4朝向将部分模拟输入置于远离J3的一端，是需解决的布局原因。

## 固件与构建

主机新增显式 `--unwrap-timestamps --max-sample-gap-us N`，支持正常uint32回绕；默认仍拒绝回绕，CRC、连续序号、缺测、变体和标定门槛保留。不能从UART v1识别任意复位、整周期停顿或65536倍数丢帧；需外部采集条件支持声明。时间展开不是异步重采样。详见 `firmware/host/VERIFICATION_TIME_UNWRAP_CN.md`。

发现未在PATH中的现有 LLVM 23.1.0；没有安装依赖。新增真实最小string实现、C startup、STM32G031F8 linker script，以及两变体object目标。主任务重新执行 `make -B ... objects-both`，20个对象均经ELF header和符号审计确认为ELF32/EM_ARM/ET_REL；**目标文件不是可烧录固件**。实际链接缺ld.lld，尚缺__aeabi_uidiv/__aeabi_lmul/__aeabi_uldivmod运行库；两变体均exit2，无最终ELF。详见 `firmware/mcu/VERIFICATION_ARM_OBJECTS_CN.md`。

已提出Homebrew `arm-none-eabi-gcc`及其依赖的安装授权问题；你提供的AGENTS.md要求新增依赖必须明确授权。等待期间继续PCB等独立工作，未擅自安装。即使链接通过，HAL、真实时钟/总线/ADC/Stop、CubeMX及板上验证仍不能关闭。

## 实际命令与证据

主任务执行日志在 `validation/revA2_goal/commands.json`：

```sh
python3 -m unittest discover -s firmware/host/tests -v
python3 -m unittest discover -s firmware/mcu/tests -v
make -B -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang
python3 firmware/mcu/tests/verify_arm_objects.py /opt/homebrew/opt/llvm/bin/llvm-nm
make -C firmware/mcu all CC=/opt/homebrew/opt/llvm/bin/clang VARIANT=0
make -C firmware/mcu all CC=/opt/homebrew/opt/llvm/bin/clang VARIANT=1
python3 tools/validate_revA2.py
git diff --check
```

另用官方CLI绝对路径重跑 `pcb drc --severity-all --refill-zones --save-board --schematic-parity`、错误级DRC，及 `bash tools/export_fab_revA2.sh` 内ERC/DRC。结果见当前Rev.A2报告与 `export_gate.log`。没有生产Gerber、钻孔或最终贴片文件。

## 仍未达到交付标准

- 25个连接缺口、111个警告；桥路成对/长度/回流质量未关闭，余下SPI/I²C/复位/控制信号需完成。
- U3引出及PAD2LID方案仍缺专用参考；U2原厂land/钢网交叉验证仍开放。
- 所购CT05、电芯允许充电电流/尺寸/保护板、采购后缀仍缺；Rev.A2壳体与器件装配STEP/3D干涉未完成。
- ARM最终ELF和完整HAL未完成；无样机、压力/盐水/梁标定/首件或板上验证。
- 原工程忽略的5类检查尚需审查，不能据当前普通错误0推定所有制造检查已覆盖。

本轮变更集中于主PCB/官方报告、固件Makefile/runtime/tests、host解码与测试、状态文档；全部已有工作和Rev.A1保留，未提交或重置分支。具体后续队列见 `repair_queue.csv` 与 `unconnected_by_net.json`。
