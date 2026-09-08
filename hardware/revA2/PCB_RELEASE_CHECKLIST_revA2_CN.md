# Rev.A2 PCB 放行状态

更新时间：2026-09-08。未勾选项均为阻断项；全部完成前不得生成生产 Gerber。

## 已完成的数字工程准备

- [x] Rev.A1 文件 SHA-256 基线已锁定，Rev.A2 使用独立目录与文件名。
- [x] 建立项目级 `smart_apo_revA2.kicad_sym`、`sym-lib-table`、`SmartApoRevA2.pretty` 和 `fp-lib-table`。
- [x] 核心符号的引脚不再全部使用 Passive；已区分电源输入/输出、数字输入/输出、双向、三态和 NC。
- [x] 阿波/智能水中两套装配变体表已复制为 Rev.A2 工作文件。
- [x] 已记录七个核心器件的官方资料核对入口与当前结论。
- [x] 离线结构检查通过，且复核确认 Rev.A1 哈希未变化。

## 原理图与封装阻断项

- [ ] 用当前 STM32CubeMX 验证 STM32G031F8P6 TSSOP20 的所有小封装引脚复用/重映射及启动状态。
- [x] 按 ST DS12992 Rev 4 重建 STM32G031F8P6 TSSOP20 真实物理脚顺序，并按 RM0444 记录 PA9/PA10 remap 要求。
- [x] 使用 ST 官方 STEVAL-MKI225A Gerber 与 DS13317 Rev 1 重建 LPS28DFW footprint；已核对铜、阻焊、钢网、Pin 1、PAD2LID，并加入顶层走线/过孔/铜皮禁布区。
- [ ] 完成其余核心器件的原厂封装/Pin 1/采购后缀复核。
- [x] W25Q256 `/CS` 增加 R12 10 kΩ 上电上拉。
- [ ] 按实际 401020 电芯规格确认 MCP73831 约 50 mA 充电电流。
- [x] 使用 KiCad 10.0.6 官方 ERC；错误为 0，警告为 0。

## PCB、制造与实物阻断项

- [ ] 从通过 ERC 的 Rev.A2 原理图新建 12 x 35 x 1.0 mm 四层 PCB；Rev.A1 PCB及上级目录中早期 `smart_apo_common_revA2_NETS_PLACED.kicad_pcb` 均仅作布局参考。
- [ ] 完成差分桥路、LSE、电源去耦、SPI、I2C、低速信号及平面/地过孔的完整布线。
- [ ] 使用 KiCad 官方 DRC，短路、未连接、间距、线宽和板框错误为零。
- [ ] 3D Viewer 检查压力口、Pogo、电池、O 形圈和壳体干涉。
- [ ] 导出并独立查看 Gerber、钻孔；从最终 PCB 重新导出 BOM/CPL。
- [ ] 完成 15 m 等效压力、电池、盐水、梁标定和 >=5 kgf 生存等实物验证。

当前结论：`NOT_FAB_RELEASED`。
