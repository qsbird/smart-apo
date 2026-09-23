# 启动建立与LSE检查点（2026-09-23）

**NOT_FAB_RELEASED，目标未完成。** 本轮未改原理图或PCB几何；板文件SHA256仍为 `11a0af492376e9f421871f7b683ed533b008d6664074b2e23b9880d0cb1a1d9f`。最近官方ERC0/0、DRC普通错误0/未连接14/警告119沿用分压阶段报告，本轮没有把这些说成新跑结果。

## 非阻塞电池上电建立保护

`board_adc_read_vbat`在TIM2开机epoch的前100000us返回失败，不启动ADC、不改输出，也不阻塞其他采样。第一次经过门槛后锁存建立状态，后续32位自然回绕不重新等待。TIM2本身故障仍使ADC失败；它只覆盖冷启动，不能检测运行中更换电池/充电阶跃。

设计计算使用Rth最大45.677kΩ、C14名义100nF、初始容差+20%、X7R温度变化+15%（乘积上界138nF），全阶跃至半个12bit LSB约56.799ms。假定时钟快5%，100ms名义保护仍对应至少95.238ms。假设不等于实际器件资格：准确电容/时钟、偏压/漏电、上电顺序和误差仍需验证。BOM为C14增加容差≤20%的要求，生成器BOM模板同步，未执行生成器build。

实际测试覆盖门槛前一微秒/正好门槛、无转换/输出不变、成功后的计数器回绕；保留4096码换算、15类故障等旧断言。`tools/check_divider_revA2.py`新增条件计算和BOM/常量交叉检查，结果在`validation/revA2_divider/consistency.json`及本目录启动证据副本。

## LSE启动

`board_start_clocks`先初始化TIM2，再以实际TIM2名义时间限制LSE启动总预算2s。处理保护写入、ready、旁路/故障/reset状态，并恢复本次获取的DBP/PWREN；不重置备份域、不改RTC选择和drive。超时不强关LSE，避免破坏其他备份消费者。

2s是策略上限，原厂典型启动值不是最坏保证。准确Y1型号、ESR/驱动/CL与负载匹配仍未获证据；代码保留drive不能证明匹配。**LSE ready仅启动快照；TIM2仍由HSI驱动，时间戳未因此校准。** 无RTC、NVIC、Stop或实板起振声明。详情及官方来源见`firmware/mcu/VERIFICATION_LSE_CN.md`。

## 主代理实际验证

```sh
python3 -m unittest discover -s firmware/mcu/tests -p test_adc.py -v
python3 tools/check_divider_revA2.py
python3 -m unittest discover -s firmware/mcu/tests -v
python3 -m unittest discover -s firmware/host/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/startup_checkpoint/arm
```

MCU **8/8**、host **23/23**；两变体20个ELF32 ARM REL对象通过，独立检查ELF标头并存SHA256于`validation/revA2_startup/arm_objects.json`。模型含实际TIM2联动LSE、权限恢复、超时和坏状态；原TIM2测试仅补LSE隔离hooks。主日志`mcu_tests.log`、`host_tests.log`、`arm_objects.log`；LSE独立静态分析/模型证据见`firmware/mcu/validation/lse/`。没有最终ELF或板上证据，没有安装依赖。

## 发现的下一项实际问题

当前APP_SLEEP没有执行硬件Stop，但恢复时仍调用`board_buses_reinit_after_stop()`，后者使TIM2失效。需要区分软件等待与真实Stop恢复，避免软件等待后进入RECORD随即触发时钟错误；不能直接取消真实Stop的时基保护。此项下一阶段修复并加状态机回归。LED输出仍为桩，实际低功耗、RTC补偿、最终链接/栈预算和样机验证未完成。

当前固件README已按实际后端状态重新整理，原版本保存在本阶段baseline，删除了仍把UART/I²C/GPIO描述为失败桩、暗示Stop已运行的过时文字。协议文档明确LSE标志不代表时间戳校准。PCB剩余14连接、制造警告、准确CT05/电芯/封装/机械资料等阻塞不变。

主要改动：`board.c` ADC启动保护和LSE段、`board_revA2.h`启动常量/契约；ADC/LSE模型及TIM2隔离hooks；C14 BOM容差说明、生成器模板与分压校验器；固件README/ADC/LSE报告、协议时钟说明及本阶段证据。未覆盖Rev.A1、未提交或重置已有工作。
