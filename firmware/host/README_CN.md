# 离线闭环调参工具

输入是阿波与智能水中的两个 CSV。下水前和回收后分别做三次同步敲击，脚本用六个冲击拟合时间偏移与晶振漂移；水中张力生成教师标签，阿波 IMU/压力生成学生特征，并按连续时间切为 60%/20%/20% 三段。

```bash
python generate_synthetic_dataset.py
python autotune.py example_data/awa.csv example_data/underwater.csv -o example_result.json
```

输出参数只作为候选版本。必须在下一次、完全未参与寻参的独立航次通过门限后，才允许写入设备；本工具有意不实现自动刷机，避免同一数据集上的过拟合参数被直接投入使用。

CSV 必填列：`timestamp_us, ax, ay, az, gx, gy, gz, pressure`；水中端另加 `tension_gf`。时间戳必须单调递增，单位为微秒。
