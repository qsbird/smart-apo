> 最新U3/C13检查点（2026-09-23）：C13可见位号修复消除10项警告；U3及配套库按最大本体重建禁布，最小理想via余量.10mm/顶部.125mm。官方ERC0/0、DRC普通错误0/未连接0/95警告、一致性0，无忽略/排除，NOT_FAB_RELEASED。见 `hardware/revA2/U3_MARGIN_AND_C13_CHECKPOINT_20260923_CN.md`。以下较小余量和警告数均为历史。

> 最大外形补充（2026-09-23）：已读取并渲染核对DS13317 Rev1第42页Figure19，L/W=2.8±0.15mm，因此最大本体2.95×2.95mm、最大高2.1mm。原2.8mm禁布矩形是名义投影，不能代替最大本体/贴装公差审查。当前顶部两via的最大本体理想净距仅0.025mm，未做贴装公差验证。源PDF、散列和页面证据在validation/revA2_u3_max_body；正式板本轮未改。

> 后续证据更新：原厂Gerber已从Downloads找回且哈希/CRC核验通过，中央接地与外围逃线已直接解析。此前“未取得原包”结论仅为历史。详见 U3_ESCAPE_CHECKPOINT_20260923_CN.md 和 validation/revA2_u3_recovered/RECOVERED_GERBER_REVIEW_CN.md。pin4为INT_DRDY，本项目不使用并标记no-connect。

# LPS28DFW Rev.A2 封装依据

核对日期：2026-09-08。

## 一手来源

- ST `LPS28DFW` 数据手册 DS13317 Rev 1，Figure 3 和 Figure 19。
- ST `STEVAL-MKI225A GERBER` 1.0，发布日期 2022-03-25。
- 官方 ZIP：`https://www.st.com/resource/en/board_manufacturing_specification/steval-mki225a_gerber.zip`
- 下载文件 SHA-256：`3ada96e8f5379a3faae7fded4939724d4bf06484e59954bf688c2410324ce10f`。
- ST TN0018 Rev 8，MEMS 顶层器件投影区禁走线/过孔、连接对称和机械应力要求。

## 从官方 Gerber 复核的焊盘

以 7 号中心焊盘为原点：

| 焊盘 | 中心位置 mm | 铜尺寸 mm | 钢网开口 mm | 阻焊开口 mm |
|---|---:|---:|---:|---:|
| 1、4 | x=±1.125, y=0 | 0.35 × 1.40 | 0.25 × 1.30 | 0.553 × 1.603 |
| 2、3、5、6 | x=±0.575, y=±1.125 | 0.90 × 0.35 | 0.80 × 0.25 | 1.103 × 0.553 |
| 7 | x=0, y=0 | 0.90 × 0.90 | 0.80 × 0.80 | 1.103 × 1.103 |

Gerber 为英制 2.5 格式；以上值由官方文件 aperture 和 flash 坐标换算，四舍五入至 0.001 mm。KiCad footprint 使用每边约 0.1015 mm 阻焊扩展、每边 0.05 mm 钢网收缩。

## 方向与约束

- KiCad footprint 按 PCB 顶视图绘制；DS13317 Figure 19 的封装底视图已进行左右镜像。
- 顶视图 Pin 1 位于左侧竖向焊盘，丝印和 Fab 左上角用于标记 Pin 1 方向。
- 7 号 PAD2LID 保持独立焊盘编号，原理图决定接 GND 或悬空；Rev.A2 当前接 GND。
- F.Cu 器件本体 2.8 × 2.8 mm 投影区设为走线、过孔和铜皮禁布，允许封装自身焊盘。
- Courtyard 采用 3.5 × 3.5 mm；压力口/O 形圈及壳体机械间隙仍须在 3D 和实物装配中验证。
