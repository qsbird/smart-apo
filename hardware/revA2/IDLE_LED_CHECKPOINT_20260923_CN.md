# 软件等待与LED检查点（2026-09-23）

本轮修复软件SLEEP错误调用Stop恢复、等待/转储时基服务及UART锁存故障后的重初始化重试；LED PB0输出由桩替换为寄存器写入/读回，增加模块故障锁存与APP_ERROR_LED。

主代理MCU8/8、host23/23，双变体20个ARM对象检查通过；三源ARM静态分析无诊断。先失败后通过的回归、虚拟时间范围、修改文件和实际命令见 `firmware/mcu/VERIFICATION_IDLE_LED_CN.md`；证据 `validation/revA2_idle/`。

PCB文件未改，SHA256仍`11a0af492376e9f421871f7b683ed533b008d6664074b2e23b9880d0cb1a1d9f`。最近官方ERC0/0、DRC普通错误0/未连接14/警告119，本轮未重复KiCad检查来充当新证据。NOT_FAB_RELEASED。

真正低功耗Stop/RTC补偿、咬钩检测、最终ELF/栈预算和实物仍未完成。PCB14连接、制造审查、准确器件/电芯/机械资料等阻塞仍在，后续继续处理。
