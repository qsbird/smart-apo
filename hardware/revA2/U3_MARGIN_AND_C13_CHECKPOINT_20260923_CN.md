# U3最大本体余量与C13位号修复 · 2026-09-23

正式PCB SHA256 `a158b0fbfa25090dda8a04a93954720a54cc67311aa8b5262a38970ede806712`。官方ERC0/0，DRC普通错误0、未连接0、一致性0，95警告；无ignored/exclusions，NOT_FAB_RELEASED。

## C13位号组

C13 Reference仍为可见F.SilkS，移到(5.9,29.7)、0°，字高0.8mm、线宽0.12mm。严格property块替换证明PCB除该字段外逐字节一致，铜/焊盘/器件位置/规则无变化。消除4项丝印压铜和6项文字重叠，105→95警告，无新增项。

使用KiCad官方PDF导出F.SilkS/F.Mask/Edge.Cuts并用现有Poppler渲染前后图，局部C13可辨认且不压开窗/相邻文字。visual-verdict仅对本处变化通过（96/100，不是项目完成比例）；全板其他丝印冲突仍可见，不能当整体图面通过。环境无cairosvg，未安装依赖，改用PDF渲染。证据在validation/revA2_analog_labels，包括before/after_REVIEW.pdf、PNG、visual_verdict.json及invariants.json。

## U3余量组

U3由(6,2.4)移到(6.025,2.5)mm，12段相关铜完整同步，包括中央pad7→5与外围通道。过孔与其他器件不移动，原理图/网络保持。板内及项目库LPS28DFW_CCLGA-7L同步将完整body禁via/pour、track guard外框扩至最大2.95×2.95mm；保留0.25mm特定引线通道，未删除禁布。

最大本体到所有via铜环的理想间隙最小0.100mm，顶部两孔0.125mm（原顶部仅0.025mm）。这一几何储备不包含SMT贴装/孔/铜盘公差或压力应力，不作装配验收声明。

子任务20000点核对库与板内规则/通道一致；官方正例0错误，本体via及内部横穿线反例均触发items_not_allowed。独立候选ERC0/DRC0错误0未连；主任务整合时恢复已经采用的C13 Reference，再独立运行官方DRC、不变量、2958个实际线宽变更铜参考样点、最大本体距离、实际连接及via/pad审查，全部达到限定几何条件。最大局部同网via反焊盘缺口半径0.448692mm，无阈值放宽；六敏感网/原外层参考无新增损失。

## 实际正式检查与回退

```sh
bash tools/export_fab_revA2.sh --check-only
python3 tools/validate_revA2.py
python3 tools/check_divider_revA2.py --output validation/revA2_u3_margin_adopt/divider_consistency.json
```

采用后KiCad10.0.6官方ERC0/0、普通DRC错误0/未连接0/95警告、一致性0；仅检查exit0，fab_export仍不存在。Rev.A1哈希保持，分压一致性通过。

validation/revA2_u3_margin_candidate保存规则正反例与原候选报告；validation/revA2_u3_margin_adopt保存主任务baseline/candidate/final、官方日志、主任务几何及连接审查、warning_queue.csv。布局只采用PCB与LPS28DFW库文件，C13新位号未丢失，固件未改未重测。

## 剩余门槛

95警告：51丝印压铜、30重叠、8板边、3文字高度、3连接区courtyard缺失。Pogo两孔/接触工艺、板厂能力、所购器件/电芯/有效电容资料、当前板3D与壳体、最终ELF和板上验证仍开放。已有STEP是旧版，不能当当前干涉证据。电气闭合和局部图面通过不等于制造放行，未生成生产Gerber。

## 校验脚本修正与最终复检

KiCad保存库封装后使用多行格式，原LPS字符串匹配导致离线校验误报。`tools/validate_revA2.py`现在与已有IMU检查一样归一化空白，保留全部尺寸及禁布匹配要求。新增`tools/tests/test_validate_revA2.py`覆盖多行/单行通过、错误焊盘尺寸/放松禁布拒绝；未修改几何或放行条件。

实际命令`python3 -m unittest discover -s tools/tests -v`：9项测试通过（含5项导出拦截测试和4项几何回归）。随后重新运行官方`--check-only`：exit0，ERC0/0、DRC0错误/0未连/95警告/0一致性问题；`python3 tools/validate_revA2.py`与分压一致性命令均exit0。证据为validator_tests.log、main_checks.log、validation.log、divider.log。最终快照报告已刷新。

warning_queue.csv保留全部95项OPEN状态，新增逐项priority/next_action/dependency。下一组优先处理8项板边丝印和3项文字高度；三项缺失courtyard须基于实际连接与装配输入，不以虚构边界消警。
