# IMU逃逸与MCU通道候选 · 2026-09-23

正式板未修改，SHA256仍为 `e30fa2c0394ecc5481a546963db4facbde0a48d4c5758d725a5c8614be59d672`。保存的主板官方结果0普通错误/2未连接/111警告、ERC0/0、一致性0、无ignored/exclusions，NOT_FAB_RELEASED。该保存结果不是本轮重跑主板验证。

## 已收敛的独立逃逸候选

validation/revA2_imu_escape_rebuild/final_snapshot保留完整不可覆盖检查点：U2右移0.23mm、C10右移0.18mm，所有受影响的F径向引线明确重建；IMU via(.65,6.8)，In2经(1.2,6.8)、(1.4,7.0)到(1.4,8.75)。没有仅改封装坐标或用旧铜压新焊盘。官方普通错误0、2原未连接、114警告、一致性0；未完成线尾track_dangling如实保留。

前两处新参考缺口通过实际改变3V3横段与IMU In2路径消除，未扩大容差。最终关键参考PASS、新铜unexpected_missing=0、无新via/SMT焊盘重叠。candidate.py可从最新主板重放到独立replay，不覆盖主板或final_snapshot。

来源记录DS12140 Rev3尺寸3.0±0.1、2.5±0.1时，U2最大本体左界0.98mm，via铜环右界0.95mm，仅余0.03mm；名义尺寸余量0.08mm。没有包含贴装位置误差和板厂钻孔/铜盘误差，不能宣称制造公差通过。U5最大EP净距3.525mm。完整MCU连接仍未完成，未采用该逃逸候选作为正式板。

## 首次完整连接尝试，拒绝

主任务在独立validation/revA2_imu_connect/stage1尝试相关SCK/UART_RX/NRST/DRDY通道重排与IMU跨层连接，并保持LSE零过孔。实际运行KiCad内置Python edit.py、官方 `kicad-cli pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity` 和 tools/check_reference_revA2.py显式填铜。

官方结果4 shorting_items、2 clearance，未连接改为3V3与MOSI各1处；不能用“IMU端点连通”抵消新增供电开路。具体冲突：

- SWCLK B横线y13.45碰新DRDY via(6.2,13.7)、NRST via(4.4,13.7)，并与IMU via(4.9,13)间距不足。
- SCK In2新路径穿过3V3 via(5.4,10.4)，同时影响供电区域连接。
- IMU via(4.85,11.4)与F供电横线y11.925间距不足。
- UART_RX F新路径碰SDA via(5.8,12.85)。

显式参考诊断：六条敏感网均无缺失样点，In1仍单轮廓，但3条未改外层铜产生新参考损失，报告GEOMETRY_REVIEW_REQUIRED；未处置为通过。精确坐标/UUID、报告与拒绝决定见stage1/drc.json、reference.json、decision.json。主板散列复核不变，没有导出制造文件。

## 下一步

继续在隔离副本对上述明确通道进行成组重排，尤其不能遗漏SWCLK/SWDIO及供电横线；不要直接复用本失败候选或仅挪端点。先保持供电与既有总线完整，再看IMU是否闭合；全部新/变化铜的参考都必须复核。

已另询问目标板厂及四层工艺的实际孔径/铜盘/填孔能力。在资料明确前维持0.60/0.30mm，不因布线拥挤擅自降低制造下限。所购Pogo接触头/治具定位资料问题仍待答复；没有把等待当授权。固件及正式PCB本轮未改，目标未完成。
