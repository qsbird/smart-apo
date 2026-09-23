# 调参事件评分修复 · 2026-09-23

修复event_metrics的多对多计分偏差。旧实现把每个重叠真值都计为TP，并把任何重叠预测都排除出FP，导致一个长报警覆盖两次事件、或一次事件被分裂成两次报警时均可能F1=1。已用原autotune.py函数AST执行复现，old_scoring_reproduction.json保留结果；这段复现未执行SciPy滤波。

新增纯标准库event_metrics.py：对有序、不相交的半开事件区间作最大一对一重叠匹配，每个真值和预测最多用一次。未匹配真值计FN，未匹配预测计FP；保留原指标字段，新增matched_events/missed_events/false_events以及matching_method=one_to_one_overlap_v2。拒绝非有限/非正时长和长度不一致输入。autotune.py实际导入该函数，候选搜索与test评分共用。

## 实际检查

- `python3 -m unittest discover -s firmware/host/tests -p test_event_metrics.py -v`：5项通过，包括4096对六采样点二值序列与穷举最大一对一匹配对照、长报警/重复报警反例、边界相邻不重叠、错误输入拒绝。最初red.log仅记录新模块尚未创建导致的导入失败，不作为旧计分行为证据；旧行为以old_scoring_reproduction.json为准。
- `python3 -m unittest discover -s firmware/host/tests -v`：28项通过，协议/固件模型原23项仍通过。
- 使用已有Codex Python运行`validation/revA2_event_metrics/search_integration.py`：实际autotune.py的tune/debounce函数在合成特征上运行，2个真值/1个持续报警只匹配1次，recall0.5、F1=2/3。确认实际导入绑定。已有NumPy2.3.5，无依赖安装。

当前系统Python无NumPy/SciPy，已有Codex Python有NumPy但无SciPy。因此未运行完整CSV→滤波→对时→搜索管线；不能声称完整自动标定通过。现有example_result.json是旧评分结果，未经新版重算，不作为新版质量证据。

修改：firmware/host/autotune.py、event_metrics.py、tests/test_event_metrics.py、README及本报告。证据validation/revA2_event_metrics含旧脚本/反例复现、5项指标测试、28项回归、合成搜索集成、源码哈希。MCU生产代码和硬件未改，未重复ARM构建或ERC/DRC。

## MCU衔接仍未完成

当前调参features使用sosfiltfilt与全航次稳健归一化，属于离线、使用未来样本的处理；不能将输出阈值直接宣称等价于实时MCU检测。真实咬钩检测器、因果特征及标定参数接口尚未实现，也没有独立实航次验证。缺测通道重采样与UART航次头仍未实现。最终ELF、Stop/RTC、实机验证及硬件放行门槛继续开放。
