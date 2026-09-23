# IMU完整连接已采用 · 2026-09-23

正式PCB SHA256 `2cda6a2f41336052446515f330fe0c3524049ff20e5bbc082fcc31f2e64f65c3`。官方普通错误0，未连接2→1（只剩SPI_MOSI），110警告；ERC0/0，一致性0，NOT_FAB_RELEASED。

## 两组独立方案及合并

上部：U2(2.6,5.95)、C10(4.9,6.6)、U7(7.42,6.0)、C9(10.5,6.4)，全部关联铜同步；U2径向引线重新构建，IMU via(.65,6.8)。按3.1×2.6mm最大本体计算，铜环余量由旧候选0.03增至0.10mm，未涵盖实际贴装误差。右侧局部3V3分支保持x11.5、宽度改为0.15mm（仍满足原制造下限），避免向板边外移；不宣称已做载流/压降/温升实测。上部独立证据在validation/revA2_imu_margin/stage4。

MCU通道：SWCLK B横段下移至y14.39；重建SCK、UART_RX、NRST、DRDY及相关供电；SDA via(6.3,12.75)、UART_RX via(5.5,12.6)、NRST via(4.425,13.86)，IMU桥接via(2.4,9.6)、(4.85,11.4)、(4.85,13)。删除冗余(5.4,10.4)供电via，R1 B供电直接接既有(6.2,10.35)via，避免同网孔重叠。MCU独立最终版本为validation/revA2_imu_corridor_fix/try9和final_snapshot；try8曾有孔间距警告，未用作合并源。

合并以try9为底，仅应用旧逃逸版本到上部stage4的几何差异：四个封装位置、上部35新增/36删除线段，无via变化。脚本逐项检查待删除铜、封装原位置及项目规则一致，发现重叠修改即停止；没有整板覆盖式重新生成。合并清单绑定全部输入散列，位于validation/revA2_imu_integrated/stage1/merge_manifest.json。

## 整体实际检查

- 官方KiCad10.0.6 DRC在独立合并板和正式采用后均为0普通错误/1未连接/110警告/0一致性；无ignored_checks或单项排除。
- 合并后显式Fill与实际铜BFS核查IMU、SCK、SDA、SCL、UART_RX、SWCLK、NRST、DRDY、3V3九网所有焊盘连接，全部通过。
- check_invariants.py确认43封装、四层1mm、12×35mm、焊盘网络和规则保持。新via/焊盘审查仍仅原J2两接触孔，未引入元件焊盘内孔。
- tools/check_reference_revA2.py显式填铜：In1单一地轮廓、六敏感网覆盖完整、原外层未改铜无新缺口，PASS_SAMPLED_GEOMETRY_ONLY。
- LSE/桥路均F.Cu零via；原始差分各2.669899mm、滤波主网段各约2.770mm保持。LSE_IN网段合计4.489165mm不变；LSE_OUT网段合计5.984693→5.862542mm。这里是全网段长之和，不能与旧文档单一路径长度混用，不能代替LSE负载/启动实测。

## 严格新铜检查的单独处置

相对正式基线重新按真实线宽检查29391个变化铜中心/边缘样点。严格“距同网via<0.46mm”检查结果仍为false，未改弱阈值。唯一超界来自3V3 F段UUID86d4aecd-d6ea-4d2b-916f-c58ebe159d6e，宽0.15，沿x11.5由y5.51到6.775，随后接电源via(11.45,7.06)。

独立重新Fill确认：地铜右边界x11.6与该via避让区融合，并有0.2mm最小填铜宽裁剪的圆滑过渡。此段55个缺失采样点中，仅5点超0.46，位于x11.575、y6.575787–6.615630，最大距离0.5000868mm；实际失参考区最长约0.201882mm。最近GNDvia(11.325,7.8)距电源via0.750483mm，处于同一地轮廓。明确接受为该处局部电源换层几何，不能称全局新铜参考无例外PASS，也不是EM/PI或板上认证。精确边界、UUID、散列与独立复核依据在reference_disposition.json/merge_review.md。

## 实际命令与回退

```sh
bash tools/export_fab_revA2.sh
python3 tools/validate_revA2.py
python3 tools/check_divider_revA2.py --output validation/revA2_imu_integrated/divider_consistency.json
python3 validation/revA2_imu_integrated/summarize.py
```

主板官方ERC0/0；制造脚本exit2拒绝生产Gerber/钻孔/CPL。Rev.A1哈希保持，分压一致性通过。完整baseline/final、各工具输出、分类比较与逐项位置队列均在validation/revA2_imu_integrated。

## 下一步与限制

下一项电气连接只剩MOSI。此前失败候选不能直接采用。MOSI闭合后，先单独跑官方ERC/DRC并审查剩余警告/制造门槛；不要机械重复会在0错误/0未连接时自动导出的export_fab脚本，避免未经完整门槛审核就产生制造包。

110项警告含3个连接区courtyard缺失，其余丝印/文字尚未关闭；两个Pogo接触孔及所购型号/治具资料待答复。目标板厂工艺、电芯/充电规格、核心模型、Rev.A2壳体、最终ELF和板上验证仍开放。旧STEP只对应旧散列，不是本轮装配快照。固件引脚网络未改变，本轮未改固件或重跑行为测试。
