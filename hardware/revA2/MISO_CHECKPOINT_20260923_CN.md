# MISO 局部布线检查点 · 2026-09-23

已采用 stage2，主板 SHA256 `31a658b1808dbffc5c5441038ab03170516769b16ebdc511f648336fe2c8e5b8`，NOT_FAB_RELEASED。

## 本轮改动

继 SCK 后完成 MISO：B.Cu 从 U5 pad2 经 x9.0 列下行，到(9.9,14.85)以一个0.60/0.30mm过孔转F接MCU，信号0.15mm。将上段CS公共端点x9→8.7、C14向右0.2mm且同步信号端点、GND过孔移至(11.45,13.5)，REED的In2局部绕行以避让新增MISO过孔。没有In1信号，没有更改焊盘网络/叠层/板框/项目规则，原理图与固件未改。

## 官方与独立证据

| 检查点 | 普通DRC错误 | 未连接 | 警告 | 一致性 |
|---|---:|---:|---:|---:|
| SCK后基线 | 0 | 13 | 120 | 0 |
| MISO stage1，拒绝 | 1 | 12 | 119 | 0 |
| MISO stage2，采用 | 0 | 12 | 119 | 0 |
| 主板复检 | 0 | 12 | 119 | 0 |

stage1地过孔与供电铜实际间距0.145mm，小于0.15mm；stage2修正至不违规后采用。回退副本 baseline、最终副本 final，完整分类 comparison.json、逐项网络/位置 repair_queue.csv，均在 validation/revA2_miso_rework。

实际执行命令（项目根目录）：

```sh
bash tools/export_fab_revA2.sh
python3 tools/validate_revA2.py
python3 tools/check_divider_revA2.py --output validation/revA2_miso_rework/divider_consistency.json
python3 validation/revA2_miso_rework/summarize.py
```

KiCad 10.0.6 官方 ERC0/0；导出脚本 exit2 正确拒绝生产文件。校验器确认Rev.A1哈希不变及跨文件分压一致。另以KiCad内置Python运行 check_invariants.py 与 tools/check_reference_revA2.py（主板对本组baseline、输出main_reference.json），均退出0；参考检查先显式填铜。

独立子任务只读填铜与≤0.01mm线心/边缘采样：新MISO路径仅自身via反焊盘内存在缺口（最大半径0.447466mm），In1地单轮廓。移动焊盘/相关线端、CS公共端点和REED两端均连续。详见 independent_review.md。最近GND via距MISO via2.0555mm，B层邻近In2参考与换层回流仍开放；此项几何检查不等于SI/EM/板上通过。

警告119项全部仍需处理：压铜56、重叠47、板边9、字高6、背面未镜像1。本组无新增警告，减少1项压铜；上组C3局部丝印问题仍在。

## 尚未完成与下一步

剩余12个连接缺口：MOSI1、IMU_INT1、SDA3、SCL3、GND3、3V3 1。下一组先处理MOSI，然后传感器总线；U3禁布逃线需结合现有原厂资料和开放复核，不能为了关闭DRC直接取消禁布区。继续每组独立副本和官方检查。

本轮未改固件、未重跑固件测试；前次MCU8/8、host23/23和20ARM对象仅为已有证据，最终ELF、真实Stop/RTC及板上运行仍未通过。所购CT05图纸、401020电芯/充电规格、核心封装/采购后缀、壳体STEP与3D干涉、制造独立查看器审查仍开放。工具链安装未得到新授权，未安装依赖。
