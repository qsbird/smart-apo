# 用户暂停检查点 · 2026-09-24

用户要求“先停止吧，已有进度做好记录”。开发已停止；保留cursor分支全部未提交工作，未提交、未重置、未覆盖Rev.A1。没有运行中的子代理；本次停止请求后只做状态检查和记录/快照，未继续开发或运行测试。

## 最后已验证成果

- PCB四层布线已闭合；官方ERC0错误/0警告，DRC0错误/0未连接/3项J1/J2/J3缺courtyard。全部丝印DRC清零，D1数字极性冲突已修复。
- 正式原理图已修复D1、遗留NC叉号、越页、标签/IC/阻容/连接器排版；官方网表对比保持电路。
- 工作BOM已校正C7值、C11/C12封装及完整库ID，43位号/变体一致性通过。
- 最新同版本硬件审查包：validation/revA2_review_bundle。含当前原理图/正反面装配PDF及不完整STEP；不是生产文件。
- 最后已通过的主机回归为34项（validation/revA2_csv_input/tests.log），已修复日志CRC失败覆盖输出、事件评分多对多误计、CSV非有限数/时间戳入口问题。
- 上一已验证MCU源码曾编译20个ARM目标文件；最终ELF仍缺lld和ARM builtins，未上板。

## 暂停时正在修改：UART航次头，**尚未验证**

刚修改8个文件，尚未运行任何构建/测试：

- firmware/mcu/src/datalog.c、include/datalog.h：缓存并提供原始16字节航次头。
- firmware/mcu/src/uart_dump.c、include/uart_dump.h：新增version=2、16字节payload航次头帧，v1样本保持。
- firmware/mcu/src/app.c：转储先发头，失败重试并阻止样本游标前进。
- firmware/mcu/tests/app_errors.c：新增头帧失败/重试及头读取失败模型断言，尚未执行。
- firmware/host/dump_decode.py：共用帧扫描，解析并核对航次变体/ODR/压力量程；调参默认要求头帧；新增显式--allow-headerless旧捕获兼容选项。
- firmware/host/tests/test_decode_safety.py：部分旧CLI测试增加旧捕获选项，尚未执行。

**34项通过及旧ARM对象报告不覆盖这批修改。** 当前WIP可能存在编译/行为问题，不可声明新协议已打通。还缺C打包→Python头解码、datalog历史头保持、坏CRC/冲突头/截断头/声明量程不符、CLI拒绝时不覆盖文件等专门回归；协议文档尚未更新。新静态头缓存/调用栈也未重新审计。

快照validation/revA2_paused_20260924/UART_HEADER_WIP_UNTESTED.zip保存上述8个文件；manifest.json记录哈希和已验证边界，git_status.txt保存工作区状态。正式硬件文件哈希也已记录。

## 恢复时从这里继续

1. 先阅读本记录，不要将未验证头帧WIP误认为34项通过的版本，不重新生成PCB或原理图。
2. 优先补齐并运行头帧端到端、历史日志头和重试回归；修复失败后跑host完整测试及双变体ARM对象编译，记录真实结果；更新协议/README与资源证据。
3. 继续处理真正Stop/RTC补偿、因果咬钩检测/标定参数衔接、异步重采样等尚未完成功能，不能照搬非因果离线滤波阈值。
4. 外部阻塞详见hardware/revA2/DELIVERY_GATES_CURRENT_CN.md：三处连接工艺courtyard、准确CT05/401020/MLCC/LED等资料、Pogo与板厂能力、准确3D/壳体、链接器/运行库与样机设备。

状态始终NOT_FAB_RELEASED。未生成生产Gerber/钻孔/CPL，未宣称机械干涉或硬件功能通过。
