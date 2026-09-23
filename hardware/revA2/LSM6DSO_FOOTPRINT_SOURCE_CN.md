# LSM6DSO LGA-14 封装来源与候选几何

复核日期：2026-09-23。状态：**候选封装；尚未通过评估板 Gerber、装配或实物验证**。

## 原厂证据与横纵方向修正

[ST LSM6DSO 数据手册 DS12140 Rev 3](https://www.st.com/resource/en/datasheet/lsm6dso.pdf)
第 142 页 Figure 25 标注：顶视图横向为 W，纵向为 L；尺寸表给出 W=3.00±0.1 mm、L=2.50±0.1 mm、H≤0.86 mm。
因此，pin 1 在左上且 1→4 沿左侧向下排列时，本体投影是 **X=3.0 mm、Y=2.5 mm**。
旧记录将“L×W=2.5×3.0”误当作“X×Y”，并把左右/上下焊盘中心交换，造成角焊盘铜重叠；旧 `LGA-14_2.5x3mm_P0.5mm_LSM6DSO` 文件已删除，不能继续引用。

[ST AN5192](https://www.st.com/resource/en/application_note/an5192-lsm6dso-alwayson-3axis-accelerometer-and-3axis-gyroscope-stmicroelectronics.pdf)
第 2 页 Figure 1 是底视图：1→4 在右侧向下，12→14 在顶部从左向右；镜像为 PCB 顶视图后为左侧 1→4、顶部 14→12，与项目 IMU14 脚号一致。不得直接照抄底视图制作 PCB 顶视图封装。

器件金属端子为 14×0.475±0.05 mm × 0.25±0.05 mm、节距 0.50 mm。
**这些是封装金属端子尺寸，不是 PCB land 推荐尺寸；不能仅由端子尺寸推定 PCB 焊盘已经合格。**

## 当前项目候选几何

文件：`SmartApoRevA2.pretty/LGA-14_3x2.5mm_P0.5mm_LSM6DSO.kicad_mod`。

采用 KiCad 10.0.6 安装库 `Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y` 的全部 14 个焊盘位置、铜尺寸与圆角参数。
该库描述引用 LSM6DS3TR-C；这里借用其可核对的几何，**不将其当成 LSM6DSO 原厂认可或评估板验证结果**。

| 项目 | 当前候选值 |
|---|---|
| 本体顶视投影 | X=3.0 mm、Y=2.5 mm |
| 左右焊盘中心 | X=±1.1625 mm；Y=−0.75、−0.25、0.25、0.75 mm |
| 上下焊盘中心 | Y=±0.9125 mm；X=−0.5、0、0.5 mm |
| 铜焊盘 | 左右 0.625×0.35 mm，上下 0.35×0.625 mm |
| 圆角 | roundrect_rratio=0.25 |
| 顶层禁布投影 | X=±1.50 mm、Y=±1.25 mm 全投影禁过孔/覆铜；仅径向 0.20 mm 通道允许 0.15 mm 引线，其他区域禁线 |
| Courtyard | X=±1.75 mm、Y=±1.50 mm |

0.625×0.35 mm 是保留的 KiCad 候选铜几何，**不是数据手册直接给出的推荐 land**。
[ST TN1383](https://www.st.com/resource/en/technical_note/tn1383-pcb-design-guidelines-for-mems-sensors-stmicroelectronics.pdf)
第 6 页引用 TN0018：端子间隙大于 0.2 mm 时，PCB land 长宽各在端子尺寸上增加 0.1 mm；按标称尺寸得到 0.575×0.35 mm 另一候选。
最终选择仍须结合角间隙、制造规则、端子公差及装配工艺确认，不因 DRC 通过而视为装配验证通过。
该指南同时要求连接走线对称、沿焊盘长轴向外引出，不在器件顶层投影内放置走线或过孔。更新 PCB 封装时必须同步调整相关走线，不能仅移动焊盘后保留旧铜。

## 仍开放的验证项

- [ST STEVAL-MKI196V1 官方页面](https://www.st.com/en/evaluation-tools/steval-mki196v1.html) 明确列有 GERBER v1.0（2018-09-04），不能再写“原厂没有 Gerber”。本次尚未取得文件：沙箱内代理连接失败，直接访问时原厂接口返回 HTTP 567；网页索引可读不等于压缩包已获取。铜、阻焊及钢网尚未与该评估板交叉验证。
- 当前 F.Mask/F.Paste 随焊盘生成，未声称满足 TN1383 钢网开口面积或实际装配厂工艺；应在取得原厂 Gerber及板厂/贴片厂工艺后评审。
- 所购准确后缀、封装版本、焊接可靠性和传感器偏置需核对/实测。
- 尚无项目绑定且核验过的 LSM6DSO 3D 模型，未通过壳体/STEP 干涉检查。
- 新封装解析和几何检查不替代整板官方 ERC/DRC；整板结果由独立检查报告记录。所有发布门槛保持有效。

## 本轮官方整板检查发现的规则阻塞

`validation/revA2_20260923/stage14_probe/drc.json` 证明：从 U2 pad2 向外直引 0.4875 mm 地线仍违反整个本体投影禁布。该副本未合入。需用原厂证据明确端子逃线通道与本体下保护区，而不是删除规则或豁免 DRC。当前新几何解决角焊盘短路，但并不代表可布线性或最终封装审核已经完成。

## 后续：逃线规则已实现（工程解释）

依据同一 TN1383 §3.2–3.5，现为完整投影禁via/pour＋14个独立径向通道的track guard。0.20 mm通道是本项目工程数值，非ST推荐值。焊盘几何不变，已接地与供电均采用0.15mm线。2000点几何检查、官方正反例及独立只读复核见 `validation/revA2_continue/u2_rule_evidence.json` 和 `CONTINUATION_20260923_CN.md`。上节矩形规则阻塞是修复前诊断，不是当前未解决项。官方Gerber、land/钢网、3D及实物验证仍开放；U3未套用本规则。
