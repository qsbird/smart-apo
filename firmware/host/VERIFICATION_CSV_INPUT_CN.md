# 调参CSV入口校验 · 2026-09-23

新增csv_input.py，由autotune.load_csv调用。拒绝缺必需列、重复表头、空/非法数字、NaN/Inf/溢出、少于两条样本以及重复/倒序时间戳；保留允许的带符号通道和非均匀递增采样，不擅自排序/插值/补零。有效数据仍由原入口转换为NumPy数组。

实际`python3 -m unittest discover -s firmware/host/tests -v`：34项通过，其中新增6项入口测试。使用已有Codex Python执行validation/revA2_csv_input/integration.py，运行实际旧/新load_csv函数：旧版接受NaN及倒序时间，新版明确拒绝，有效数组转换保持。证据tests.log、integration.json、integration.log及source_manifest.json。不依赖新安装；完整SciPy滤波/对时/调参管线仍未运行。

修改autotune.py、csv_input.py、tests/test_csv_input.py及文档。硬件与MCU未改，不重复ERC/DRC/ARM构建。校验不证明日志来源、传感器标定或真实采样时序；因果MCU检测、Stop/RTC、最终链接和实机仍未完成。
