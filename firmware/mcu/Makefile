# Review-only skeleton: ARM objects do not establish working hardware drivers.
# No toolchain is installed automatically. Override CC for a local ARM compiler.
ifeq ($(origin CC),default)
CC := arm-none-eabi-gcc
endif
CC ?= arm-none-eabi-gcc
BUILD ?= build-arm
VARIANT ?= 0
OUT := $(BUILD)/variant$(VARIANT)
TARGET := $(OUT)/smart_apo_revA2_skeleton.elf
SRCS := src/main.c src/board.c src/datalog.c src/sensors.c src/app.c src/uart_dump.c src/led.c src/flash.c runtime/string.c runtime/startup.c
OBJS := $(SRCS:%.c=$(OUT)/%.o)
CPUFLAGS := -mcpu=cortex-m0plus -mthumb
ifneq ($(findstring clang,$(notdir $(CC))),)
CPUFLAGS += --target=arm-none-eabi
LINKFLAGS := -fuse-ld=lld
RUNTIME_LIBS ?= -lclang_rt.builtins-arm
else
RUNTIME_LIBS ?= -lgcc
endif
CFLAGS := $(CPUFLAGS) -std=c11 -Os -g -ffreestanding -fno-builtin \
 -ffunction-sections -fdata-sections -Wall -Wextra -Werror
CPPFLAGS := -Iinclude -Iruntime/include -DSMART_APO_VARIANT=$(VARIANT)

.PHONY: all objects objects-both check-toolchain clean
all: check-toolchain $(TARGET)

objects: check-toolchain $(OBJS)

objects-both:
	$(MAKE) objects VARIANT=0
	$(MAKE) objects VARIANT=1

$(OUT)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CPPFLAGS) $(CFLAGS) -MMD -MP -c $< -o $@

$(TARGET): $(OBJS) runtime/stm32g031f8.ld
	$(CC) $(CPUFLAGS) $(LINKFLAGS) -nostdlib -Wl,--gc-sections \
	 -Wl,-Map,$(OUT)/firmware.map -T runtime/stm32g031f8.ld \
	 $(OBJS) $(RUNTIME_LIBS) -o $@

check-toolchain:
	@command -v "$(CC)" >/dev/null 2>&1 || { \
	 echo "ARM compiler unavailable: $(CC). No firmware build claimed."; exit 2; }
	@case "$(VARIANT)" in 0|1) ;; *) echo "VARIANT must be 0 (AWA) or 1 (UW)"; exit 2;; esac

clean:
	rm -rf $(OUT)

-include $(OBJS:.o=.d)
