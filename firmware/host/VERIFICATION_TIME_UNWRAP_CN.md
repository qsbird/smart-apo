# 长航次时间展开验证（2026-09-23）

## 改动与回退

- `dump_decode.py`：新增 opt-in 时间展开；要求明确声明单次不重启采集及最大样本间隔，保持严格序号/CRC/缺测/变体门槛。
- `tests/test_decode_safety.py`：新增 6 项自动回归测试。
- `README_CN.md`：增加使用契约及不能从 UART v1 推断的情况。
- 修改前副本：`firmware/host/checkpoints/time_unwrap_before/` 中同名三文件。未修改 MCU 或 PCB。

## 实际执行

仓库根目录执行：

```text
python3 -m unittest discover -s firmware/host/tests -v
修改前：Ran 17 tests in 11.125s / OK
修改后：Ran 23 tests in 5.630s / OK

python3 -m py_compile firmware/host/dump_decode.py firmware/host/tests/test_decode_safety.py
exit 0
```

新增测试验证：

1. `0xfffffff0 → 16 → 48` 正常展开为 `4294967280 → 4294967312 → 4294967344`，同时允许 seq `65535 → 0 → 1`，原始样本不变。
2. 重复时间、后退时间、等于/超过半周期和超过声明上限时拒绝。
3. 缺失/零/负数/半周期/非整数上限，或未选择展开却传上限时拒绝。
4. 开启展开仍拒绝内部 CRC 错误、外层 CRC 丢帧造成的序号缺口、缺测通道及变体冲突。
5. 14 条间隔 10^9 us 的模拟记录累计到 13×10^9 us，跨多次回绕正确。
6. 实际 subprocess CLI：默认拒绝回绕；缺少上限/上限过小拒绝并保留已有目标；明确上限后成功导出。

## 验证边界

这是宿主 Python 及已有 C 模拟回归证据，不是 ARM 构建或实物运行证据。没有添加依赖，也未改变传输格式。

UART v1 没有 boot ID、航次头或 64 位时钟。复位若恰好产生可接受的小正模增量、超整周期停顿或丢失 65536 倍数条记录，不能从当前载荷可靠识别。必须有外部采集记录支持不中断/间隔声明，否则只保留 raw。正常小幅后退或超上限能被拒绝，不代表任意复位已被检测。

时间展开不补缺测，不插值，不证明异步通道同时有效。异步日志重采样、校准、ARM/HAL 及板上验证继续保持开放。
