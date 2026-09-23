# ARM资源审查：对象文件阶段 · 2026-09-23

状态：**PRELINK_RESOURCE_EVIDENCE_ONLY**。完成新的真实ARM编译和资源统计，不是最终ELF、完整栈上界或板上运行通过。生产固件源码未改，未安装依赖。

## 实际命令

```sh
make -C firmware/mcu objects-both CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/stack_audit/arm CFLAGS='-mcpu=cortex-m0plus -mthumb --target=arm-none-eabi -std=c11 -Os -g -ffreestanding -fno-builtin -ffunction-sections -fdata-sections -Wall -Wextra -Werror -fstack-usage'
python3 firmware/mcu/tests/report_arm_resources.py --build firmware/mcu/validation/stack_audit/arm --llvm-bin /opt/homebrew/opt/llvm/bin --output firmware/mcu/validation/stack_audit/resources.json
```

现有Homebrew Clang23.1.0，两个版本共20个对象，编译exit0，保留build.log、全部.o/.su、反汇编和llvm-size输出。资源脚本校验ELF32小端、ET_REL、EM_ARM，保存源文件及对象散列。另用llvm-size --format=sysv逐对象独立交叉检查.data/.bss合计，结果一致，见independent_section_crosscheck.json。

## 结果与边界

| 对象文件指标 | AWA / variant0 | UW / variant1 |
|---|---:|---:|
| 静态RAM节有效字节之和 | 714 | 705 |
| 每节另计最大对齐填充后的和 | 847 | 829 |
| 只读ALLOC节字节之和 | 9830 | 10084 |
| 编译器栈记录函数数 | 74 | 74 |
| 最大单函数栈帧 | 312 | 312 |
| 已知直接调用链最大栈帧合计 | 616 | 616 |
| 反汇编调用数/调用或跳转重定位数 | 193/193 | 205/205 |

以上是链接前统计：节可能被gc-sections删除或重排，最终固件另含运行库、填充与可能的链接器跳板。只读ALLOC和不能当最终烧录镜像大小，RAM两行不能当最终map。

最大单帧为flash_page_program312字节，其次board_i2c1_read_n288字节。最长已知路径为Reset_Handler→main→app_step_from_clock→app_step→datalog_append→datalog_flush_page→flash_page_program→flash_read→flash_cmd→board_spi1_tx→spi_transfer→spi_wait_mask。尾跳保守保留调用者帧，不把各函数栈帧简单求和作为使用量。

当前反汇编没有发现寄存器间接调用，解析到的直接调用图没有递归环；仅对本次产物成立。未知被调函数帧仍有__aeabi_lmul、__aeabi_uidiv、__aeabi_uldivmod。脚本对未知帧不计入已知小计，同时明确输出full_stack_bound_verified=false，不能把616字节当全路径上界。

runtime/stm32g031f8.ld声明8KiB RAM并保留2KiB栈；最终链接尚未完成，该ASSERT还未在最终ELF中执行。异常硬件压栈、嵌套中断、外部运行库、最终链接布局、真实启动和高水位测量均未验证。报告没有把“看起来有余量”升级为安全通过。

## 新增文件及下一步

新增tests/report_arm_resources.py及validation/stack_audit证据。本轮没有修改生产源码、没有重复既有功能测试；此前8/8 MCU、23/23 host仅为已有行为证据。

下一步在具备已授权的完整ARM链接工具链/运行库后生成ELF/map，执行链接ASSERT，再对最终ELF重新核调用图和栈，最后板上用栈填充水位与错误/转储/采样路径实测。当前无新工具链安装授权，未安装。KiCad审批服务额度问题仍独立存在，本次编译为不依赖该审批的固件工作，没有重试或绕过被拒绝的PCB操作。
