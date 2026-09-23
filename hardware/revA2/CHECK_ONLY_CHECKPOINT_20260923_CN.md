# 官方检查与制造导出分离 · 2026-09-23

新增 `bash tools/export_fab_revA2.sh --check-only`。它执行完全相同的官方ERC、DRC及原理图一致性门禁：失败保留非零退出；通过则退出0，但在任何mkdir/rm/导出调用前结束，不创建、不清空、不改写制造目录。检查通过也输出NOT_FAB_RELEASED提醒，其含义只是该脚本没有完成其余放行门槛。

不带参数的既有行为保持：电气门禁通过后导出候选Gerber/钻孔/CPL/BOM；仍不设置FAB_RELEASED。新增--help及参数校验，未知/多余参数在调用KiCad前退出64。没有放宽原有任何拦截条件。

## 实际验证

- `bash -n tools/export_fab_revA2.sh`：通过。
- `python3 -m unittest discover -s tools/tests -p 'test_export_fab_revA2.py' -v`：5个测试方法通过，覆盖clean check-only、ERC警告拦截、DRC错误、开路、一致性问题、工具失败、无参旧行为、无效参数/帮助。测试在临时项目中使用假CLI，只验证脚本编排，不能当作PCB验证。
- `bash tools/export_fab_revA2.sh --check-only`：实际KiCad10.0.6 ERC0违规，普通DRC错误0、1未连接（MOSI）、110警告，返回2。制造目录前后均不存在，散列/存在性核查确认没有制造文件被修改。证据validation/revA2_check_only/{tests.log,official_checks.log,verification.json}。

改动：tools/export_fab_revA2.sh；新增tools/tests/test_export_fab_revA2.py。未改PCB、原理图或固件源代码，没有新依赖。

后续MOSI闭合及丝印处理阶段使用--check-only，待用户要求的警告、制造和机械门槛审核完成后再运行无参导出；不把只检查模式的exit0当作生产放行。
