# 日志读取输出保护 · 2026-09-23

已修复datalog_dump_next在CRC失败前覆盖调用者输出的问题。旧实现先memcpy到sample再校验；新实现校验本地候选，CRC通过才复制到输出并推进游标。空指针原已有防护，本次没有新加该逻辑；新增回归锁定其不推进游标的行为。接口声明明确0/-1不改输出。

实际证据：先加测试，旧代码在`memcmp(&out,&last_good,sizeof(out))==0`断言失败（red.log）；修复后`python3 -m unittest discover -s firmware/host/tests -v`共23项通过，日志生命周期用AWA/UW两变体分别编译执行。测试保留坏记录错误、存储修复后重新开始转储、空指针拒绝后的首条序号、历史日志只读等路径。

`make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/log_read_safety/arm` exit0。20对象逐个ELF32 little-endian/ET_REL/EM_ARM检查通过，llvm-nm跨对象只有既知链接脚本符号和__aeabi运行库待解析，证据arm_verification.json。没有最终ELF、烧录或板上测试。

为核对新增临时记录的代价，使用相同Clang Cortex-M0+ -Os/-fstack-usage编译修改前后datalog.c：datalog_dump_next静态函数帧40→72字节，增加32字节；完整命令与.su在stack_delta.json及before/after_stack.su。仅为单函数帧证据，不是完整运行栈上界；旧资源审计对应修改前源码，最终链接/异常栈/实机测量仍缺。

修改文件：src/datalog.c、include/datalog.h、tests/log_lifecycle.c、firmware/host/tests/test_firmware_contract.py。证据目录validation/revA2_log_read_safety保留修改前源码、红/绿日志、ARM对象散列、栈差值和source_manifest.json。PCB/原理图未改，未重复ERC/DRC。

剩余：真正Stop/RTC补偿、咬钩检测与实机采样/Flash/转储可靠性仍未完成；最终链接缺lld/ARM builtins。不改变NOT_FAB_RELEASED状态，不将模型回归当硬件验证。
