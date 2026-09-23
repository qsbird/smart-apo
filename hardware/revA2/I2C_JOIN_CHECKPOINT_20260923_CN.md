# I²C 主干接入检查点 · 2026-09-23

两组分别采用并重跑主板官方门禁。最终主板SHA256 `44c9a8afb8d6c7fef85bdf2b07ae659e7b21f979601d429aa3fc47430cfca52a`，NOT_FAB_RELEASED。

## 改动

SCL组：via从(8.2,3.3)移至(8.3,3.6)，相关F/In2线端同步；R2从F(8.5,8.4)移至(9,8.4)，两端走线同步；新增via(7.825,8.4)，B路径(8.3,3.6)→(8.3,8.4)→(7.825,8.4)，F接R2。独立实际铜连通图确认U2.13/U3.3/U1.20/R2.1/U4.13均已连通，R2.2保持3V3。

SDA组：via(1.9,1.1)，F接原上部SDA，In2经(1.9,8.2)接已有via(3.3,9.6)，0.15mm线、0.60/0.30mmvia。新增GND via(2.8,0.75)，距离SDA换层via约0.966mm，并核验接入多个地铜层。U2.14/U3.1/U1.1/R1.1实际连通，ADC U4.14尚未接入。

只采用PCB铜与R2位置变更；未重生成整板，未改Rev.A1、原理图、封装库或制造规则。43封装、12×35mm、四层1mm、焊盘网络保持；固件本轮未改。

## 实际工具结果

| 正式检查点 | 普通DRC错误 | 未连接 | 警告 | 一致性 |
|---|---:|---:|---:|---:|
| 原基线 | 0 | 5 | 120 | 0 |
| SCL采用后 | 0 | 4 | 122 | 0 |
| SDA采用后 | 0 | 3 | 122 | 0 |

每组均实际运行 `bash tools/export_fab_revA2.sh`：KiCad10.0.6 ERC0错误/0警告；DRC如上，制造导出exit2拒绝Gerber/钻孔/CPL。`python3 tools/validate_revA2.py`确认Rev.A1哈希未变；`python3 tools/check_divider_revA2.py --output validation/revA2_sda_join/divider_consistency.json`通过跨文件一致性。

两组各有完整baseline/final、官方报告、main_gate.log、board_invariants.json、comparison.json、repair_queue.csv，目录分别为validation/revA2_scl_join和validation/revA2_sda_join。分类/位置清单由各自summarize.py实际生成。SDA独立探索证据另在validation/revA2_sda_analysis；原探索未带项目库产生7项lib_footprint_issues，最终版本带完整项目库重新验证，没有将缺库结果当正式证据。

SDA stage2的首个接地via(.9,.85)碰斜切板边且悬空，官方检出1项copper_edge_clearance与via_dangling；拒绝后stage3移至合法位置。stage1无该地孔的版本0错误/3未连接，stage3补地孔后同为0/3，没有新增悬空。

## 参考与机械余量边界

用KiCad内置Python显式Fill后审查。SCL组通用参考检查PASS_SAMPLED_GEOMETRY_ONLY；独立新线0.025mm中心/双边采样仅同网via局部缺口，In2调整段有1点距via0.452416mm（不硬称≤0.45）。新via在R2焊盘外，铜环至pad净距0.095mm。两个SCL via对U5最大物理EP净距0.075/0.082426mm，余量较窄，必须继续在装配/机械审查中保留，不等于量产公差验证。

SDA组 `tools/check_reference_revA2.py` 主板对本组baseline退出2，保留GEOMETRY_REVIEW_REQUIRED：六敏感网无缺口、In1地单轮廓；旧SDA45个边缘采样点落入新增同网via反焊盘，最大半径0.448588451mm，实际离散边界最大0.454387288mm。独立2730点新In2采样缺口仅两端同网via内；主任务在叠加版再次运行check_combined.py确认相同连通与参考结论及地孔接层。见independent_review.md、stage3/supplement.json，不修改检查器、不将人工处置包装为无条件PASS。

以上仅为数字几何/连通证据，未验证电磁回流、I²C上升时间、贴装偏差或实物噪声。警告122均未豁免：压铜56、重叠50、板边9、字高6、背面未镜像1；R2移位增加的丝印问题仍开放。

## 剩余任务

3个实际连接缺口：ADC SDA、IMU_INT、MOSI。下一组优先ADC SDA，再处理两个控制/串行信号。还需全板回流与警告/忽略检查审查、最终制造包与独立查看器、器件/电芯资料及壳体STEP/3D。固件前次MCU8/8、host23/23、20ARM对象不是本轮新测试，也不代替最终ELF或板上验证。目标未完成。
