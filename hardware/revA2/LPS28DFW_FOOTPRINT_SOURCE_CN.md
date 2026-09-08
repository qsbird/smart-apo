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
