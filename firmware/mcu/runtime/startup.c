/* Review-only C startup, independent implementation for STM32G031F8.
 * Vector order: ST cmsis-device-g0 startup_stm32g031xx.s (see report).
 * Reset clock configuration is retained. No HAL, C++ constructors or heap.
 * Hardware driver initialization remains in app_boot and is not complete.
 */
#include <stdint.h>
extern uint32_t _estack, _sidata, _sdata, _edata, _sbss, _ebss;
extern int main(void);
void Default_Handler(void) { for (;;) {} }
void Reset_Handler(void)
{
    volatile uint32_t *dst = &_sdata;
    const uint32_t *src = &_sidata;
    while (dst < &_edata) *dst++ = *src++;
    for (dst = &_sbss; dst < &_ebss; ++dst) *dst = 0;
    (void)main();
    Default_Handler();
}
void NMI_Handler(void) __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SVC_Handler(void) __attribute__((weak, alias("Default_Handler")));
void PendSV_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void) __attribute__((weak, alias("Default_Handler")));
void WWDG_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void PVD_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void RTC_TAMP_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void FLASH_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void RCC_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void EXTI0_1_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void EXTI2_3_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void EXTI4_15_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void DMA1_Channel1_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void DMA1_Channel2_3_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void DMA1_Ch4_5_DMAMUX1_OVR_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void ADC1_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void TIM1_BRK_UP_TRG_COM_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void TIM1_CC_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void TIM2_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void TIM3_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void LPTIM1_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void LPTIM2_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void TIM14_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void TIM16_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void TIM17_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void I2C1_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void I2C2_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void SPI1_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void SPI2_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void USART1_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void USART2_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void LPUART1_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
__attribute__((section(".isr_vector"), used, aligned(256)))
const uintptr_t vectors[] = {
    (uintptr_t)&_estack, (uintptr_t)Reset_Handler,
    (uintptr_t)NMI_Handler,
    (uintptr_t)HardFault_Handler,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    (uintptr_t)SVC_Handler,
    0,
    0,
    (uintptr_t)PendSV_Handler,
    (uintptr_t)SysTick_Handler,
    (uintptr_t)WWDG_IRQHandler,
    (uintptr_t)PVD_IRQHandler,
    (uintptr_t)RTC_TAMP_IRQHandler,
    (uintptr_t)FLASH_IRQHandler,
    (uintptr_t)RCC_IRQHandler,
    (uintptr_t)EXTI0_1_IRQHandler,
    (uintptr_t)EXTI2_3_IRQHandler,
    (uintptr_t)EXTI4_15_IRQHandler,
    0,
    (uintptr_t)DMA1_Channel1_IRQHandler,
    (uintptr_t)DMA1_Channel2_3_IRQHandler,
    (uintptr_t)DMA1_Ch4_5_DMAMUX1_OVR_IRQHandler,
    (uintptr_t)ADC1_IRQHandler,
    (uintptr_t)TIM1_BRK_UP_TRG_COM_IRQHandler,
    (uintptr_t)TIM1_CC_IRQHandler,
    (uintptr_t)TIM2_IRQHandler,
    (uintptr_t)TIM3_IRQHandler,
    (uintptr_t)LPTIM1_IRQHandler,
    (uintptr_t)LPTIM2_IRQHandler,
    (uintptr_t)TIM14_IRQHandler,
    0,
    (uintptr_t)TIM16_IRQHandler,
    (uintptr_t)TIM17_IRQHandler,
    (uintptr_t)I2C1_IRQHandler,
    (uintptr_t)I2C2_IRQHandler,
    (uintptr_t)SPI1_IRQHandler,
    (uintptr_t)SPI2_IRQHandler,
    (uintptr_t)USART1_IRQHandler,
    (uintptr_t)USART2_IRQHandler,
    (uintptr_t)LPUART1_IRQHandler,
    0,
};
_Static_assert(sizeof(vectors) == 188, "STM32G031 has 47 vector entries");
