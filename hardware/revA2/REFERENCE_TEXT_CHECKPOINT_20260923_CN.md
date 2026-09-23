# U3/J3 位号修复 · 2026-09-23

正式板SHA256 `d5f8931ff216b24bbb2daeef932fd4b7ac9cece0f18420001f2839f8f12424be`。NOT_FAB_RELEASED。

仅改变两个Reference字段：U3移到(8.1,1.65)、旋转90°；U3/J3均采用0.8mm字高、0.12mm线宽，仍在F.SilkS可见。字节级归一化比较确认除这两个property块外，PCB文件完全一致；铜/焊盘/器件位置/填铜/规则未改。没有通过隐藏器件位号或改变DRC等级消除警告。

第一版U3位置与C4参考文字冲突，未采用；第二版改为沿空白区域竖排，官方新增warning集合为空，原text_height减少2、silk_edge_clearance减少1，110→107。一次脚本旋转API调用不兼容导致编辑未保存；核对本机pcbnew.py后改为SetTextAngleDegrees，重新执行修改和DRC，未用失败编辑后的旧板结果作为采用依据。

实际执行 `bash tools/export_fab_revA2.sh --check-only`：KiCad10.0.6 ERC0违规、普通DRC错误0、1个MOSI未连接、107警告、一致性0，无ignored/exclusions。退出2，未创建制造输出。随后 `python3 tools/validate_revA2.py` 更新报告，Rev.A1哈希保持。

baseline/candidate/candidate2/final、edit脚本、官方日志和严格字段差异证明在validation/revA2_reference_text。未执行独立视觉/印刷实物检查，不把DRC文字间距通过当实物可读性验证。

MOSI另在独立副本继续，尚未采用；需保留本次两个Reference字段再合并。其余107警告、Pogo资料、板厂能力、最终ELF/板上及机械/3D门槛仍开放，固件本轮未改未重测。
