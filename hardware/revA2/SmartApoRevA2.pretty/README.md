## W25Q256JV E 封装更新（2026-09-23）

`WSON-8_W25Q256JV_8x6mm_AN0000009.kicad_mod`依据Winbond AN0000009 Rev2.1第21页land/stencil与RevR机械图，中央PCB铜3.25×4.05mm，pad9浮空。已替换不匹配Microchip EP6×4.8库封装；3D模型未核验而不附。来源、翻面、复核和仍开放的工艺条件见上级`FLASH_LAND_CHECKPOINT_20260923_CN.md`。不是整板放行。

> 2026-09-23：现用 IMU 封装是 `LGA-14_3x2.5mm_P0.5mm_LSM6DSO`，旧 X/Y 几何已更正。land/钢网及禁布逃线仍待评审，见 `../LSM6DSO_FOOTPRINT_SOURCE_CN.md` 与 `../DEVELOPMENT_20260923_CN.md`。

# Rev.A2 project footprint library

`LGA-14_2.5x3mm_P0.5mm_LSM6DSO.kicad_mod` is the Rev.A2 LSM6DSO land
pattern from ST DS Figure 25 (2.5 x 3.0 mm body, 0.50 mm pitch). See
`../LSM6DSO_FOOTPRINT_SOURCE_CN.md`. The KiCad library 3.0 x 2.5 mm LGA-14
is LSM6DS3 and must not be used.

`LPS28DFW_CCLGA-7L.kicad_mod` is reconstructed from ST's official
STEVAL-MKI225A copper, mask, and paste Gerbers and cross-checked against
DS13317 Rev 1. It includes a top-side trace/via/copper-pour keepout beneath the
2.8 x 2.8 mm body. See `../LPS28DFW_FOOTPRINT_SOURCE_CN.md`.

`REED_CT05_COMPACT.kicad_mod` is a board-fit CT05-class land pattern (body
5.1 x 1.9 mm, courtyard 6.8 x 2.8 mm). The KiCad library CT05 courtyard is
11.65 mm wide and cannot fit the 12 mm board; the purchased reed drawing must
still be checked before SMT.


2026-09-23 U3更新：LPS28DFW保留完整F.Cu本体禁via/pour；仅0.25mm几何通道允许在用外围脚和pad7→5原厂路径，铜线0.20mm。来源与正反例见 ../U3_ESCAPE_CHECKPOINT_20260923_CN.md；不能恢复为全矩形track禁布，也不能整体移除guard。

2026-09-23 D1：`LED_0805_2012Metric_RevA2_EdgeSilk`由当前板LED_SMD:LED_0805_2012Metric派生，只裁短两段板边丝印，焊盘/钢网/阻焊/模型不变。保留原轮廓开放端方向，不作为所购LED极性验证。详见 ../BOTTOM_SILK_CHECKPOINT_20260923_CN.md。

2026-09-23：TSSOP-20_4.4x6.5mm_P0.65mm_RevA2_Pin1由板内标准TSSOP封装派生，仅平移1脚丝印三角形；U5的WSON项目库同步平移同类标记。详见 ../PIN1_SILK_CHECKPOINT_20260923_CN.md，不改变铜与装配方向。

D1极性更正：现用LED_0805_2012Metric_RevA2_K1，1=K、2=A，与LED_AK_REVA2符号匹配。旧EdgeSilk仅为历史，不能继续用于D1。封装旋转180°，原物理铜连接不变。见 ../D1_POLARITY_FIX_20260923_CN.md。
