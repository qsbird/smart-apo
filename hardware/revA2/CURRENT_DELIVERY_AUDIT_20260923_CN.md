# 当前交付证据审查 · 2026-09-23

PCB SHA256 `5d1f8a7a330c3bbbf86d8e15930d2b26694e2a207ddf2a994f410223839efa94`。本阶段PCB、原理图和固件生产代码均未改，上一阶段官方ERC0/0、DRC0错误/0未连/3项courtyard仍适用于同一板文件。NOT_FAB_RELEASED。

## 当前3D审查件

实际运行`kicad-cli pcb export step --subst-models --output validation/revA2_current_delivery_audit/revA2_CURRENT_REVIEW_ONLY_INCOMPLETE.step hardware/revA2/smart_apo_common_revA2.kicad_pcb`，exit0；STEP 1664963字节，板与STEP SHA在manifest.json。旧3D审查件对应07bc3e…板，已明确为历史，不能当当前板证据。

KiCad内置Python重新遍历43封装模型：35个模型引用可解析为现有通用STEP；J1/J2/J3/U2/U3/U5/SW1仍未绑定模型；Y1绑定路径仍无法解析，导出日志有其模型诊断。exit0不是模型齐全或碰撞通过。无Rev.A2壳体及准确实购物料外形，未运行独立3D查看器/装配碰撞检查。

## 固件最终构建实测

实际逐版本运行：

```sh
make -C firmware/mcu all CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/delivery_link_audit VARIANT=0
make -C firmware/mcu all CC=/opt/homebrew/opt/llvm/bin/clang BUILD=validation/delivery_link_audit VARIANT=1
```

两次make均exit2，最终链接失败：Clang `invalid linker name in argument '-fuse-ld=lld'`。新目录生成20个目标文件，二进制标头逐个确认ELF32 little-endian、ET_REL、EM_ARM，哈希在manifest.json；没有生成最终ELF。因此状态仍是“ARM目标文件可编译”，不能叫“最终固件构建通过”或“板上运行”。

现有LLVM bin中没有lld，lib/clang中没有ARM builtins archive；rustc及用户Rust工具链目录也不可用，没有可复用的rust-lld。链接至少仍需ARM链接器和兼容的__aeabi运行库。未安装新工具或依赖；既有授权问题未有答复。无样机，未烧录/上板。旧模型/runtime测试证据不因本次对象构建变成硬件验证。

## 产物与下一步

`validation/revA2_current_delivery_audit/`含当前STEP、当前模型清单、官方导出日志、两份实际链接日志、退出码、20对象及STEP哈希清单；对象在firmware/mcu/validation/delivery_link_audit/。更新3D_CHECK_PARKED_CN.md和MCU README状态入口。

继续可独立进行的最终BOM/装配变体/极性一致性核查。缺失的具体输入仍为连接工艺courtyard及Pogo尺寸/定位公差、CT05所购图纸、401020允许充电电流、核心采购后缀/MLCC有效容量、Rev.A2壳体/模型、最终链接工具与板上设备。没有生产Gerber导出或FAB_RELEASED声明。
