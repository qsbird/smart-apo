# 智能阿波共板 Rev.A2 工作区

此目录是从 Rev.A1 独立建立的生产候选工作区。任何 Rev.A2 生成或审查操作都不得写入上级目录中的 `*revA1*` 文件。

## 当前状态

- Rev.A1 基线 SHA-256 已记录在 `revA1_baseline_sha256.json`。
- `smart_apo_revA2.kicad_sym` 使用逐脚电气类型，不再把核心 IC 的所有引脚定义为 Passive。
- `smart_apo_common_revA2.kicad_sch` 是独立原理图；当前先完成符号电气类型修复，电路改动需在官方 ERC 与逐脚审查后进行。
- `SmartApoRevA2.pretty` 是项目级封装库目录。
- `BOM_revA2_WORKING.csv` 与 `ASSEMBLY_VARIANTS_revA2.csv` 保留双装配版本；前者仍是工作 BOM，不是最终下单 BOM。
- `CPL_revA1_REFERENCE_ONLY.csv` 只用于查看旧布局，严禁作为 Rev.A2 贴片坐标文件。
- 上级 `hardware/smart_apo_common_revA2_NETS_PLACED.kicad_pcb` 是早期文本生成、0 走线的参考板，不属于本工作区的生产候选 PCB；不得用它替代从审核后原理图重新建立的 PCB。
- 已使用 KiCad 10.0.6 官方 ERC：0 错误、0 警告。
- LPS28DFW footprint 已按 ST 官方 STEVAL-MKI225A 铜层/阻焊/钢网 Gerber 重建，并对照 DS13317 Rev 1 确认 Pin 1 与 PAD2LID。
- STM32G031F8P6 已按 DS12992 Rev 4 的真实 TSSOP20 物理脚顺序重建；Rev.A1 中错误的物理脚编号没有沿用。
- W25Q256 `/CS` 已增加 R12 10 kΩ 上电上拉。
- KiCad 官方网表已导出：43 个器件、33 个已连接网络、9 个明确未连接引脚。
- 电池焊盘、7 针 Pogo 和 6 线桥接口已迁入项目级 `.pretty`；IMU、Flash 和磁簧开关已改用 KiCad 10 中可解析的封装链接。

## 放行原则

只有在从原理图更新 PCB、完成布线、官方 DRC 为零错误、独立查看 Gerber/钻孔并重新导出 BOM/CPL 后，才可把状态改为 `FAB_RELEASED`。
