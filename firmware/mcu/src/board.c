#include "board_revA2.h"

/* GPIO register hooks are only overridden by the host state model. */
#ifndef BOARD_GPIO_READ
#define BOARD_GPIO_READ(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define BOARD_GPIO_WRITE(a, v) (*(volatile uint32_t *)(uintptr_t)(a) = (v))
#endif
#ifndef BOARD_GPIO_TIME
#define BOARD_GPIO_TIME board_time_us
#endif
#define GPIO_A 0x50000000u
#define GPIO_B 0x50000400u
#define GPIO_SYSCFG 0x40010000u
#define GPIO_REMAP (SMART_APO_SYSCFG_PA11_RMP | SMART_APO_SYSCFG_PA12_RMP)
#define GPIO_REED (1u << 9)
#define GPIO_INPUT_MODES (3u | (3u << 18) | (3u << 20))
static int gpio_ready, reed_edges_ready, reed_tracking;
static uint32_t reed_started, reed_last;

static void gpio_modify(uint32_t a, uint32_t mask, uint32_t value)
{
    BOARD_GPIO_WRITE(a, (BOARD_GPIO_READ(a) & ~mask) | value);
}

void board_enable_syscfg(void)
{
    gpio_modify(RCC_APBENR2_G0, 0u, 1u);
    (void)BOARD_GPIO_READ(RCC_APBENR2_G0);
}

void board_apply_pa9_pa10_remap(void)
{
    if ((BOARD_GPIO_READ(RCC_APBENR2_G0) & 1u) == 0u) return;
    gpio_modify(GPIO_SYSCFG, 0u, GPIO_REMAP);
    (void)BOARD_GPIO_READ(GPIO_SYSCFG);
}

static int gpio_inputs_valid(void)
{
    return gpio_ready &&
        (BOARD_GPIO_READ(RCC_IOPENR_G0) & 3u) == 3u &&
        (BOARD_GPIO_READ(RCC_APBENR2_G0) & 1u) != 0u &&
        (BOARD_GPIO_READ(GPIO_SYSCFG) & GPIO_REMAP) == GPIO_REMAP &&
        (BOARD_GPIO_READ(GPIO_A) & GPIO_INPUT_MODES) == 0u &&
        (BOARD_GPIO_READ(GPIO_A + 12u) & GPIO_INPUT_MODES) == 0u;
}

/* TIM2 belongs exclusively to this timebase. Register layout/bit positions:
 * ST stm32g031xx.h; see VERIFICATION_TIM2_CN.md for source links and limits.
 * The reset clock tree is validated, never silently assumed or changed.
 * BOARD_TIME_REG is overridden only by the register-model unit test.
 */
#ifndef BOARD_TIME_REG
#define BOARD_TIME_REG(address) (*(volatile uint32_t *)(uintptr_t)(address))
#endif
#define TIME_RCC_CR       BOARD_TIME_REG(0x40021000u)
#define TIME_RCC_ICSCR    BOARD_TIME_REG(0x40021004u)
#define TIME_RCC_CFGR     BOARD_TIME_REG(0x40021008u)
#define TIME_RCC_RESET    BOARD_TIME_REG(0x4002102Cu)
#define TIME_RCC_ENABLE   BOARD_TIME_REG(RCC_APBENR1_G0)
#define TIME_RCC_SLEEP    BOARD_TIME_REG(0x4002104Cu)
#define TIME_TIM_CR1      BOARD_TIME_REG(0x40000000u)
#define TIME_TIM_SMCR     BOARD_TIME_REG(0x40000008u)
#define TIME_TIM_DIER     BOARD_TIME_REG(0x4000000Cu)
#define TIME_TIM_SR       BOARD_TIME_REG(0x40000010u)
#define TIME_TIM_EGR      BOARD_TIME_REG(0x40000014u)
#define TIME_TIM_CNT      BOARD_TIME_REG(0x40000024u)
#define TIME_TIM_PSC      BOARD_TIME_REG(0x40000028u)
#define TIME_TIM_ARR      BOARD_TIME_REG(0x4000002Cu)
#define TIME_POLL_MAX     4096u
static int time_ready, time_attempted;
static uint32_t time_trim, time_last;

static int time_clock_valid(void)
{
    /* HSION + HSIRDY, HSIDIV=/1; SW/SWS=HSISYS; HPRE=PPRE=/1.
     * Thus nominal SYSCLK=HCLK=PCLK=TIM2CLK=16 MHz. */
    return (TIME_RCC_CR & 0x00003D00u) == 0x00000500u &&
           (TIME_RCC_CFGR & 0x00007F3Fu) == 0u;
}

static int time_config_valid(void)
{
    return time_clock_valid() && TIME_RCC_ICSCR == time_trim &&
           (TIME_RCC_ENABLE & 1u) != 0u && (TIME_RCC_RESET & 1u) == 0u &&
           (TIME_RCC_SLEEP & 1u) != 0u && TIME_TIM_CR1 == 1u &&
           TIME_TIM_SMCR == 0u && TIME_TIM_DIER == 0u &&
           TIME_TIM_PSC == 15u && TIME_TIM_ARR == UINT32_MAX;
}

static void time_start(void)
{
    unsigned i;
    uint32_t first;
    /* Re-entry may not reset an existing epoch or clear a latched fault. */
    if (time_attempted) return;
    time_attempted = 1;
    if (!time_clock_valid()) return;
    time_trim = TIME_RCC_ICSCR;
    TIME_RCC_ENABLE |= 1u;
    (void)TIME_RCC_ENABLE; /* Peripheral clock enable readback delay. */
    TIME_RCC_SLEEP |= 1u;
    TIME_RCC_RESET |= 1u;
    TIME_RCC_RESET &= ~1u;
    TIME_TIM_CR1 = 0u;
    TIME_TIM_SMCR = 0u;
    TIME_TIM_DIER = 0u;
    TIME_TIM_PSC = 15u;
    TIME_TIM_ARR = UINT32_MAX;
    TIME_TIM_EGR = 1u; /* UG loads buffered PSC and resets prescaler. */
    TIME_TIM_SR = 0u;
    TIME_TIM_CNT = 0u;
    TIME_TIM_CR1 = 1u; /* CEN, upcount, internal clock, no IRQ/DMA. */
    first = TIME_TIM_CNT;
    for (i = 0; i < TIME_POLL_MAX; ++i) {
        time_last = TIME_TIM_CNT;
        if (time_last != first) {
            time_ready = time_config_valid();
            return;
        }
    }
}

/* LSE hooks are overridden only by host register models. */
#ifndef BOARD_LSE_READ
#define BOARD_LSE_READ(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define BOARD_LSE_WRITE(a, v) (*(volatile uint32_t *)(uintptr_t)(a) = (v))
#endif
#define LSE_BDCR 0x4002105Cu
#define LSE_PWR_CR1 0x40007000u
#define LSE_PWREN (1u << 28)
#define LSE_DBP (1u << 8)
#define LSE_ON 1u
#define LSE_RDY 2u
#define LSE_UNSAFE ((1u << 2) | (1u << 6) | (1u << 16))

static int lse_start(void)
{
    uint32_t started, now, bdcr, power, dbp;
    int ok = 0;
    /* Even a ready oscillator cannot disguise an invalid timestamp clock. */
    if (board_time_us(&started) != 0) return 0;
    bdcr = BOARD_LSE_READ(LSE_BDCR);
    /* Never repair bypass, CSS failure, or a held backup reset here. */
    if (bdcr & LSE_UNSAFE) return 0;
    if ((bdcr & (LSE_ON | LSE_RDY)) == (LSE_ON | LSE_RDY)) return 1;
    if ((bdcr & (LSE_ON | LSE_RDY)) == LSE_RDY) return 0;
    power = BOARD_LSE_READ(RCC_APBENR1_G0) & LSE_PWREN;
    BOARD_LSE_WRITE(RCC_APBENR1_G0,
                    BOARD_LSE_READ(RCC_APBENR1_G0) | LSE_PWREN);
    if (!(BOARD_LSE_READ(RCC_APBENR1_G0) & LSE_PWREN)) return 0;
    dbp = BOARD_LSE_READ(LSE_PWR_CR1) & LSE_DBP;
    BOARD_LSE_WRITE(LSE_PWR_CR1, BOARD_LSE_READ(LSE_PWR_CR1) | LSE_DBP);
    while (!(BOARD_LSE_READ(LSE_PWR_CR1) & LSE_DBP)) {
        if (board_time_us(&now) != 0 ||
            now - started >= LSE_STARTUP_TIMEOUT_US) goto restore;
    }
    bdcr = BOARD_LSE_READ(LSE_BDCR);
    if (bdcr & LSE_UNSAFE) goto restore;
    /* Preserve drive strength: exact crystal/drive qualification is pending.
     * Do not reset the backup domain or alter RTCSEL, RTCEN, CSS or LSCO. */
    BOARD_LSE_WRITE(LSE_BDCR, bdcr | LSE_ON);
    for (;;) {
        if (board_time_us(&now) != 0 ||
            now - started >= LSE_STARTUP_TIMEOUT_US) break;
        bdcr = BOARD_LSE_READ(LSE_BDCR);
        if ((bdcr & LSE_UNSAFE) || !(bdcr & LSE_ON)) break;
        if (bdcr & LSE_RDY) { ok = 1; break; }
    }
restore:
    /* Leave LSE running even on timeout; another backup consumer may use it.
     * Restore only access bits we acquired, preserving unrelated state. */
    if (!dbp) {
        BOARD_LSE_WRITE(LSE_PWR_CR1, BOARD_LSE_READ(LSE_PWR_CR1) & ~LSE_DBP);
        if (BOARD_LSE_READ(LSE_PWR_CR1) & LSE_DBP) ok = 0;
    }
    if (!power) {
        BOARD_LSE_WRITE(RCC_APBENR1_G0,
                        BOARD_LSE_READ(RCC_APBENR1_G0) & ~LSE_PWREN);
        if (BOARD_LSE_READ(RCC_APBENR1_G0) & LSE_PWREN) ok = 0;
    }
    return ok;
}

int board_start_clocks(void)
{
    time_start();
    return lse_start();
}

int board_time_us(uint32_t *now_us)
{
    unsigned i;
    uint32_t first, current;
    if (now_us == 0 || !time_ready) return -1;
    if (!time_config_valid()) goto fault;
    first = TIME_TIM_CNT;
    /* Require observed hardware progress, not a CPU-loop timestamp. The
     * bounded poll is a fault timeout, not a calibrated physical duration. */
    for (i = 0; i < TIME_POLL_MAX; ++i) {
        current = TIME_TIM_CNT;
        if (current != first) {
            if (!time_config_valid() || current - time_last > INT32_MAX)
                goto fault;
            time_last = current;
            *now_us = current; /* Atomic aligned 32-bit CNT read; native wrap. */
            return 0;
        }
    }
fault:
    time_ready = 0;
    return -1;
}

void board_init_gpio(void)
{
    gpio_ready = reed_edges_ready = reed_tracking = 0;
    gpio_modify(RCC_IOPENR_G0, 0u, RCC_GPIOAEN | RCC_GPIOBEN);
    if ((BOARD_GPIO_READ(RCC_IOPENR_G0) & 3u) != 3u) return;
    /* Preload output latches before selecting output mode: CS high, LED off. */
    BOARD_GPIO_WRITE(GPIO_A + 24u, 1u << 4);
    BOARD_GPIO_WRITE(GPIO_B + 24u, 1u << 16);
    gpio_modify(GPIO_A + 4u, 1u << 4, 0u);
    gpio_modify(GPIO_A + 8u, 3u << 8, 0u);
    gpio_modify(GPIO_A + 12u, 3u << 8, 0u);
    gpio_modify(GPIO_A, 3u << 8, 1u << 8);
    gpio_modify(GPIO_B + 4u, 1u, 0u);
    gpio_modify(GPIO_B + 8u, 3u, 0u);
    gpio_modify(GPIO_B + 12u, 3u, 0u);
    gpio_modify(GPIO_B, 3u, 1u);
    if ((BOARD_GPIO_READ(RCC_APBENR2_G0) & 1u) == 0u ||
        (BOARD_GPIO_READ(GPIO_SYSCFG) & GPIO_REMAP) != GPIO_REMAP) return;
    /* External reed pull-up; sensor interrupt pins are externally driven. */
    gpio_modify(GPIO_A + 12u, GPIO_INPUT_MODES, 0u);
    gpio_modify(GPIO_A, GPIO_INPUT_MODES, 0u);
    gpio_ready = 1;
    gpio_ready = gpio_inputs_valid();
}

int board_led_gate_set(int on)
{
    if (!gpio_ready || !(BOARD_GPIO_READ(RCC_IOPENR_G0) & RCC_GPIOBEN)) return -1;
    if ((BOARD_GPIO_READ(GPIO_B) & 3u) != 1u ||
        (BOARD_GPIO_READ(GPIO_B + 4u) & 1u)) {
        BOARD_GPIO_WRITE(GPIO_B + 24u, 1u << 16); /* safe latch for later restore */
        return -1;
    }
    BOARD_GPIO_WRITE(GPIO_B + 24u, on ? 1u : 1u << 16);
    return ((BOARD_GPIO_READ(GPIO_B + 20u) & 1u) != 0u) == (on != 0) ? 0 : -1;
}

void board_reed_exti_setup(void)
{
    reed_edges_ready = reed_tracking = 0;
    if (!gpio_inputs_valid()) return;
    /* EXTI9 is an edge latch polled by software, never an IRQ/Stop wake. */
    gpio_modify(EXTI_BASE_G0 + EXTI_IMR1_OFF, GPIO_REED, 0u);
    gpio_modify(EXTI_BASE_G0 + 0x84u, GPIO_REED, 0u);
    gpio_modify(EXTI_BASE_G0 + EXTI_EXTICR3_OFF, 7u << 8, 0u);
    gpio_modify(EXTI_BASE_G0 + EXTI_FTSR1_OFF, GPIO_REED, 0u);
    gpio_modify(EXTI_BASE_G0 + EXTI_RTSR1_OFF, 0u, GPIO_REED);
    BOARD_GPIO_WRITE(EXTI_BASE_G0 + EXTI_RPR1_OFF, GPIO_REED);
    BOARD_GPIO_WRITE(EXTI_BASE_G0 + EXTI_FPR1_OFF, GPIO_REED);
    reed_edges_ready = 1;
}

void board_imu_int_exti_setup(void)
{
    /* Compatibility entry point: PA0 is polled from IDR, no EXTI/NVIC setup. */
}

int board_imu_int_pending(void)
{
    return gpio_inputs_valid() && (BOARD_GPIO_READ(GPIO_A + 16u) & 1u) != 0u;
}

void board_buses_reinit_after_stop(void)
{
    /* TIM2 stops in Stop mode; without RTC compensation the epoch is lost. */
    time_ready = 0;
    /* Stop-1 wake: HSI is back. RCC enable bits are retained, but a mid-byte
     * SPI/I2C transfer is invalid. Re-run init: CS high before SPE, then I2C
     * (includes SCL recover if SDA is stuck). Do not clear PA11_RMP/PA12_RMP.
     * Do not disable SWD on PA13/PA14.
     */
    board_spi1_init();
    board_i2c1_init();
}

int board_reed_is_closed(void)
{
    int closed = gpio_inputs_valid() &&
        (BOARD_GPIO_READ(GPIO_A + 16u) & GPIO_REED) == 0u;
    if (!closed) reed_tracking = 0;
    return closed;
}

int board_reed_held_for_sleep(void)
{
    uint32_t now;
    if (!board_reed_is_closed() || !reed_edges_ready ||
        (BOARD_GPIO_READ(EXTI_BASE_G0 + EXTI_EXTICR3_OFF) & (7u << 8)) != 0u ||
        (BOARD_GPIO_READ(EXTI_BASE_G0 + EXTI_RTSR1_OFF) & GPIO_REED) == 0u ||
        (BOARD_GPIO_READ(EXTI_BASE_G0 + EXTI_IMR1_OFF) & GPIO_REED) != 0u ||
        (BOARD_GPIO_READ(EXTI_BASE_G0 + 0x84u) & GPIO_REED) != 0u ||
        BOARD_GPIO_TIME(&now) != 0) {
        reed_tracking = 0;
        return 0;
    }
    if (BOARD_GPIO_READ(EXTI_BASE_G0 + EXTI_RPR1_OFF) & GPIO_REED) {
        BOARD_GPIO_WRITE(EXTI_BASE_G0 + EXTI_RPR1_OFF, GPIO_REED);
        reed_tracking = 0; /* Even an open-close entirely between polls counts. */
        return 0; /* Start a fresh timestamp on the next closed observation. */
    }
    if (!reed_tracking) {
        reed_started = reed_last = now;
        reed_tracking = 1;
        return 0;
    }
    if (now - reed_last > INT32_MAX || now == reed_last) {
        reed_tracking = 0;
        return 0;
    }
    reed_last = now;
    /* Recheck after timing, so a release during the call cannot qualify. */
    if (!board_reed_is_closed() ||
        (BOARD_GPIO_READ(EXTI_BASE_G0 + EXTI_RPR1_OFF) & GPIO_REED) != 0u) {
        reed_tracking = 0;
        return 0;
    }
    if (now - reed_started < REED_HOLD_SLEEP_MS * 1000u) return 0;
    reed_started = now - REED_HOLD_SLEEP_MS * 1000u; /* Saturate across wraps. */
    return 1;
}

/* Exclusive ADC1/PA1 polling backend; ST sources and analog limitations are
 * documented in VERIFICATION_ADC_CN.md. Recalibrate for every single read. */
#ifndef BOARD_ADC_READ
#define BOARD_ADC_READ(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define BOARD_ADC_WRITE(a, v) (*(volatile uint32_t *)(uintptr_t)(a) = (v))
#endif
#ifndef BOARD_ADC_TIME
#define BOARD_ADC_TIME board_time_us
#endif
#define ADC_BASE_G031 0x40012400u
#define ADC_REG(o) (ADC_BASE_G031 + (o))
#define ADC_RCC_RESET 0x40021030u
#define ADC_RCC_BIT (1u << 20)
#define ADC_REGULATOR (1u << 28)
#define ADC_POLL_MAX 4096u
static int adc_input_settled;

static void adc_modify(uint32_t a, uint32_t mask, uint32_t value)
{
    BOARD_ADC_WRITE(a, (BOARD_ADC_READ(a) & ~mask) | value);
}

static int adc_clock_valid(void)
{
    return (BOARD_ADC_READ(0x40021000u) & 0x3D00u) == 0x500u &&
           (BOARD_ADC_READ(0x40021008u) & 0x7F3Fu) == 0u;
}

static int adc_config_valid(uint32_t trim)
{
    return adc_clock_valid() && BOARD_ADC_READ(0x40021004u) == trim &&
        (BOARD_ADC_READ(RCC_IOPENR_G0) & 1u) != 0u &&
        (BOARD_ADC_READ(RCC_APBENR2_G0) & ADC_RCC_BIT) != 0u &&
        (BOARD_ADC_READ(ADC_RCC_RESET) & ADC_RCC_BIT) == 0u &&
        (BOARD_ADC_READ(0x50000000u) & 12u) == 12u &&
        (BOARD_ADC_READ(0x5000000Cu) & 12u) == 0u &&
        BOARD_ADC_READ(ADC_REG(4u)) == 0u &&
        BOARD_ADC_READ(ADC_REG(12u)) == 0u &&
        BOARD_ADC_READ(ADC_REG(16u)) == 0x80000000u &&
        BOARD_ADC_READ(ADC_REG(20u)) == 7u &&
        BOARD_ADC_READ(ADC_REG(40u)) == 2u &&
        (BOARD_ADC_READ(ADC_REG(8u)) & ~0x80000005u) == ADC_REGULATOR;
}

static int adc_wait(uint32_t a, uint32_t mask, uint32_t expected, uint32_t trim)
{
    unsigned i;
    for (i = 0; i < ADC_POLL_MAX; ++i) {
        if (!adc_config_valid(trim) || (BOARD_ADC_READ(ADC_REG(0u)) & 16u))
            return -1;
        if ((BOARD_ADC_READ(a) & mask) == expected) return 0;
    }
    return -1;
}

static int adc_delay(uint32_t duration, uint32_t trim)
{
    uint32_t start, now;
    unsigned i;
    if (BOARD_ADC_TIME(&start) != 0) return -1;
    for (i = 0; i < ADC_POLL_MAX; ++i) {
        if (!adc_config_valid(trim) || BOARD_ADC_TIME(&now) != 0 ||
            now - start > INT32_MAX) return -1;
        if (now - start >= duration) return 0;
    }
    return -1;
}

static void adc_reset(void)
{
    adc_modify(ADC_RCC_RESET, 0u, ADC_RCC_BIT);
    adc_modify(ADC_RCC_RESET, ADC_RCC_BIT, 0u);
}

int board_adc_read_vbat(uint16_t *adc_12)
{
    uint32_t trim, value = 0u, now;
    int result = -1;
    if (adc_12 == 0 || !adc_clock_valid() || BOARD_ADC_TIME(&now) != 0)
        return -1;
    /* TIM2 epoch starts at boot. Refuse early samples without blocking other
     * acquisition; this guard covers power-on RC settling, not later steps. */
    if (!adc_input_settled) {
        if (now < VBAT_STARTUP_SETTLE_US) return -1;
        adc_input_settled = 1;
    }
    trim = BOARD_ADC_READ(0x40021004u);
    adc_modify(RCC_IOPENR_G0, 0u, 1u);
    (void)BOARD_ADC_READ(RCC_IOPENR_G0);
    adc_modify(0x5000000Cu, 12u, 0u); /* PA1 no pulls. */
    adc_modify(0x50000000u, 12u, 12u); /* PA1 analog; preserve SWD. */
    adc_modify(RCC_APBENR2_G0, 0u, ADC_RCC_BIT);
    (void)BOARD_ADC_READ(RCC_APBENR2_G0);
    adc_reset();
    BOARD_ADC_WRITE(ADC_REG(4u), 0u); /* no interrupt */
    BOARD_ADC_WRITE(ADC_REG(12u), 0u); /* 12-bit right, software single, no DMA */
    BOARD_ADC_WRITE(ADC_REG(16u), 0x80000000u); /* synchronous HCLK/4 = 4 MHz */
    BOARD_ADC_WRITE(ADC_REG(20u), 7u); /* SMP1=160.5 cycles; channel 1 uses SMP1 */
    BOARD_ADC_WRITE(ADC_REG(0u), 0x2000u); /* CCRDY W1C before CHSELR */
    BOARD_ADC_WRITE(ADC_REG(40u), 2u); /* fixed sequence: IN1 only */
    BOARD_ADC_WRITE(ADC_REG(8u), ADC_REGULATOR);
    /* TIM2 measured delays, not empty CPU loops; 30us includes HSI margin. */
    if (adc_delay(30u, trim) != 0 ||
        adc_wait(ADC_REG(0u), 0x2000u, 0x2000u, trim) != 0) goto done;
    BOARD_ADC_WRITE(ADC_REG(0u), 0x800u); /* EOCAL W1C */
    BOARD_ADC_WRITE(ADC_REG(8u), ADC_REGULATOR | 0x80000000u);
    if (adc_wait(ADC_REG(8u), 0x80000000u, 0u, trim) != 0 ||
        adc_wait(ADC_REG(0u), 0x800u, 0x800u, trim) != 0 ||
        adc_delay(2u, trim) != 0) goto done;
    BOARD_ADC_WRITE(ADC_REG(0u), 0x81Fu); /* discard calibration/stale data flags */
    BOARD_ADC_WRITE(ADC_REG(8u), ADC_REGULATOR | 1u);
    if (adc_wait(ADC_REG(0u), 1u, 1u, trim) != 0 ||
        BOARD_ADC_READ(ADC_REG(8u)) != (ADC_REGULATOR | 1u)) goto done;
    BOARD_ADC_WRITE(ADC_REG(8u), ADC_REGULATOR | 5u);
    if (adc_wait(ADC_REG(0u), 12u, 12u, trim) != 0 ||
        adc_wait(ADC_REG(8u), ~ADC_REGULATOR, 1u, trim) != 0) goto done;
    value = BOARD_ADC_READ(ADC_REG(64u)); /* hardware DR; read clears EOC */
    if (value <= ADC_FULL_COUNTS && adc_config_valid(trim) &&
        !(BOARD_ADC_READ(ADC_REG(0u)) & 16u)) result = 0;
done:
    /* Cancels any timed-out operation, powers regulator down; next call must
     * calibrate again. This reset affects ADC only, never the RCC clock tree. */
    adc_reset();
    if (result == 0) *adc_12 = (uint16_t)value;
    return result;
}

uint16_t board_vbat_mv_from_adc(unsigned adc)
{
    uint32_t mv;

    if (adc > ADC_FULL_COUNTS) {
        adc = ADC_FULL_COUNTS;
    }
    mv = ((uint32_t)adc * VBAT_MV_NUM) / VBAT_MV_DEN;
    if (mv > 65535u) {
        mv = 65535u;
    }
    return (uint16_t)mv;
}

/* Exclusive polling USART2 TX; ST register/LL sources and hardware limits
 * are recorded in VERIFICATION_UART_CN.md. RX is deliberately disabled. */
#ifndef BOARD_UART_READ
#define BOARD_UART_READ(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define BOARD_UART_WRITE(a, v) (*(volatile uint32_t *)(uintptr_t)(a) = (v))
#endif
#define UART_CR1 (USART2_BASE_G0 + 0x00u)
#define UART_ISR (USART2_BASE_G0 + 0x1Cu)
#define UART_TDR (USART2_BASE_G0 + 0x28u)
#define UART_RESET 0x4002102Cu
#define UART_GPIO 0x50000000u
#define UART_CONTROL 9u /* UE|TE, 8N1, OVER8=0, FIFO/IRQ/DMA/RX disabled. */
#define UART_TEACK (1u << 21)
static int uart_ready;
static uint32_t uart_trim;

static void uart_modify(uint32_t address, uint32_t mask, uint32_t value)
{
    BOARD_UART_WRITE(address, (BOARD_UART_READ(address) & ~mask) | value);
}

static int uart_clock_valid(void)
{
    /* G031 USART2 uses PCLK; no USART2SEL field on this device. */
    return (BOARD_UART_READ(0x40021000u) & 0x3D00u) == 0x500u &&
           (BOARD_UART_READ(0x40021008u) & 0x7F3Fu) == 0u;
}

static int uart_config_valid(void)
{
    return uart_ready && uart_clock_valid() &&
        BOARD_UART_READ(0x40021004u) == uart_trim &&
        (BOARD_UART_READ(RCC_IOPENR_G0) & RCC_GPIOAEN) != 0u &&
        (BOARD_UART_READ(RCC_APBENR1_G0) & RCC_USART2EN) != 0u &&
        (BOARD_UART_READ(UART_RESET) & RCC_USART2EN) == 0u &&
        BOARD_UART_READ(UART_CR1) == UART_CONTROL &&
        BOARD_UART_READ(USART2_BASE_G0 + 4u) == 0u &&
        BOARD_UART_READ(USART2_BASE_G0 + 8u) == 0u &&
        BOARD_UART_READ(USART2_BASE_G0 + 12u) == USART2_HSI16_BRR &&
        BOARD_UART_READ(USART2_BASE_G0 + 0x2Cu) == 0u &&
        (BOARD_UART_READ(UART_GPIO) & 0xF0u) == 0xA0u &&
        (BOARD_UART_READ(UART_GPIO + 4u) & 0xCu) == 0u &&
        (BOARD_UART_READ(UART_GPIO + 0x0Cu) & 0xF0u) == 0u &&
        (BOARD_UART_READ(UART_GPIO + 0x20u) & 0xFF00u) == 0x1100u;
}

static int uart_abort(void)
{
    if (uart_ready && (BOARD_UART_READ(RCC_APBENR1_G0) & RCC_USART2EN))
        BOARD_UART_WRITE(UART_CR1, 0u);
    uart_ready = 0;
    return -1;
}

static int usart_wait_isr(uint32_t want)
{
    unsigned i;
    for (i = 0; i < USART_XFER_POLL_MAX; ++i) {
        uint32_t status;
        if (!uart_config_valid()) return -1;
        status = BOARD_UART_READ(UART_ISR);
        /* PE/FE/NE/ORE are unexpected even with RX disabled: fail closed. */
        if (status & 0xFu) return -1;
        if ((status & want) == want && uart_config_valid()) return 0;
    }
    return -1;
}

void board_usart2_init(void)
{
    uart_ready = 0;
    uart_modify(RCC_APBENR1_G0, 0u, RCC_USART2EN);
    (void)BOARD_UART_READ(RCC_APBENR1_G0);
    /* Explicit init cancels any previous/partial transmission. */
    uart_modify(UART_RESET, 0u, RCC_USART2EN);
    uart_modify(UART_RESET, RCC_USART2EN, 0u);
    if (!uart_clock_valid()) return;
    uart_trim = BOARD_UART_READ(0x40021004u);
    uart_modify(RCC_IOPENR_G0, 0u, RCC_GPIOAEN);
    (void)BOARD_UART_READ(RCC_IOPENR_G0);
    /* Only PA2/3; PA13/14 SWD, PA9/10 remap and SPI stay untouched. */
    uart_modify(UART_GPIO + 4u, 0xCu, 0u);
    uart_modify(UART_GPIO + 8u, 0xF0u, 0u);
    uart_modify(UART_GPIO + 0x0Cu, 0xF0u, 0u);
    uart_modify(UART_GPIO + 0x20u, 0xFF00u, 0x1100u);
    uart_modify(UART_GPIO, 0xF0u, 0xA0u);
    BOARD_UART_WRITE(UART_CR1, 0u);
    BOARD_UART_WRITE(USART2_BASE_G0 + 4u, 0u);
    BOARD_UART_WRITE(USART2_BASE_G0 + 8u, 0u);
    BOARD_UART_WRITE(USART2_BASE_G0 + 0x2Cu, 0u);
    BOARD_UART_WRITE(USART2_BASE_G0 + 12u, USART2_HSI16_BRR);
    BOARD_UART_WRITE(UART_CR1, UART_CONTROL);
    uart_ready = 1;
    if (usart_wait_isr(UART_TEACK | USART_ISR_TXE | USART_ISR_TC) != 0)
        (void)uart_abort();
}

int board_usart2_write(const uint8_t *data, unsigned len)
{
    unsigned i;
    if (!uart_ready || (len != 0u && data == 0)) return uart_abort();
    for (i = 0; i < len; ++i) {
        if (usart_wait_isr(UART_TEACK | USART_ISR_TXE) != 0)
            return uart_abort();
        /* TDR write clears TXE and TC in hardware; no stale TC success. */
        BOARD_UART_WRITE(UART_TDR, data[i]);
    }
    if (usart_wait_isr(UART_TEACK | USART_ISR_TC) != 0)
        return uart_abort();
    return 0;
}

/* SPI1 and PA4..PA7 are exclusively owned here; no ISR/DMA users.
 * ST CMSIS/LL definitions and limits: VERIFICATION_SPI_CN.md. */
#ifndef BOARD_SPI_READ
#define BOARD_SPI_READ(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define BOARD_SPI_WRITE(a, v) (*(volatile uint32_t *)(uintptr_t)(a) = (v))
#define BOARD_SPI_READ8(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define BOARD_SPI_WRITE8(a, v) (*(volatile uint8_t *)(uintptr_t)(a) = (v))
#endif
#define SPI_GPIO_BASE 0x50000000u
#define SPI_CR1 (SPI1_BASE_G0 + 0u)
#define SPI_CR2 (SPI1_BASE_G0 + 4u)
#define SPI_SR  (SPI1_BASE_G0 + 8u)
#define SPI_DR  (SPI1_BASE_G0 + 12u)
#define SPI_RCC_RESET 0x40021030u
#define SPI_CS (1u << 4)
/* MSTR | BR=/16 | SSI | SSM. CPOL/CPHA=0, MSB first, full duplex. */
#define SPI_CONTROL (0x004u | (3u << 3) | 0x300u)
#define SPI_ENABLE 0x40u
#define SPI_FORMAT 0x1700u /* DS=7 (8 bits), FRXTH=1 (one byte). */
static int spi_ready, spi_gpio_ready, spi_selected;
static uint32_t spi_trim;

static void spi_modify(uint32_t address, uint32_t mask, uint32_t value)
{
    BOARD_SPI_WRITE(address, (BOARD_SPI_READ(address) & ~mask) | value);
}

static int spi_clock_valid(void)
{
    /* Only verified HSI16 /1 SYSCLK, HCLK and PCLK. SCK = 16 MHz /16.
     * Reject other trees rather than silently overspeed a flash device. */
    return (BOARD_SPI_READ(0x40021000u) & 0x3D00u) == 0x500u &&
           (BOARD_SPI_READ(0x40021008u) & 0x7F3Fu) == 0u;
}

static int spi_config_valid(void)
{
    return spi_ready && spi_clock_valid() &&
        BOARD_SPI_READ(0x40021004u) == spi_trim &&
        (BOARD_SPI_READ(RCC_IOPENR_G0) & RCC_GPIOAEN) != 0u &&
        (BOARD_SPI_READ(RCC_APBENR2_G0) & RCC_SPI1EN) != 0u &&
        (BOARD_SPI_READ(SPI_RCC_RESET) & RCC_SPI1EN) == 0u &&
        BOARD_SPI_READ(SPI_CR1) == (SPI_CONTROL | SPI_ENABLE) &&
        BOARD_SPI_READ(SPI_CR2) == SPI_FORMAT &&
        (BOARD_SPI_READ(SPI1_BASE_G0 + 0x1Cu) & 0x800u) == 0u &&
        (BOARD_SPI_READ(SPI_GPIO_BASE) & 0xFF00u) == 0xA900u &&
        (BOARD_SPI_READ(SPI_GPIO_BASE + 4u) & 0xF0u) == 0u &&
        (BOARD_SPI_READ(SPI_GPIO_BASE + 0x20u) & 0xFFF00000u) == 0u;
}

static int spi_abort(void)
{
    /* A partial command may already have reached the flash. Never retry it
     * here or report success. Recovery requires explicit reinitialization. */
    if (spi_gpio_ready) {
        spi_modify(RCC_IOPENR_G0, 0u, RCC_GPIOAEN);
        (void)BOARD_SPI_READ(RCC_IOPENR_G0);
        BOARD_SPI_WRITE(SPI_GPIO_BASE + 0x18u, SPI_CS);
    }
    if (spi_ready && (BOARD_SPI_READ(RCC_APBENR2_G0) & RCC_SPI1EN)) {
        /* OVR: DR then SR; MODF: SR read then CR1 write. Disable SPE.
         * Any remaining FIFO contents are discarded by next init reset. */
        (void)BOARD_SPI_READ8(SPI_DR);
        (void)BOARD_SPI_READ(SPI_SR);
        BOARD_SPI_WRITE(SPI_CR1, SPI_CONTROL);
    }
    spi_ready = spi_selected = 0;
    return -1;
}

static int spi_wait_mask(uint32_t want_set, uint32_t want_clear)
{
    unsigned i;
    for (i = 0; i < SPI_XFER_POLL_MAX; ++i) {
        uint32_t sr;
        if (!spi_config_valid()) return -1;
        sr = BOARD_SPI_READ(SPI_SR);
        if (sr & (SPI_SR_OVR | SPI_SR_MODF | SPI_SR_FRE)) return -1;
        if ((sr & want_set) == want_set && (sr & want_clear) == 0u)
            return 0;
    }
    return -1;
}

void board_spi1_init(void)
{
    spi_ready = spi_selected = 0;
    spi_modify(RCC_IOPENR_G0, 0u, RCC_GPIOAEN);
    (void)BOARD_SPI_READ(RCC_IOPENR_G0);
    /* Preload CS latch before changing PA4 to output, then release it. */
    BOARD_SPI_WRITE(SPI_GPIO_BASE + 0x18u, SPI_CS);
    spi_modify(SPI_GPIO_BASE + 4u, SPI_CS, 0u);
    spi_modify(SPI_GPIO_BASE, 3u << 8, 1u << 8);
    spi_gpio_ready = 1;
    spi_modify(RCC_APBENR2_G0, 0u, RCC_SPI1EN);
    (void)BOARD_SPI_READ(RCC_APBENR2_G0);
    spi_modify(SPI_RCC_RESET, 0u, RCC_SPI1EN);
    spi_modify(SPI_RCC_RESET, RCC_SPI1EN, 0u);
    if (!spi_clock_valid()) return;
    spi_trim = BOARD_SPI_READ(0x40021004u);
    /* RMW only PA4..7; PA13/14 SWD, remap and unrelated RCC stay intact. */
    spi_modify(SPI_GPIO_BASE + 4u, 0xF0u, 0u);
    spi_modify(SPI_GPIO_BASE + 8u, 0xFF00u, 0u); /* low slew at 1 MHz */
    spi_modify(SPI_GPIO_BASE + 0x0Cu, 0xFF00u, 0u);
    spi_modify(SPI_GPIO_BASE + 0x20u, 0xFFF00000u, 0u);
    spi_modify(SPI_GPIO_BASE, 0xFF00u, 0xA900u);
    BOARD_SPI_WRITE(SPI1_BASE_G0 + 0x1Cu, 0u); /* SPI, not I2S */
    BOARD_SPI_WRITE(SPI_CR2, SPI_FORMAT);
    BOARD_SPI_WRITE(SPI_CR1, SPI_CONTROL);
    BOARD_SPI_WRITE(SPI_CR1, SPI_CONTROL | SPI_ENABLE);
    spi_ready = 1;
    if (spi_wait_mask(SPI_SR_TXE, SPI_SR_BSY | SPI_SR_RXNE) != 0)
        (void)spi_abort();
}

int board_spi1_cs(int active_low)
{
    if (!spi_ready) return spi_abort();
    if (spi_wait_mask(SPI_SR_TXE, SPI_SR_BSY | SPI_SR_RXNE) != 0)
        return spi_abort();
    BOARD_SPI_WRITE(SPI_GPIO_BASE + 0x18u,
                    active_low ? SPI_CS << 16 : SPI_CS);
    spi_selected = active_low != 0;
    return 0;
}

static int spi_transfer(const uint8_t *tx, uint8_t *rx, unsigned n)
{
    unsigned i;
    if (!spi_ready || !spi_selected) return spi_abort();
    for (i = 0; i < n; ++i) {
        uint8_t value;
        if (spi_wait_mask(SPI_SR_TXE, 0u) != 0) return spi_abort();
        BOARD_SPI_WRITE8(SPI_DR, tx ? tx[i] : 0xFFu);
        if (spi_wait_mask(SPI_SR_RXNE, 0u) != 0) return spi_abort();
        value = BOARD_SPI_READ8(SPI_DR);
        if (rx) rx[i] = value;
    }
    if (spi_wait_mask(SPI_SR_TXE, SPI_SR_BSY | SPI_SR_RXNE) != 0)
        return spi_abort();
    return 0;
}

int board_spi1_tx(const uint8_t *bytes, unsigned n)
{
    if (n && !bytes) return spi_abort();
    return spi_transfer(bytes, 0, n);
}

int board_spi1_rx(uint8_t *bytes, unsigned n)
{
    if (n && !bytes) return spi_abort();
    return spi_transfer(0, bytes, n);
}

/* Exclusive I2C1/PB6/PB7 polling master. Timing derivation and limitations:
 * VERIFICATION_I2C_CN.md. No interrupt/DMA or concurrent bus owners. */
#ifndef BOARD_I2C_READ
#define BOARD_I2C_READ(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define BOARD_I2C_WRITE(a, v) (*(volatile uint32_t *)(uintptr_t)(a) = (v))
#endif
#ifndef BOARD_I2C_TIME
#define BOARD_I2C_TIME board_time_us
#endif
#define I2C_REG(o) (I2C1_BASE_G0 + (o))
#define I2C_GPIO 0x50000400u
#define I2C_RESET 0x4002102Cu
#define I2C_CCIPR 0x40021054u
#define I2C_SCL 0x40u
#define I2C_SDA 0x80u
#define I2C_ERRORS 0x3F10u /* NACK/BERR/ARLO/OVR/PECERR/TIMEOUT/ALERT */
#define I2C_START (1u << 13)
#define I2C_STOP (1u << 14)
#define I2C_AUTOEND (1u << 25)
static int i2c_ready, i2c_active;
static uint32_t i2c_trim;

static void i2c_modify(uint32_t a, uint32_t mask, uint32_t value)
{
    BOARD_I2C_WRITE(a, (BOARD_I2C_READ(a) & ~mask) | value);
}

static int i2c_clock_valid(void)
{
    return (BOARD_I2C_READ(0x40021000u) & 0x3D00u) == 0x500u &&
           (BOARD_I2C_READ(0x40021008u) & 0x7F3Fu) == 0u;
}

static int i2c_config_valid(void)
{
    return i2c_ready && i2c_clock_valid() &&
        BOARD_I2C_READ(0x40021004u) == i2c_trim &&
        (BOARD_I2C_READ(I2C_CCIPR) & 0x3000u) == 0u &&
        (BOARD_I2C_READ(RCC_APBENR1_G0) & RCC_I2C1EN) != 0u &&
        (BOARD_I2C_READ(I2C_RESET) & RCC_I2C1EN) == 0u &&
        (BOARD_I2C_READ(RCC_IOPENR_G0) & RCC_GPIOBEN) != 0u &&
        BOARD_I2C_READ(I2C_REG(0u)) == 1u &&
        BOARD_I2C_READ(I2C_REG(8u)) == 0u &&
        BOARD_I2C_READ(I2C_REG(12u)) == 0u &&
        BOARD_I2C_READ(I2C_REG(16u)) == I2C1_HSI16_TIMINGR &&
        BOARD_I2C_READ(I2C_REG(20u)) == 0u &&
        (BOARD_I2C_READ(I2C_GPIO) & 0xF000u) == 0xA000u &&
        (BOARD_I2C_READ(I2C_GPIO + 4u) & 0xC0u) == 0xC0u &&
        (BOARD_I2C_READ(I2C_GPIO + 12u) & 0xF000u) == 0u &&
        (BOARD_I2C_READ(I2C_GPIO + 32u) & 0xFF000000u) == 0x66000000u;
}

static int i2c_delay(uint32_t us)
{
    uint32_t start, now;
    unsigned i;
    if (BOARD_I2C_TIME(&start) != 0) return -1;
    for (i = 0; i < I2C_XFER_POLL_MAX; ++i) {
        if (!i2c_clock_valid() || BOARD_I2C_READ(0x40021004u) != i2c_trim ||
            BOARD_I2C_TIME(&now) != 0 || now - start > INT32_MAX) return -1;
        if (now - start >= us) return 0;
    }
    return -1;
}

static int i2c_scl_release(void)
{
    unsigned i;
    uint32_t start, now;
    BOARD_I2C_WRITE(I2C_GPIO + 24u, I2C_SCL);
    if (BOARD_I2C_TIME(&start) != 0) return -1;
    for (i = 0; i < I2C_XFER_POLL_MAX; ++i) {
        if (BOARD_I2C_TIME(&now) != 0 || now - start > 25000u) return -1;
        if (BOARD_I2C_READ(I2C_GPIO + 16u) & I2C_SCL) return i2c_delay(6u);
    }
    return -1;
}

int board_i2c1_bus_recover(void)
{
    unsigned i;
    int result = -1;
    i2c_ready = i2c_active = 0;
    /* This explicit operation assumes a single-master bus. Never called
     * automatically after ARLO. Release pins even if recovery fails. */
    i2c_modify(RCC_IOPENR_G0, 0u, RCC_GPIOBEN);
    (void)BOARD_I2C_READ(RCC_IOPENR_G0);
    i2c_modify(RCC_APBENR1_G0, 0u, RCC_I2C1EN);
    (void)BOARD_I2C_READ(RCC_APBENR1_G0);
    BOARD_I2C_WRITE(I2C_REG(0u), 0u);
    BOARD_I2C_WRITE(I2C_GPIO + 24u, I2C_SCL | I2C_SDA);
    i2c_modify(I2C_GPIO + 4u, 0u, 0xC0u); /* open drain before output mode */
    i2c_modify(I2C_GPIO + 8u, 0xF000u, 0u);
    i2c_modify(I2C_GPIO + 12u, 0xF000u, 0u); /* external pull-ups required */
    i2c_modify(I2C_GPIO, 0xF000u, 0x5000u);
    if (!i2c_clock_valid()) goto done;
    i2c_trim = BOARD_I2C_READ(0x40021004u);
    if (i2c_scl_release() != 0) goto done;
    if (!(BOARD_I2C_READ(I2C_GPIO + 16u) & I2C_SDA)) {
        for (i = 0; i < I2C_RECOVER_SCL_PULSES; ++i) {
            BOARD_I2C_WRITE(I2C_GPIO + 24u, I2C_SCL << 16);
            if (i2c_delay(6u) != 0 || i2c_scl_release() != 0) goto done;
            if (BOARD_I2C_READ(I2C_GPIO + 16u) & I2C_SDA) break;
        }
        /* Form STOP without first creating a START: drive SDA while SCL low. */
        BOARD_I2C_WRITE(I2C_GPIO + 24u, I2C_SCL << 16);
        BOARD_I2C_WRITE(I2C_GPIO + 24u, I2C_SDA << 16);
        if (i2c_delay(6u) != 0 || i2c_scl_release() != 0) goto done;
        BOARD_I2C_WRITE(I2C_GPIO + 24u, I2C_SDA);
        if (i2c_delay(6u) != 0) goto done;
    }
    if ((BOARD_I2C_READ(I2C_GPIO + 16u) & 0xC0u) != 0xC0u) goto done;
    /* Reset only I2C1, select PCLK16, configure with PE=0. */
    i2c_modify(I2C_RESET, 0u, RCC_I2C1EN);
    i2c_modify(I2C_RESET, RCC_I2C1EN, 0u);
    i2c_modify(I2C_CCIPR, 0x3000u, 0u);
    BOARD_I2C_WRITE(I2C_REG(4u), 0u);
    BOARD_I2C_WRITE(I2C_REG(8u), 0u);
    BOARD_I2C_WRITE(I2C_REG(12u), 0u);
    BOARD_I2C_WRITE(I2C_REG(16u), I2C1_HSI16_TIMINGR);
    BOARD_I2C_WRITE(I2C_REG(20u), 0u);
    i2c_modify(I2C_GPIO + 32u, 0xFF000000u, 0x66000000u);
    i2c_modify(I2C_GPIO, 0xF000u, 0xA000u);
    BOARD_I2C_WRITE(I2C_REG(0u), 1u); /* analog filter on, DNF=0, no IRQ/DMA */
    i2c_ready = 1;
    if (i2c_config_valid() &&
        !(BOARD_I2C_READ(I2C_REG(24u)) & (I2C_ERRORS | I2C_ISR_BUSY))) result = 0;
done:
    if (result != 0) {
        BOARD_I2C_WRITE(I2C_REG(0u), 0u);
        BOARD_I2C_WRITE(I2C_GPIO + 24u, 0xC0u);
        i2c_ready = 0;
    }
    return result;
}

void board_i2c1_init(void)
{
    (void)board_i2c1_bus_recover();
}

static int i2c_abort(void)
{
    unsigned i;
    uint32_t status, errors;
    /* Do not force STOP after arbitration loss; another master may own bus.
     * No retries: a partial register write may already have taken effect. */
    if (BOARD_I2C_READ(RCC_APBENR1_G0) & RCC_I2C1EN) {
        status = BOARD_I2C_READ(I2C_REG(24u));
        errors = status & I2C_ERRORS;
        if (i2c_active && i2c_config_valid() && (status & I2C_ISR_BUSY) &&
            !(status & (1u << 9))) {
            i2c_modify(I2C_REG(4u), I2C_START, I2C_STOP);
            for (i = 0; i < I2C_XFER_POLL_MAX; ++i) {
                status = BOARD_I2C_READ(I2C_REG(24u));
                errors |= status & I2C_ERRORS;
                if (!i2c_config_valid() || (status & (I2C_ISR_STOPF | (1u << 9)))) break;
            }
        }
        /* A clean NACK is a device-level failure; other addresses remain usable.
         * This invocation still fails and never replays a possibly partial write. */
        if (errors == I2C_ISR_NACKF && (status & I2C_ISR_STOPF) &&
            !(status & I2C_ISR_BUSY) && i2c_config_valid()) {
            BOARD_I2C_WRITE(I2C_REG(28u), I2C_ISR_NACKF | I2C_ISR_STOPF);
            BOARD_I2C_WRITE(I2C_REG(4u), 0u);
            i2c_active = 0;
            return -1;
        }
        BOARD_I2C_WRITE(I2C_REG(28u), I2C_ERRORS | I2C_ISR_STOPF);
        BOARD_I2C_WRITE(I2C_REG(0u), 0u);
    }
    i2c_ready = i2c_active = 0; /* hard fault requires explicit init/recover */
    return -1;
}

static int i2c_wait(uint32_t set, uint32_t clear)
{
    unsigned i;
    uint32_t start, now, status;
    if (BOARD_I2C_TIME(&start) != 0) return -1;
    for (i = 0; i < I2C_XFER_POLL_MAX; ++i) {
        if (!i2c_config_valid() || BOARD_I2C_TIME(&now) != 0 ||
            now - start > 25000u) return -1;
        status = BOARD_I2C_READ(I2C_REG(24u));
        if ((status & I2C_ERRORS) ||
            ((status & I2C_ISR_STOPF) && !(set & (I2C_ISR_STOPF | I2C_ISR_RXNE)))) return -1;
        if ((status & set) == set && !(status & clear)) return 0;
    }
    return -1;
}

static int i2c_begin(void)
{
    if (!i2c_config_valid()) return -1;
    /* Never clear a stale error and silently accept it as a new transfer. */
    return i2c_wait(0u, I2C_ISR_BUSY | I2C_ISR_RXNE | I2C_ISR_TC);
}

static int i2c_finish(void)
{
    if (i2c_wait(I2C_ISR_STOPF, I2C_ISR_BUSY) != 0) return i2c_abort();
    BOARD_I2C_WRITE(I2C_REG(28u), I2C_ISR_STOPF);
    BOARD_I2C_WRITE(I2C_REG(4u), 0u);
    i2c_active = 0;
    return 0;
}

int board_i2c1_write_u8(uint8_t addr7, uint8_t reg, uint8_t value)
{
    if (addr7 > 0x7Fu) return -1;
    if (i2c_begin() != 0) return i2c_abort();
    i2c_active = 1;
    BOARD_I2C_WRITE(I2C_REG(4u), ((uint32_t)addr7 << 1) |
                    (2u << 16) | I2C_START | I2C_AUTOEND);
    if (i2c_wait(I2C_ISR_TXIS, 0u) != 0) return i2c_abort();
    BOARD_I2C_WRITE(I2C_REG(40u), reg);
    if (i2c_wait(I2C_ISR_TXIS, 0u) != 0) return i2c_abort();
    BOARD_I2C_WRITE(I2C_REG(40u), value);
    return i2c_finish();
}

int board_i2c1_read_n(uint8_t addr7, uint8_t reg, uint8_t *buf, unsigned n)
{
    uint8_t pending[255];
    unsigned i;
    if (addr7 > 0x7Fu || n == 0u || n > sizeof pending || buf == 0) return -1;
    if (i2c_begin() != 0) return i2c_abort();
    i2c_active = 1;
    BOARD_I2C_WRITE(I2C_REG(4u), ((uint32_t)addr7 << 1) | (1u << 16) | I2C_START);
    if (i2c_wait(I2C_ISR_TXIS, 0u) != 0) return i2c_abort();
    BOARD_I2C_WRITE(I2C_REG(40u), reg);
    if (i2c_wait(I2C_ISR_TC, 0u) != 0) return i2c_abort();
    BOARD_I2C_WRITE(I2C_REG(4u), ((uint32_t)addr7 << 1) | (n << 16) |
                    (1u << 10) | I2C_START | I2C_AUTOEND);
    for (i = 0; i < n; ++i) {
        if (i2c_wait(I2C_ISR_RXNE, 0u) != 0) return i2c_abort();
        pending[i] = (uint8_t)BOARD_I2C_READ(I2C_REG(36u));
    }
    if (i2c_finish() != 0) return -1;
    for (i = 0; i < n; ++i) buf[i] = pending[i];
    return 0;
}
