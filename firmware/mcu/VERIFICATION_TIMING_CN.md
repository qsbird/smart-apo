# Rev.A2 固件时基修复验证

状态：**native 逻辑可编译及模拟测试通过；HAL 时基未实现；ARM 启动及板上运行未验证。**

## 问题与改动

原 `main.c` 每轮无条件 `now_us += 1000`，可将 CPU 循环误认为真实毫秒；原 `sensors.c` 用 `now >= deadline` 和 `now + floor(1000000/hz)`，跨 32 位回绕失效且累积轮询/截断漂移。

改为 `board_time_us()` 明确 HAL 契约，骨架始终失败且不修改输出。`app_step_from_clock()` 在 RECORD 取时失败立即置 `APP_ERROR_CLOCK`、关 LED、禁止继续写入；已有数据仍可只读转储。`main` 不再生成伪时间。直接传入时间的 `app_step()` 保留为注入时钟测试入口。

传感器调度用四个整数相位：`phase += elapsed_us * hz`，以 1000000 为分母，无小数周期累积误差。第一次调用建立相位，后续无符号差可跨 32 位计数回绕。每次最多读各通道一次，迟到的历史槽计入饱和计数，禁止突发补造历史数据。时间差大于 INT32_MAX 判为错误并锁定；应用处理 -1 时不再把错误返回值当作有效样本。

备份位置：`validation/timing_baseline/`。只复制本子任务修改前的文件，未覆盖已有工作。APO2/34 字节样本/UART v1 格式未改。

## 实际检查

仓库根目录命令：

```sh
python3 -m unittest discover -s firmware/host/tests -v
```

- 修改前：15 项，通过（5.775 秒）。
- 修改后：17 项，通过（7.027 秒），完整输出 `validation/native_tests_timing.log`。
- 该套件对两变体所有 MCU 源文件执行 native `clang -std=c11 -Wall -Wextra -Werror -fsyntax-only`。
- 新 `tests/sensors_timing.c` 两变体各模拟 3 小时、1 ms 步进，包含重复同一时间的额外调用：IMU 104/208 Hz、压力 50/100 Hz、张力 320 Hz、电池 1 Hz 总数均严格等于秒数×频率+初始一次；所有未过载计数为零。起点设在 UINT32_MAX 附近，覆盖多次回绕。
- 1 秒调度停顿：各通道只读一次，跳槽计数正确；恢复保持相位且不突发补发。后退时间与 0x80000000 歧义间隔拒绝采样并锁定错误。
- 时基骨架失败不改变输出值；应用时基失败不调用采样、无记录增加；错误后只能只读转储。传感器错误返回不被追加为记录。

## 改动文件

- `src/main.c`, `src/board.c`, `include/board_revA2.h`：时基契约和实际入口。
- `src/app.c`, `include/app.h`：失败闭合、时钟错误位。
- `src/sensors.c`, `include/sensors.h`：回绕、相位、过载诊断。
- `tests/app_errors.c`, 新 `tests/sensors_timing.c`；`firmware/host/tests/test_firmware_contract.py`：回归证据。
- `README_CN.md`、本报告、native 日志及修改前备份。

## 未关闭条件

1. 无真实 HAL 时基；未指定未经确认的 MCU 定时器。必须根据芯片资源/时钟树提供可靠微秒计时、溢出处理、Stop 连续性与故障报告。
2. 仅凭 32 位计数不能辨认任意长停顿或硬件冻结；调用间隔须 ≤ INT32_MAX us，HAL 必须报告停转/重置，不能根据循环数判断物理时长。
3. 跳槽计数是 RAM 诊断，未持久化到 v1 记录；不代表传感器实际丢样数。IMU/压力真实 DRDY/FIFO 与 I²C/Flash 最坏阻塞时间仍需上板测量。
4. 主机 `dump_decode.py` 当前主动拒绝 timestamp 回绕以免错误 autotune，约 71.6 分钟以上记录需显式重建时间；本任务未修改主机解码实现。
5. 未运行 ARM 构建、未烧录、未验证实际频率/抖动/功耗；无新增依赖。
