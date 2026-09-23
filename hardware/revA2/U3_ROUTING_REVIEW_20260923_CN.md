> 后续证据更新：原厂Gerber已从Downloads找回且哈希/CRC核验通过，中央接地与外围逃线已直接解析。此前“未取得原包”结论仅为历史。详见 U3_ESCAPE_CHECKPOINT_20260923_CN.md 和 validation/revA2_u3_recovered/RECOVERED_GERBER_REVIEW_CN.md。pin4为INT_DRDY，本项目不使用并标记no-connect。

# U3 LPS28DFWTR 原厂约束与逃线审查

日期：2026-09-23。范围：只读审查正式 Rev.A2 原理图、PCB、工程规则、封装及来源记录；本次仅新增本文，未修改电气网络、封装、PCB 或规则。结论不构成制造放行，状态仍为 `NOT_FAB_RELEASED`。

## 结论

1. **六外围焊盘向外逃线有原厂原则依据，但本次没有取得足以证明“LPS28DFW 六个径向开口的具体形状和尺寸已获原厂验证”的布局证据。** 可形成工程方案，不能把通用建议直接升级为该封装的已批准例外。
2. **PAD2LID 电气浮空是数据手册明确允许的选项。** 当前正式设计选择 GND；维持或改变该选择是电气/系统设计决策，不能以消除 DRC 未连接项为理由偷偷改网。
3. ST 官方仍列出 STEVAL-MKI225A Gerber 1.0（2022-03-25）；本次下载再次返回 HTTP 567，未获得有效 ZIP。官方原理图可读，但不能代替铜层和钻孔布局。

## 一、可验证的原厂事实

### PAD2LID

[DS13317 Rev 1，2021-12，LPS28DFW 数据手册](https://www.st.com/resource/en/datasheet/lps28dfw.pdf) **第 1/51 页 Description** 对金属盖给出的关键原文是：

> “optionally, connected to ground or left floating electrically in the application PCB layout.”

前后文指出连接方式取决于客户目标应用。**第 3/51 页 Table 1** 将 pin 7 定义为 PAD2LID，功能为连接金属盖。因此允许的是盖子对应焊盘的**电气浮空**，不是明确允许删除中央铜焊盘、取消焊接或改变钢网。

[STEVAL-MKI225A 官方原理图 Rev 1，2022-03](https://www.st.com/resource/en/schematic_pack/steval-mki225a_schematic.pdf) 第 1/6 页 Figure 1 提供 PAD7 接 GND 的参考电路；它证明接地方案存在，不能证明接地走线经过何处。

### 顶层禁布与向外连接

[TN1383 Rev 1，2023-08](https://www.st.com/resource/en/technical_note/tn1383-pcb-design-guidelines-for-mems-sensors-stmicroelectronics.pdf)：

- **第 7/24 页 §3.2、Figure 4**：连接应对称、同宽，地平面通过普通走线连接焊盘。方向原文为：“All traces should flow outside the component, parallel to the long edge of the pad.”
- **第 8/24 页 §3.3、Figure 5**：不要在器件下方顶层布线或放过孔。
- **同页 §3.4、Figure 6**：压力传感器允许器件下方底层信号走线或电源平面；这不等于允许通过器件下方过孔转到底层。
- **第 9/24 页 §3.5**：通用 LGA 反例说明应把焊盘下过孔移到器件外，引线直接向外；该反例的 pin 6/7 属于图中的器件，不能混同为 LPS28DFW PAD2LID 必须接地。

[TN0018 Rev 8，2025-03，官方索引地址](https://www.st.com/resource/en/technical_note/CD00134799.pdf)：本次 ST 域名搜索索引可取得 **第 13/37 页 §3.8、Figure 14** 的对称连接及普通走线接地要求，以及 **第 14/37 页 §3.9/3.10、Figures 15/16** 的顶层禁布、底层允许说明。直接打开该 PDF 及索引给出的长文件名返回 404，故本次对 TN0018 的确认限于**官方搜索索引文本**，未重新取得完整 PDF；上述要求由本次可完整读取的 TN1383 交叉支持。

## 二、正式文件的可验证状态

检查对象：`smart_apo_common_revA2.kicad_pcb`、同名 `.kicad_sch/.kicad_pro`、`netlist_revA2_kicad10.xml`、`SmartApoRevA2.pretty/LPS28DFW_CCLGA-7L.kicad_mod`、`OFFICIAL_COMPONENT_REVIEW_CN.md`、`LPS28DFW_FOOTPRINT_SOURCE_CN.md`。

| 项目 | 读取结果 |
|---|---|
| U3 位置 | 顶层，中心 (6.0, 2.4) mm，无旋转 |
| 外围 pad 1/4 | 局部中心 (±1.125, 0)，尺寸 0.35 × 1.40 mm |
| 外围 pad 2/3/5/6 | 局部中心 (±0.575, ±1.125)，尺寸 0.90 × 0.35 mm |
| pad 7 | 中心 (0,0)，0.90 × 0.90 mm，PCB 与导出网表均为 `/GND` |
| 其他网络 | 1 SDA；2 GND/SA0；3 SCL；4 原理图 NC 对应 unconnected 网络；5 GND；6 3V3 |
| U3 禁布 | F.Cu 本体投影矩形，局部 ±1.4 mm；禁止 tracks/vias/copperpour，允许 pads；PCB 绝对范围 (4.6,1.0)–(7.4,3.8) mm |
| 工程制造下限 | 线宽/间距 0.15 mm；过孔外径 0.60 mm；孔径 0.30 mm；铜至板边 0.25 mm |

外围焊盘最外铜边位于局部 ±1.30 mm，本体禁布到 ±1.40 mm：所有外围连接都必须跨越至少 **0.10 mm 的非焊盘带**才能离开当前矩形。允许焊盘本身不等于允许引线跨越这条带。因此，现有硬性 keepout 与必要逃线之间存在几何冲突；不能用“焊盘允许”来宣布走线合法。pin 4 为 NC，不需要为了凑齐六条线而新增电气连接。

历史来源记录给出官方 ZIP 的 SHA-256：`3ada96e8f5379a3faae7fded4939724d4bf06484e59954bf688c2410324ce10f`，并记录由 Gerber 得到铜/阻焊/钢网尺寸。**这是已有项目追溯记录，本次没有重新获得原始 ZIP 验证该散列，也未从这些尺寸记录推导出原厂逃线路径。**

## 三、工程推论与未证实项

- 将必要连接从外围焊盘沿最短外向路径引出、保持对称同宽、过孔置于本体外，符合减少器件下方横穿走线的设计意图；可作为待核准的工程候选。
- 但当前外围长条焊盘的长边沿封装周边排列：pad 1/4 长边沿 Y，另外四个长边沿 X；最短径向逃线恰与长边垂直。**不能声称径向方案逐字符合 TN1383 的“平行长边”表述。** 需要该特殊 CCLGA 封装的官方实板铜层，或 ST 针对封装的说明，解决通用指引与实际焊盘形状的对应关系。
- 中央 pad7 若保持 GND，任何顶层普通走线必须经过本体内部；直接打过孔也触及现有禁布。只为六外围焊盘开通道并不能自动解决 pad7。
- PAD2LID 浮空虽被允许，仍需系统级确认金属压力口、外壳、液体接触、ESD/屏蔽策略；数据手册没有为本项目直接选择该选项。本次不做选择，也不把它包装成 DRC 修复。
- 未验证：官方 Gerber 中 pad7 的实际接地路径、是否含焊盘内孔/特殊工艺、外围精确引出方向与线宽、机械应力与压力偏移实测。底层允许布线不消除这些问题。

## 四、官方资源可取得性及最小后续动作

[ST 产品页](https://www.st.com/en/evaluation-tools/steval-mki225a.html) 可读取并列出 Gerber、BOM 和原理图。其 [官方 Gerber ZIP](https://www.st.com/resource/en/board_manufacturing_specification/steval-mki225a_gerber.zip) 在网页工具中因不支持 ZIP 类型无法读取；一次可联网 shell 下载得到 **HTTP 567、7352 字节错误响应**，不是有效 Gerber。停止重试该接口。本次未取得可靠的官方铜层布局图；产品照片和电气原理图不能替代它。

最小下一步：

1. 优先找回历史散列对应的已下载官方 ZIP；否则由正常 ST 下载渠道或 ST 技术支持取得官方制造包。保存有效 ZIP、散列和铜层/钻孔局部图，核对 pad1–7 实际接法。
2. 先在评审文件中确定 pad7 继续接地的实现路径及工艺；若考虑浮空，作为明确的电气设计变更单独审查，不能静默删网。
3. 证据足够后，才把 keepout 调整为保留内部禁布、只允许已核准外向引线的精确几何；保留当前线宽、间距和过孔制造下限。规则变更应有依据和评审记录，不能仅因为 DRC 报错而降级。
4. 在隔离副本验证允许路径，并增加反向检查：内部横穿线、本体内过孔和错误网络仍须被发现；随后重新运行官方 ERC/DRC 与原理图一致性检查。所有检查通过前不宣称 U3 已完成布线或已可投板。

本文为证据审查，无代码简化、无生产文件变更；未运行制造放行检查，也不沿用历史 DRC 数字作为本次结论。
