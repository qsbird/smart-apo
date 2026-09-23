# 软件等待恢复、UART重试与LED输出（2026-09-23）

实现已通过模型与对象构建，**不是硬件Stop、实物闪光或最终固件验证**。本轮无PCB改变。

## 修复与边界

- APP_SLEEP当前只是软件等待。移除其对`board_buses_reinit_after_stop`的错误调用，避免没有进入Stop却丢失TIM2时基；真实Stop后失效保护函数保持原样，TIM2原模型仍覆盖它。
- `app_step_from_clock`在等待和转储期间也读取真实TIM2时间，避免长时间未服务32位epoch而无法识别回绕。非记录状态遇到时钟失败保留只读转储路径并锁存APP_ERROR_CLOCK；不伪造时间、不恢复记录。
- 时间已失效时，ERROR使用真实闭合输入请求只读转储，不要求无法验证的1.5s长按；其他错误仍使用长按。转储是否可完成还取决于SPI/UART时钟和设备状态。
- UART后端故障锁存后，APP现在显式重新初始化，再在下一步重试同一完整记录。保留原记录、序号与CRC，成功前不推进读取；失败可能已经发送前缀或整帧，主机仍须重同步/去重，没有ACK或持久化保证。
- `board_led_gate_set`使用PB0 BSRR和ODR读回，检查GPIO初始化、时钟及推挽输出模式。只改PB0锁存器，不能证明实际MOSFET/LED电流或光输出。
- LED模块实现原有AWA名义10Hz/50%/2s时序与取消，UW不触发闪光。写入/配置失败锁存，停止请求并尽力写低；硬件写入失效时可能保持高，不能声称物理关断成功。需显式`led_init`恢复。`APP_ERROR_LED`可查询并粘滞，不改变APO2/UART样本格式；LED失效不自动丢弃传感器记录。
- 闪光依赖`led_poll`调用节拍，没有硬件PWM；迟到/阻塞可能延长物理脉冲，必须实测调度/波形。咬钩检测器仍未实现，不能把输出驱动当检测成功。

## 真实回归证据

先加状态模型复现再修复：`regression_before.log`在四小时软件等待缺少时基服务的断言失败；`uart_regression_before.log`在模拟真实TX故障锁存后拒绝恢复的断言失败。新模型不再把Stop恢复或UART初始化写成无副作用空函数。

修复后AWA/UW均验证：四小时虚拟转储重试+四小时软件等待、跨32位回绕、等待不增加样本、正常恢复不触发Stop调用、时基故障永不恢复写日志、无需失效计时即可请求只读恢复；保留之前日志/CRC/重试断言。LED模型覆盖40个半周期、截止、回绕、取消、UW禁止闪光、ON/OFF写丢失和模式错误，并验证故障锁存与显式恢复。虚拟时间不是八小时实板运行。

主代理执行：

```sh
python3 -m unittest discover -s firmware/host/tests -p test_firmware_contract.py -k app_log_errors -v
python3 -m unittest discover -s firmware/mcu/tests -p test_gpio.py -v
python3 -m unittest discover -s firmware/mcu/tests -v
python3 -m unittest discover -s firmware/host/tests -v
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/idle_led_checkpoint/arm
```

MCU8/8、host23/23，状态机用例运行两变体；最终额外状态/LED粘滞检查也通过。两变体20个ARM ELF32 REL对象经独立标头/哈希验证，清单`validation/revA2_idle/objects.json`。`app.c`、`led.c`、`board.c`的ARM clang静态分析均无诊断。命令形式：

```sh
/opt/homebrew/opt/llvm/bin/clang --analyze --target=arm-none-eabi -mcpu=cortex-m0plus -mthumb -std=c11 -ffreestanding -I firmware/mcu/include -I firmware/mcu/runtime/include firmware/mcu/src/app.c -o validation/revA2_idle/app.plist
```

对led/board同样执行。完整日志`validation/revA2_idle/{final_mcu_tests,final_host_tests,final_state_test,final_arm_objects,led_test}.log`，各源分析日志及plist同目录。

## 剩余和文件

仍缺真实Stop/RTC补偿、最终链接/栈预算、器件/总线/ADC/时钟/电流/闪光实测；工具链安装授权待答复。板上与最终ELF成功均未声明。源文件修改为app.c、board.c的LED段、led.c及对应header；扩充app_errors/gpio模型和host双变体调用。输入备份在`validation/revA2_idle/baseline/`。无安装、提交、PCB或Rev.A1修改。
