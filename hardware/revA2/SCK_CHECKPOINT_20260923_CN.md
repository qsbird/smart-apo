# SCK 局部布线检查点 · 2026-09-23

本检查点已采用 stage6，主板 SHA256 `2781ac5d73608c1b7643d8bd2aab2b18c31af057f05e2919803b7fa99508f927`。保持 NOT_FAB_RELEASED。

## 改动与回退

仅采用 PCB 改动：SCK 走 B.Cu/In2.Cu/F.Cu，0.15 mm 线宽、两个 0.60/0.30 mm 过孔；In1 不增加信号。移动 C3 并重接电源、地，关联过孔和走线同步调整。重排局部 CS 并补 B.Cu 电源桥，避免 In2 分割导致供电断开。没有修改原理图、固件、网络映射或生成整板。

完整采用前副本在 `validation/revA2_sck_rework/baseline/`；采用后快照在 `final/`。stage1–5 为试验，仅 stage6 已采用。43 封装、四铜层、1 mm 厚度、12×35 mm 板框、焊盘网络及项目规则保持，详见 board_invariants.json。

## 实际验证

- `bash tools/export_fab_revA2.sh`：官方 KiCad 10.0.6 ERC 0 错误/0 警告；普通 DRC 错误 0、未连接 14→13、警告 119→120、一致性 0。退出 2，生产导出被拦截，无本轮生产文件。首次沙盒运行启动失败，随后本机权限重跑取得此结果。
- KiCad Python `tools/check_reference_revA2.py hardware/revA2/smart_apo_common_revA2.kicad_pcb --baseline validation/revA2_sck_rework/baseline/smart_apo_common_revA2.kicad_pcb --output validation/revA2_sck_rework/main_reference.json`：退出 0；先显式重新填铜，In1 地单轮廓，六条敏感网共 1374 个线心/边缘采样点完整，原有未改外层走线无新增参考缺口。仅几何证据，不代表信号完整性或电磁回流已验证。
- `python3 tools/validate_revA2.py` 与 `python3 tools/check_divider_revA2.py --output validation/revA2_sck_rework/divider_consistency.json`：报告保持未放行，跨文件分压一致性通过。
- `python3 validation/revA2_sck_rework/summarize.py`：生成逐阶段分类比较 comparison.json 与按网络、位置和 UUID 的 repair_queue.csv。

警告分类：丝印压铜 57、丝印重叠 47、丝印板边 9、文字高度 6、背面未镜像文字 1。C3 移位产生 C3/U1 参考文字与轮廓、U7 参考文字与 C3 焊盘的局部冲突；全部保持 OPEN，无豁免。不能仅凭普通错误 0 宣称 DRC 通过。

## 下一步与阻塞

剩余缺口：SDA 3、SCL 3、GND 3、3V3 1、IMU_INT 1、MISO 1、MOSI 1。先继续 Flash MISO/MOSI 局部候选及其回流检查，再处理传感器总线与 U3 逃线。每组独立副本验证后采用。

固件本轮未改、未重新运行构建；前次证据 MCU 8/8、host 23/23、20 ARM 对象不能当作最终 ELF 或板上验证。链接工具链、真实 Stop/RTC、实测、CT05 所购图纸、401020 电芯规格、U2/U3 封装资料及机械/3D 输入仍未闭合。
