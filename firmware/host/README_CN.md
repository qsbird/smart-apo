> 最新CSV入口校验：直接调参输入拒绝非有限值、重复/倒序时间戳及缺失/重复列；34项host回归通过，旧/新真实加载函数对照通过。完整SciPy管线仍未运行。见VERIFICATION_CSV_INPUT_CN.md。

> 最新评分修复：事件评价改为一对一重叠匹配，防止长报警/重复报警获得虚高F1；28项host回归通过，4096组序列对照及实际搜索函数合成集成通过。完整SciPy管线未运行；example_result.json为旧评分历史，不可当新版质量证据。见VERIFICATION_EVENT_METRICS_CN.md。

# 离线闭环调参工具

输入是阿波与智能水中的两个 CSV。下水前和回收后分别做三次同步敲击，脚本用六个冲击拟合时间偏移与晶振漂移；水中张力生成教师标签，阿波 IMU/压力生成学生特征，并按连续时间切为 60%/20%/20% 三段。

```bash
python generate_synthetic_dataset.py
python autotune.py example_data/awa.csv example_data/underwater.csv -o example_result.json
```

输出参数只作为候选版本。必须在下一次、完全未参与寻参的独立航次通过门限后，才允许写入设备；本工具有意不实现自动刷机，避免同一数据集上的过拟合参数被直接投入使用。

CSV 必填列：`timestamp_us, ax, ay, az, gx, gy, gz, pressure`；水中端另加 `tension_gf`。时间戳必须单调递增，单位为微秒。

回收后若从设备 UART 拉原始帧（`A5 5A` 同步），用：

```bash
python dump_decode.py capture.bin -o voyage_raw.csv
python dump_decode.py capture.bin --autotune awa -o awa.csv
python dump_decode.py capture.bin --autotune uw --tension-lsb-per-gf "$CAL_COUNTS_PER_GF" --tension-zero-counts "$CAL_ZERO_COUNTS" -o underwater.csv
```

`--autotune` 输出 `autotune.py` 所需列，但会先执行下述安全检查。加速度/角速度用 `sensors.h` 候选量程（±4 g、±500 dps）及 ST 官方敏感度 0.122 mg/LSB、17.50 mdps/LSB。压力按 DS13317：阿波 4096 LSB/hPa（Mode 1），水中 2048 LSB/hPa（Mode 2，15 m 不能用 1260 hPa 档）。raw 导出一直保留张力原始计数；UW 调参导出必须填写实际梁标定得到的 CAL_COUNTS_PER_GF 和 CAL_ZERO_COUNTS，不提供默认 gf。帧格式见 `firmware/mcu/include/uart_dump.h`。这不是自动刷机。


宿主机协议/固件模拟接口回归（无 numpy/scipy 依赖，在仓库根目录运行）：

```bash
python3 -m unittest discover -s firmware/host/tests -v
```

2026-09-23：增加显式时间展开验证，见 `firmware/host/VERIFICATION_TIME_UNWRAP_CN.md`；ARM/板上验证未完成。MCU 已实现全航次 Flash/RAM 尾转储的模拟验证，host 去除连续完全相同的重试帧；raw 原样保留计数及 flags；`--autotune` 已拒绝含缺测通道的日志，不会把未采样零值送入调参。显式重采样仍未实现。前序证据与阻塞见 `firmware/mcu/VERIFICATION_20260923_CN.md`。

## 调参导出安全门槛

- AWA 每条样本必须同时置位 IMU_OK(bit 1) 和 PRESS_OK(bit 2)，且不能携带 STRAIN_OK(bit 3)；UW 每条必须三个有效位齐全。没有有效位的数值（即使为 0）只能作为 raw 诊断数据，不能解释为物理零值。
- 任一条缺测即拒绝整次调参导出，退出 2，不创建/覆盖目标 CSV；不擅自删行、补零、插值或前值填充。当前异步 MCU 日志通常会被此门槛拒绝，直到明确实现重采样流程。
- 检查样本内部 CRC，时间戳必须严格递增，sequence 必须按模 65536 连续（允许 65535→0）；外层 CRC 丢弃中间坏帧后产生的序号缺口也拒绝调参；回绕/复位需显式重建，不能直接调参。UART 外层 CRC 仍负责帧筛选，完全相同的连续重试帧去重。
- UW 张力采用 `(raw - zero_counts) / counts_per_gf`；斜率须有限且非零（可为负以表达桥方向），零点必须显式提供且有限。ADC 内部 offset 校准不等于梁的 gf 标定。
- UART v1 尚未传送航次头。`--autotune awa|uw` 是操作者声明的装配变体，不能自动证明压力量程正确；AWA/UW 压力比例分别是 4096/2048 LSB/hPa。
- raw 导出不改变原样本，包括诊断用无效值与 flags。它使用 `*_raw` 列名，不能直接当作 autotune 输入。

## 长航次 uint32 微秒时间展开（显式选择）

默认仍拒绝时间戳回绕。uint32 微秒计数约 71.6 分钟回绕一次；只有操作者能从采集记录确认以下条件时，才可展开：单次不中断启动、没有重启/时钟复位、相邻记录实际间隔始终不超过已知上限，且该上限严格小于半周期（2147483648 us，约 35.8 分钟）。例如已确认最大相邻间隔不超过 10000 us：

```bash
python3 firmware/host/dump_decode.py capture.bin --autotune awa --unwrap-timestamps --max-sample-gap-us 10000 -o awa.csv
```

两个参数必须一起用于 `--autotune`，上限必须为 1..2147483647 的整数。此选项是对采集条件的显式声明，软件不能替操作者证明。每步按模 2^32 计算增量，重复、明显后退、增量超上限、半周期及以上歧义全部拒绝；输出从第一条原始计数开始累加为展开时间，不推断第一条之前的回绕次数。原始记录和内部 CRC 不改写，seq 模 65536 连续、CRC、变体及缺测门槛全部保留；验证失败不覆盖输出。

UART v1 缺少启动/航次标识和宽时间戳，任意长停顿（特别是整周期停顿）、恰好伪装成小正增量的复位，以及恰丢失 65536 的整数倍记录，无法仅凭这两个有限位宽计数可靠识别。来源不明确的日志应保留 raw，不应使用展开参数强行放行。连续完全相同的 UART 重试帧仍按既有规则去重；这不证明采集未重启。时间展开不是异步传感器重采样，当前存在缺测标志的 MCU 日志仍拒绝调参导出。
