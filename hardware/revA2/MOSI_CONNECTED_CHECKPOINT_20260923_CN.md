# MOSI闭合：整板电气连接检查点 · 2026-09-23

正式PCB SHA256 `03201629fad52090db7331362f10628c5b99c38823cf2f243026d4fd582cc6e4`。

**官方ERC0违规；DRC普通错误0、未连接0、一致性0。仍105警告，无ignored_checks和单项排除。NOT_FAB_RELEASED。**

## 本轮采用改动

MOSI经Flash附近F桥、In2段及B层下方/右侧路径接入MCU；相关CS、SCL、MISO局部、电源、GND和UART_TX同步重排。封装位姿仅改Y1至(1.91,8.550001),180°；C15至(4.4,8.8),0°；C16至(1.1,10.6),180°；C3至(1.06,13.7),270°。值、焊盘网络、原理图、库及制造规则不变，U3/J3位号修复保留。

最终几何补丁校验每个待删铜的UUID/位置/层/宽度/网络及四个封装原位姿，独立重放34删除/65新增（含替换）铜对象。只有全审后的final_snapshot被主任务复制、复检并采用；早期0open但短路或失参考的try1–try9均不是最终采用依据。最终快照与可重放补丁位于validation/revA2_mosi_final_route/final_snapshot、final_geometry_patch.json、apply_replay.py；主任务副本在validation/revA2_mosi_integrated/candidate2。

try6的F地岛含C16/C3地脚，不能删除或豁免；最终通过C3旋转/位置及UART_TX局部重排形成实际地返回，零地开路。旧C16的LSE悬端也已确认无用并删除，不保留悬空敏感线尾。

## 主任务实际复检

```sh
bash tools/export_fab_revA2.sh --check-only
python3 tools/validate_revA2.py
python3 tools/check_divider_revA2.py --output validation/revA2_mosi_integrated/divider_consistency.json
```

仅检查模式本轮退出0：KiCad10.0.6 ERC/DRC电气门禁通过，但不会创建或清空制造目录。验证后fab_export仍不存在。validate始终保持NOT_FAB_RELEASED；Rev.A1哈希不变。

独立KiCad Python显式Fill复核：

- check_invariants.py：43封装、四层1mm、12×35mm、焊盘网络和项目规则保持。
- bfs.py：所有相关命名网络焊盘实际铜连通，包括MOSI、IMU、SDA/SCL、UART_TX/RX、SWCLK、NRST、DRDY、3V3和GND。
- check_new_copper.py：相对正式基线，选择同时考虑坐标、线宽、层、网络变化；按实际线宽对新/变更铜以≤0.01mm步距采样中心和两边，共23262点。1564个无In1铜样点均在同网via局部避让内，最大半径0.451330mm，小于既有0.46mm诊断阈值，未放宽。该几何检查不能代替EM/PI实测；之前已明确处置的既有局部电源转换不因本轮通过而被取消。
- tools/check_reference_revA2.py：In1仍单一地轮廓、无In1信号，六敏感网均F层零via且完整采样覆盖，未改外层铜无新增参考损失。
- 新via无实际SMT铜环重叠；全板仍有既有近焊盘铜环关系。保守包围框报告11对、精确shape报告10对，不能混用；实际孔入接触焊盘仍仅J2.5/J2.7两项，资料未闭合。

## 敏感电路与制造边界

LSE网段总长（不是单路径）：IN4.489165→4.596839mm，OUT5.862542→5.087250mm，均F层零via、参考完整；四条模拟输入网未改变，原始差分各约2.669899mm、滤波各约2.770mm。

C3是100n，C10是1µF近端输出支路；U7→C10显式F轨段图长度1.436348mm未变。C10实际MLCC型号、偏压/温度有效容量及稳压瞬态仍待验证，不能只凭标称值通过。

最大本体/EP铜环理想余量：U2最大3.1×2.6mm余0.100mm；U3最大2.95×2.95mm余0.025mm；U5最大EP3.45×4.35mm余0.075mm。后两处是既有位置，未计入贴装/钻孔/铜盘公差。U3来源DS13317 Rev1 p42已独立渲染核对，不能用名义2.8mm代替最大外形。

## 仍未放行

105项warning全部保留待审：55丝印压铜、36重叠、8板边、3文字高度、3连接区courtyard缺失；没有悬端、孔距或连通警告。逐项队列warning_queue.csv。还需Pogo接触资料、目标板厂实际工艺、所购CT05/401020/关键后缀与电容资料、当前版本3D/壳体干涉、最终BOM/CPL与独立制造查看器、最终ELF和板上验证。

没有运行无参制造导出，没有生成生产Gerber。既有STEP绑定旧散列，不是当前装配快照。固件网络定义未改变，本轮未改固件或重测行为。目标尚未完成。

主任务baseline/final、main_checks.log、board_invariants.json、reference/supplement/bfs/via_pad_audit、counts.json均在validation/revA2_mosi_integrated，足以回退及审核本次采用。
