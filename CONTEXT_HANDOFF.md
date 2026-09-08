# 智能阿波 + 智能水中项目交接上下文

> 目标放置目录：`/Users/qs/Documents/smart_apo_revA 2`
>
> 下一智能体开始工作前，必须先完整阅读本文件、`README_CN.md`、`hardware/PCB_RELEASE_CHECKLIST_CN.md` 和 `validation/revA1_validation_report.json`。不要把当前PCB误认为可直接投板版本。

## 1. 项目目标

设计一套面向真实海钓环境的双端研究系统：

- **智能阿波**：通过IMU、压力信号检测鱼讯，并以快速闪光提示，不需要无线实时通信。
- **智能水中**：安装在子线/鱼钩附近，通过316L弹性梁和应变桥直接记录钩侧张力，作为原型研究阶段的“教师传感器”。
- 两端独立记录原始数据，回收后自动对时；水中张力生成教师标签，自动优化阿波侧检测参数。
- 目标是可靠区分海浪/流致扰动与钩侧机械事件。必须注意：张力事件不等价于“鱼咬钩”，最终语义真值仍需摄像、提竿或捕获结果辅助。

## 2. 用户背景与协作方式

- 用户不了解嵌入式开发和PCB设计，需要按操作顺序解释，避免只给行业术语。
- 用户倾向直接使用定制PCB、SMT和3D打印在真实环境研究，不再做面包板级原型。
- 可以积极完成数字工程设计，但必须明确区分：数字检查通过、官方KiCad ERC/DRC通过、实物验证通过。
- 不得声称未经KiCad官方引擎验证的Gerber可以生产。

## 3. 已锁定的默认参数

| 项目 | 默认值 |
|---|---|
| 阿波外形 | 最大直径32 mm，高49 mm |
| 共用PCB | 12 × 35 × 1.0 mm，4层，ENIG |
| 首批数量 | PCB共10片；装5套阿波、5套智能水中 |
| 电池 | 带保护401020 LiPo，60–80 mAh，线焊 |
| 工作水深 | 10 m |
| 密封验证 | 15 m等效静水压力 |
| 水中张力量程 | 0–2 kgf工作 |
| 梁生存目标 | 独立样件验证≥5 kgf；未试验前不得作为额定载荷 |
| 弹性梁 | 0.30 mm 316L，首批10片 |
| 打印工艺 | PA12 MJF/SLS |
| 水中负浮力 | 海水中−2.900 g |
| 水中空气称重目标 | 23.294 g（按海水密度1.025 g/mL） |

## 4. 核心电气方案

### 4.1 共用核心板

- MCU：STM32G031F8P6，LCSC `C529334`。
- IMU：LSM6DSOTR，LCSC `C2655100`。
- 压力：LPS28DFWTR，LCSC `C3263277`。
- Flash：W25Q256JVEIQ，LCSC `C97522`；备选`C5334276`必须复核封装。
- 充电：MCP73831T-2ACI/OT，LCSC `C424093`。
- LDO：TPS7A0233PDBVR，LCSC `C2887324`。
- 低漂移时基：32.768 kHz晶振，接PC14/PC15。
- 磁簧开关只作唤醒输入，不能承载电池主电流。

此前曾考虑STM32U031F8P6，后因采购可用性和成熟度改为STM32G031F8P6。后续不要无理由改回U031。

### 4.2 智能水中专用

- 应变ADC：NAU7802SGI，LCSC `C5180029`。
- 采样上限：320 SPS。
- DVDD为3.3 V；内部LDO/AVDD及桥激励暂定3.0 V，确保DVDD高于AVDD约0.3 V。
- 350 Ω全桥，预计激励电流约8.6 mA。
- 六线桥接口：`E+ / E- / S+ / S- / A+ / A-`。
- NAU7802 `REFP/REFN`接远端`S+/S-`，以补偿细线激励压降。
- 差分输入：`A+ / A-`经R8/R9进入`VIN1P/VIN1N`。

### 4.3 阿波专用

- 红色高亮LED及MOSFET驱动。
- 水中版本不贴Q1、D1、R6、R7。
- 阿波版本不贴U4、J3、R8、R9、C6、C7、C13。

完整DNP规则见`hardware/ASSEMBLY_VARIANTS_revA1.csv`。

## 5. MCU引脚映射

| TSSOP20引脚 | MCU引脚/功能 | 网络 |
|---:|---|---|
| 1 | PB7 | I2C_SDA |
| 2 | VDD/VDDA | 3V3 |
| 3 | PA1/ADC | VBAT_SENSE |
| 4 | PF2/NRST | NRST |
| 5 | PB6 | I2C_SCL |
| 6 | PA13 | SWDIO |
| 7 | PA5 | SPI_SCK |
| 8 | PA6 | SPI_MISO |
| 9 | PA7 | SPI_MOSI |
| 10 | PB0 | LED_GATE |
| 11 | PA3 | UART_RX |
| 12 | PA14 | SWCLK |
| 13 | VSS/VSSA | GND |
| 14 | PA4 | FLASH_CS |
| 15 | PC14 | LSE_IN |
| 16 | PC15 | LSE_OUT |
| 17 | PA9 | REED_WAKE |
| 18 | PA10 | STRAIN_DRDY |
| 19 | PA0 | IMU_INT |
| 20 | PA2 | UART_TX |

正式放行前必须用最新STM32G031F8P6数据手册/CubeMX再次验证复用功能。

## 6. 现有文件与状态

### 6.1 原理图

文件：`hardware/smart_apo_common_revA1.kicad_sch`

- KiCad 9格式，可由KiCad 10打开并转换。
- 42个器件，11个嵌入式自定义符号定义。
- 生成器结构校验无报错，`kiutils`可解析。
- 引脚网络清单：`hardware/pin_net_review_revA1.csv`。
- 生成脚本：`tools/generate_schematic.py`。

**重要限制：**当前自定义符号的引脚主要定义为`Passive`，因此“结构校验通过”不代表正式ERC有充分覆盖。下一版本必须用原厂/正式符号重建，或逐脚设置正确电气类型后再运行ERC。

### 6.2 PCB

文件：`hardware/smart_apo_common_revA1_NETS_PLACED.kicad_pcb`

- 12 × 35 × 1.0 mm，4层。
- 42个封装。
- 35个网络（包含空网络）。
- 2个内层平面定义。
- 走线数量为0。
- `kiutils`可解析。
- 状态明确为：`BLOCKED_NO_ROUTING_NO_OFFICIAL_DRC_NO_GERBER`。
- 生成脚本：`tools/generate_pcb.py`。

**不要直接在该文件上投板。**建议把它作为布局参考；正式符号/封装完成后，从审核后的原理图重新更新/建立PCB。

### 6.3 LPS28DFW封装

这是当前最高优先级风险。

- 当前U3封装只是工程暂定封装。
- 当前近似焊盘：外围6个约0.45 × 0.55 mm，中央7号约0.65 × 0.65 mm。
- 必须从ST产品页面获得原厂EDA模型，并对照最新数据手册及TN0018复核：焊盘编号、铜焊盘、阻焊、钢网、Pin 1、中央PAD2LID、Courtyard、压力孔和机械禁布区。
- 当前7号PAD2LID接GND；ST允许金属盖按应用接地或悬空，因此该选择还需结合盐水环境、EMC和密封结构确认。
- U3上方压力孔必须无遮挡，O形圈不得堵孔或把压紧力传给陶瓷底座。
- 传感器下方避免过孔和不对称铜结构，远离螺钉、板弯曲区和梁固定点。

参考：

- ST LPS28DFW产品页：<https://www.st.com/en/mems-and-sensors/lps28dfw.html>
- ST TN0018：<https://www.st.com/resource/en/technical_note/tn0018-handling-mounting-and-soldering-guidelines-for-mems-devices-stmicroelectronics.pdf>

### 6.4 BOM/CPL

- BOM：`hardware/BOM_revA1_JLCPCB.csv`。
- 双版本装配：`hardware/ASSEMBLY_VARIANTS_revA1.csv`。
- 当前布局坐标：`hardware/CPL_revA1.csv`。

当前CPL只能用于审查，最终布局改变后必须从正式KiCad PCB重新导出。BOM中已锁7个核心LCSC料号；通用阻容、LED、MOSFET、晶振、磁簧管需在下单当天锁定实际可贴料号。

### 6.5 机械文件

- 参数源：`mechanical/smart_apo_revA.scad`。
- 阿波：主体、上盖、电子仓托架STL。
- 水中：两半壳、配重盒STL。
- 弹性梁：`mechanical/316L_flexure_0p30mm_revA.dxf`。
- 梁预览STL标明`NOT_FOR_PRINTING`，真正梁必须316L加工。
- 所有STL经处理后的封闭网格检查通过。
- 弹性梁规范：`mechanical/316L_FLEXURE_SPEC_CN.md`。
- 打印装配说明：`mechanical/PRINT_AND_ASSEMBLY_CN.md`。

注意：当前3D模型是工程验证几何，不是已经完成公差、O形圈压缩率和15 m压力验证的生产壳体。

### 6.6 自动调参工具

- 协议：`firmware/DATA_AND_AUTOTUNE_PROTOCOL_CN.md`。
- 主程序：`firmware/host/autotune.py`。
- 合成数据生成：`firmware/host/generate_synthetic_dataset.py`。
- 使用说明：`firmware/host/README_CN.md`。
- 合成数据结果：`firmware/host/example_result.json`。

当前链路包括：

1. 两端起始/结束三次敲击检测。
2. 线性拟合时间偏移和时钟漂移。
3. 水中张力高通+MAD阈值生成教师事件。
4. 阿波加速度、角速度、压力变化率生成特征。
5. 按连续时间60%/20%/20%切分训练/验证/测试，禁止随机打散相邻窗口。
6. 网格搜索权重、阈值和最短持续时间。
7. 报告事件级F1、精确率、召回率和每小时误报数。

合成双端日志的对时RMS残差约0.27 ms，烟雾测试通过。当前工具只产生候选参数，刻意不做自动刷机。参数必须在下一次完全未参与寻参的独立航次继续优于旧参数，才允许升级，否则回滚。

## 7. 已完成验证

验证文件：`validation/revA1_validation_report.json`

- 原理图解析：PASS。
- PCB解析：PASS。
- 机械STL封闭性：PASS。
- 自动调参合成数据烟雾测试：PASS。
- 总结状态：`PASS_WITH_FABRICATION_GATES`。

仍未通过/未执行：

- 原厂封装逐项验证。
- 正式原理图ERC。
- PCB布线。
- KiCad官方DRC及原理图一致性检查。
- Gerber/钻孔/CPL独立查看。
- 电池实物尺寸与保护板确认。
- 15 m等效压力试验。
- 316L梁0–2 kgf标定和≥5 kgf生存试验。

## 8. 下一智能体优先任务

### 阶段A：把Rev.A1升级成Rev.A2生产候选版

1. 不直接修改Rev.A1，建立`revA2`工作副本。
2. 获取并核对所有核心器件最新原厂数据手册。
3. 用正式符号重建原理图，设置正确电气引脚类型。
4. 逐脚复核STM32G031、LSM6DSO、LPS28DFW、NAU7802、W25Q256、MCP73831和TPS7A02。
5. 建立项目级`.kicad_sym`与`.pretty`库。
6. 从ST原厂CAD/数据手册重建LPS28DFW封装，并按TN0018添加禁布约束。
7. 复核其余封装、Pin 1和采购封装后，运行正式ERC。
8. 从审核后的原理图重新建立PCB；旧PCB仅作布局参考。

### 阶段B：四层布局布线

推荐层叠：

| 层 | 用途 |
|---|---|
| F.Cu | 器件及主要信号 |
| In1.Cu | 连续GND |
| In2.Cu | 3V3/VBAT电源 |
| B.Cu | 低速信号/少量器件 |

推荐初始规则：普通信号0.15 mm，电源0.25–0.35 mm，间距0.15 mm，过孔0.45/0.20 mm，铜到板边≥0.25 mm。最终以实际板厂能力为准。

布线顺序：

1. J3—R8/R9—NAU7802桥路差分输入。
2. 六线桥的Sense/Reference和Excitation。
3. LSE晶振。
4. 电源和去耦。
5. SPI Flash。
6. I²C。
7. SWD/UART/中断/LED/磁簧等低速信号。
8. GND平面、3V3/VBAT平面和地过孔。

桥路输入要求短、并行、基本等长，尽量无过孔，保持连续地参考，远离SPI时钟、LED和充电回路。晶振短、对称、无过孔。

### 阶段C：生产输出

1. 使用KiCad官方引擎运行ERC和DRC。
2. DRC要求短路、未连接、间距、线宽、板框错误均为0。
3. 使用3D Viewer检查外形、压力口、Pogo、电池和壳体干涉。
4. 导出F/B及两内层铜、F/B阻焊、F/B丝印、Edge.Cuts和钻孔文件。
5. 用Gerber Viewer独立复核。
6. 最终PCB重新导出BOM和CPL。
7. 同一PCB建立阿波、水中两套SMT装配订单，严格执行DNP表。

## 9. 当前环境限制

此前生成Rev.A1的执行环境没有KiCad/OpenSCAD命令行程序，所以：

- KiCad文件通过Python生成并用`kiutils`解析。
- 机械STL通过Python几何工具生成和检查。
- 没有官方KiCad ERC/DRC报告。
- 没有完成走线。
- 没有Gerber。

如果下一智能体所在环境有`kicad-cli`，应优先使用官方引擎，不应继续只靠文本生成器模拟DRC。可检查：

```bash
kicad-cli version
kicad-cli sch erc --help
kicad-cli pcb drc --help
```

## 10. 当前重建与检查命令

在项目根目录执行。Python依赖包括`numpy scipy trimesh shapely manifold3d mapbox_earcut kicad-sch-api kiutils`。

```bash
python tools/generate_artifacts.py
python tools/generate_schematic.py
python tools/generate_pcb.py

python firmware/host/generate_synthetic_dataset.py
python firmware/host/autotune.py \
  firmware/host/example_data/awa.csv \
  firmware/host/example_data/underwater.csv \
  -o firmware/host/example_result.json

python tools/validate_revA1.py
```

不要在改过电气设计后盲目运行旧生成脚本覆盖正式手工审核结果；进入Rev.A2后，应把生成器同步升级或将其标记为Rev.A1归档工具。

## 11. 实物阶段不可由智能体替代的工作

- 316L材料、厚度、毛刺、平面度和加工质量确认。
- 应变片粘贴、固化、防水涂覆和绝缘检查。
- 真实0–2 kgf多循环标定、回差和温漂测量。
- 独立样件≥5 kgf生存/破坏试验。
- 电池尺寸、保护电路、充电温升和密封状态检查。
- 15 m等效压力测试。
- 盐水浸泡、腐蚀和湿式触点检查。
- SMT首件焊点、器件方向和必要的X-ray/AOI确认。

## 12. 下一智能体可直接采用的任务描述

> 请先完整阅读`CONTEXT_HANDOFF.md`及其中指定文件。基于现有Rev.A1建立独立Rev.A2生产候选版本，不覆盖Rev.A1。先对照最新原厂资料重建具有正确电气引脚类型的正式原理图和项目封装库，重点按ST LPS28DFW原厂CAD、数据手册及TN0018重建U3封装。随后完成12 × 35 × 1.0 mm四层共用PCB的低噪声布局布线，保留阿波/水中两个装配变体。必须使用KiCad官方ERC/DRC验证后才能生成Gerber、钻孔和最终BOM/CPL。任何无法完成的官方工具验证或实物验证均需明确标记为阻断项，不得推定通过。
