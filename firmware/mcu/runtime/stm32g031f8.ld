/* STM32G031F8: ST DS12992 Rev 4 and CMSIS stm32g031xx.h.
 * Review-only until linked and tested. No heap; reserve 2 KiB for stack.
 */
ENTRY(Reset_Handler)
MEMORY {
    FLASH (rx) : ORIGIN = 0x08000000, LENGTH = 64K
    RAM (rwx) : ORIGIN = 0x20000000, LENGTH = 8K
}
_estack = ORIGIN(RAM) + LENGTH(RAM);
SECTIONS {
    .isr_vector : { KEEP(*(.isr_vector)) } > FLASH
    .text : { *(.text*) *(.rodata*) . = ALIGN(4); } > FLASH
    .ARM.extab : { *(.ARM.extab*) } > FLASH
    .ARM.exidx : { *(.ARM.exidx*) } > FLASH
    .data : {
        . = ALIGN(4); _sdata = .;
        *(.data*)
        . = ALIGN(4); _edata = .;
    } > RAM AT > FLASH
    _sidata = LOADADDR(.data);
    .bss (NOLOAD) : {
        . = ALIGN(4); _sbss = .;
        *(.bss*) *(COMMON)
        . = ALIGN(8); _ebss = .;
    } > RAM
    ASSERT(_ebss <= _estack - 2048, "RAM leaves less than 2 KiB stack")
    ASSERT(SIZEOF(.isr_vector) == 188, "STM32G031 vector table must have 47 entries")
}
