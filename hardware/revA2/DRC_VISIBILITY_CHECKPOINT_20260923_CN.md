# DRC检查可见性与工程注释图层 · 2026-09-23

当前正式板SHA256 `e30fa2c0394ecc5481a546963db4facbde0a48d4c5758d725a5c8614be59d672`，NOT_FAB_RELEASED。两组都已通过官方复检并采用。

## 恢复被忽略检查

将footprint_filters_mismatch、footprint_type_mismatch、missing_courtyard、track_not_centered_on_via、tuning_profile_track_geometries从ignore改为warning。仅增强检查，没有降低任何制造下限或错误等级；项目JSON除这五项外逐字段一致。

独立官方审查新增4项：J1/J2/J3各一项missing_courtyard，MCU地线1项track_not_centered_on_via。其余三类没有报项，这只能证明本轮没有对应违规，不能代替实体封装正确性审查。

将GND线段UUID8580f8c7-952a-4f37-8ea1-68efe75bd346的尾端从(4.2,12.875)对准via(4.099999,12.875)，消除端点警告。板框/焊盘网络/四层/厚度保持，显式填铜参考增量PASS。三个连接区机械边界缺失继续OPEN：没有根据未知电池线/Pogo治具/桥接口外形猜画courtyard，也没有豁免这些warning。

采用后官方结果：普通错误0、2未连接、125警告（原122+新可见3项）。ignored_checks=[]，项目drc_exclusions=[]。完整前后副本、清单manifest、规则差异检查、官方报告和main_gate.log位于validation/revA2_ignored_rules。

## 将工程状态说明移出生产丝印

PCB上唯一长状态说明 `SMART APO Rev.A2 | PARTIAL EXPLICIT ROUTING NO GERBER` 原在B.SilkS，并非器件编号或接口标识。本轮只把它移到Dwgs.User保留为工程审查注释，内容/位置/大小不变；没有删除信息或移动器件标识。

文本差分严格断言PCB仅一行图层变化，所有铜/焊盘/器件/填铜缓存及其他文本字节一致，项目文件也逐字节一致。独立及正式官方DRC都确认：125→111警告，具体为压铜56→51、重叠50→43、字高6→5、背面未镜像1→0；板边9及missing_courtyard3不变。解除的是不应印到板上的工程说明造成的违规，不是警告豁免。证据在validation/revA2_status_annotation/invariants.json、main_gate.log、repair_queue.csv及前后副本。

## 实际命令与最终状态

每组实际运行 `bash tools/export_fab_revA2.sh`，官方KiCad10.0.6 ERC0错误/0警告；最终普通DRC错误0、2未连接、111警告、一致性0、无忽略检查及单项排除。制造导出exit2，未生成生产Gerber/钻孔/CPL。

另执行 `python3 tools/validate_revA2.py`，报告已更新，Rev.A1哈希不变。本轮未改固件，未重复其测试。过孔/Pogo清单的几何内容仍有效，但原报告散列指向注释修改前版本；未将其冒充新实物验证。

仍需完成IMU_INT和MOSI。111项警告、J1/J2/J3机械边界、Pogo所购接触头/治具资料、最终ELF/板上和壳体/3D尚未闭合。IMU完整扇出重建仍在独立副本推进，未合入未通过的候选。
