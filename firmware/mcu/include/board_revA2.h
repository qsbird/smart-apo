#ifndef BOARD_REVA2_H
#define BOARD_REVA2_H

#include <stdint.h>

/* STM32G031F8P6 TSSOP20 pin map for Smart Apo Rev.A2.
 * Physical pin order is from ST DS12992 Rev 4 Figure 5, not Rev.A1's
 * incorrect 1-20 logical mapping.
 *
 * CubeMX is not installed here. These constants are for a future HAL/LL
 * project and for code review against the schematic netlist.
 */

#define SMART_APO_VARIANT_AWA 0
#define SMART_APO_VARIANT_UW  1

#ifndef SMART_APO_VARIANT
#define SMART_APO_VARIANT SMART_APO_VARIANT_AWA
#endif

/* SYSCFG_CFGR1 bits from RM0444 Rev 6. Set both before using PA9/PA10. */
#define SMART_APO_SYSCFG_PA11_RMP (1u << 3)
#define SMART_APO_SYSCFG_PA12_RMP (1u << 4)

#define PIN_I2C_SDA        1u  /* PB7, I2C1 SDA AF6 */
#define PIN_LSE_IN         2u  /* PC14 */
#define PIN_LSE_OUT        3u  /* PC15 */
#define PIN_3V3            4u
#define PIN_GND            5u
#define PIN_NRST           6u
#define PIN_IMU_INT        7u  /* PA0 EXTI */
#define PIN_VBAT_SENSE     8u  /* PA1 ADC */
#define PIN_UART_TX        9u  /* PA2 USART2 AF1 */
#define PIN_UART_RX       10u  /* PA3 USART2 AF1 */
#define PIN_FLASH_CS      11u  /* PA4 GPIO; R12 10k pull-up to 3V3 */
#define PIN_SPI_SCK       12u  /* PA5 SPI1 AF0 */
#define PIN_SPI_MISO      13u  /* PA6 SPI1 AF0 */
#define PIN_SPI_MOSI      14u  /* PA7 SPI1 AF0 */
#define PIN_LED_GATE      15u  /* PB0 GPIO */
#define PIN_REED_WAKE     16u  /* PA9 after PA11_RMP */
#define PIN_STRAIN_DRDY   17u  /* PA10 after PA12_RMP */
#define PIN_SWDIO         18u  /* PA13, do not reassign */
#define PIN_SWCLK         19u  /* PA14, do not reassign */
#define PIN_I2C_SCL       20u  /* PB6, I2C1 SCL AF6 */

#define I2C_ADDR_LSM6DSO_SA0_GND  0x6Au
#define I2C_ADDR_LPS28DFW         0x5Cu
#define I2C_ADDR_NAU7802          0x2Au

#define ODR_IMU_AWA_HZ      104u
#define ODR_IMU_UW_HZ       208u
#define ODR_PRESS_AWA_HZ     50u
#define ODR_PRESS_UW_HZ     100u
#define ODR_STRAIN_UW_SPS   320u
#define ODR_BATT_HZ           1u

#define LSE_STARTUP_TIMEOUT_MS  2000u
#define LSE_STARTUP_TIMEOUT_US  (LSE_STARTUP_TIMEOUT_MS * 1000u)

/* SW1 is NO to GND; R10 100 kΩ pulls REED_WAKE to 3V3. Closed = 0.
 * Long press in RECORD enters DUMP. EXTI9 rising pending records release;
 * currently polled only, not a Stop wake source. Configure after PA11_RMP.
 */
#define REED_CLOSED_LEVEL       0
#define REED_HOLD_SLEEP_MS      1500u
#define REED_EXTI_LINE          9u
#define IMU_EXTI_LINE           0u  /* PA0, LSM6DSO INT1, default active-high */
#define EXTI_BASE_G0            0x40021800u
#define EXTI_RTSR1_OFF          0x00u
#define EXTI_FTSR1_OFF          0x04u
#define EXTI_RPR1_OFF           0x0Cu
#define EXTI_FPR1_OFF           0x10u
#define EXTI_EXTICR1_OFF        0x60u
#define EXTI_EXTICR3_OFF        0x68u
#define EXTI_IMR1_OFF           0x80u

/* R4=180 kΩ VBAT→VBAT_SENSE, R5=60.4 kΩ to GND. STM32G031 12-bit ADC, VDDA=3.3 V.
 * mV = adc * 3300 * 240400 / (60400 * 4095) = adc * 132220 / 41223.
 * Worst 1% Thevenin resistance is <50 kΩ; VREF/analog accuracy remain unverified.
 */
#define VBAT_R_TOP_OHM      180000u
#define VBAT_R_BOT_OHM       60400u
#define ADC_VREF_MV           3300u
#define ADC_FULL_COUNTS       4095u
#define VBAT_MV_NUM         132220u
#define VBAT_MV_DEN          41223u
/* From boot TIM2 epoch, nonblocking. R/C/HSI assumptions in startup report. */
#define VBAT_STARTUP_SETTLE_US 100000u

/* USART2 on PA2/PA3 AF1. Do not use PA9/PA10 (those are reed/DRDY after remap).
 * RM0444: USART2 0x40004400, APBENR1 USART2EN bit 17, IOPENR GPIOAEN bit 0.
 * 115200 8N1. With default HSI 16 MHz and OVER8=0, BRR ≈ 139.
 */
#define USART2_BASE_G0       0x40004400u
#define USART2_AF            1u
#define USART2_BAUD          115200u
#define USART2_HSI16_BRR     139u
#define RCC_IOPENR_G0        0x40021034u
#define RCC_APBENR1_G0       0x4002103Cu
#define RCC_APBENR2_G0       0x40021040u
#define RCC_GPIOAEN          (1u << 0)
#define RCC_GPIOBEN          (1u << 1)
#define RCC_USART2EN         (1u << 17)
#define RCC_I2C1EN           (1u << 21)
#define RCC_SPI1EN           (1u << 12)
#define SPI1_BASE_G0         0x40013000u
#define SPI1_AF              0u /* PA5/PA6/PA7 AF0, mode 0 for W25Q256 */
#define I2C1_BASE_G0         0x40005400u
#define I2C1_AF              6u /* PB6 SCL / PB7 SDA AF6, open-drain */
#define I2C1_HSI16_TIMINGR   0x10A2272Fu /* conservative Standard-mode @ PCLK16; see VERIFICATION_I2C_CN.md */

/* RM0444 I2C_ISR: TXIS bit1, RXNE bit2, NACKF bit4, STOPF bit5, TC bit6, BUSY bit15.
 * SPI_SR: RXNE bit0, TXE bit1, BSY bit7. Timeouts are poll counts, not a timer.
 */
#define I2C_ISR_TXIS         (1u << 1)
#define I2C_ISR_RXNE         (1u << 2)
#define I2C_ISR_NACKF        (1u << 4)
#define I2C_ISR_STOPF        (1u << 5)
#define I2C_ISR_TC           (1u << 6)
#define I2C_ISR_BUSY         (1u << 15)
#define SPI_SR_RXNE          (1u << 0)
#define SPI_SR_TXE           (1u << 1)
#define SPI_SR_MODF          (1u << 5)
#define SPI_SR_OVR           (1u << 6)
#define SPI_SR_FRE           (1u << 8)
#define SPI_SR_BSY           (1u << 7)
#define I2C_XFER_POLL_MAX    4096u
#define SPI_XFER_POLL_MAX    256u
/* W25Q256JV Rev R, 9.7 p84: tPP max 3ms; 2ms margin. Not an erase timeout. */
#define FLASH_BUSY_TIMEOUT_US 5000u
#define FLASH_BUSY_STALL_MAX  4096u /* fault termination, not calibrated time */
#define I2C_RECOVER_SCL_PULSES 9u
#define USART_ISR_TXE        (1u << 7)
#define USART_ISR_TC         (1u << 6)
#define USART_XFER_POLL_MAX  256u

#if VBAT_R_TOP_OHM != 180000u || VBAT_R_BOT_OHM != 60400u
#error "VBAT divider ohms do not match R4 180k / R5 60.4k"
#endif

typedef struct __attribute__((packed)) {
    uint32_t timestamp_us;
    uint16_t sequence;
    int16_t ax, ay, az;
    int16_t gx, gy, gz;
    int32_t pressure_raw;
    int32_t tension_raw;
    int16_t temperature;
    uint16_t battery_mv;
    uint16_t flags;
    uint16_t crc16;
} smart_apo_sample_t;

void board_apply_pa9_pa10_remap(void);
/* Initialize TIM2 first; return 1 only for observed crystal-mode LSE ready
 * with a valid TIM2 clock, otherwise 0 (app records LSE_FAIL). Wait at most
 * 2 s of nominal HSI/TIM2 time including DBP access. Preserve LSE drive and
 * backup/RTC selection; reject bypass/CSS fault/reset. No crystal qualification,
 * RTC setup, timestamp calibration, interrupts or Stop support is implied.
 * Exclusive startup register access; no concurrent RCC/PWR writers. */
int board_start_clocks(void);
/* board_start_clocks initializes exclusive TIM2 on validated HSI16 /1 clocks.
 * 0 writes nominal microseconds modulo 2^32; -1 leaves output untouched.
 * Faults latch until reset; Stop/wake invalidates the epoch. Call at least
 * once per INT32_MAX us. HSI tolerance applies; not an absolute time source.
 * No other code/ISR may change TIM2, RCC clock tree or trim. Transient stops
 * or resets restored between calls cannot be detected without an independent
 * reference; see VERIFICATION_TIM2_CN.md. No time is derived from CPU loops.
 */
int board_time_us(uint32_t *now_us);
/* Init order: enable_syscfg, remap, init_gpio, reed_exti_setup. PA4 starts high,
 * PB0 low; PA0/9/10 inputs without internal pulls; unrelated pins/SWD preserved.
 * reed_is_closed reads active-low IDR. held requires valid TIM2 and 1.5 s since
 * first closed observation; any observed release/EXTI9 rising latch restarts it.
 * Call at least once per INT32_MAX us. Time/config errors return false and reset
 * tracking. Exclusive EXTI9, no concurrent readers clearing its rising pending.
 * IMU pending is live PA0 active-high level, not a queued event: pulses may be
 * missed. No NVIC, ISR, Stop/wake, or LED waveform implementation is implied. */
void board_enable_syscfg(void);
void board_init_gpio(void);
/* PB0 latch control/readback only; does not prove LED current or optical output. */
int board_led_gate_set(int on);
void board_reed_exti_setup(void);
void board_imu_int_exti_setup(void);
int board_imu_int_pending(void);
int board_reed_is_closed(void);
int board_reed_held_for_sleep(void);
void board_buses_reinit_after_stop(void);
/* Exclusive ADC1/PA1, single 12-bit raw reading. Requires initialized valid
 * TIM2 and HSI16 /1 tree. Each call resets/calibrates ADC; failure leaves output
 * unchanged. Bounded waits; no ISR/DMA/concurrent RCC or GPIO writers.
 * 0 validates conversion completion, NOT analog accuracy: existing divider
 * now uses 180k/60.4k (<50k Thevenin with 1% tolerance); analog accuracy
 * and settling still require validation. See VERIFICATION_ADC_CN.md. */
int board_adc_read_vbat(uint16_t *adc_12);
uint16_t board_vbat_mv_from_adc(unsigned adc);
/* Exclusive USART2 TX, validated HSI16/PCLK /1, nominal 115200 8N1.
 * PA2/3 AF1; RX disabled. Init cancels prior transmission. Poll counts are
 * bounded, not calibrated timeouts. 0 means last stop bit completed, not host
 * acknowledgement. -1 may follow a partial or even complete wire frame;
 * failure latches until explicit init. No transparent retry, ISR or DMA.
 * len=0 checks readiness/TC; NULL is allowed only then. */
void board_usart2_init(void);
int board_usart2_write(const uint8_t *data, unsigned len);
/* Exclusive polling SPI1, HSI16 /1 tree required, nominal SCK=1 MHz.
 * Mode0, 8-bit, PA4 software CS. Init aborts any previous transaction.
 * -1 releases CS and latches failure until init; partial RX prefix and flash
 * side effects may exist and must not be treated as a complete transaction.
 * Caller serializes all operations; tx/rx require asserted CS, including n=0.
 * Poll bounds are iteration limits, not calibrated timeouts. */
void board_spi1_init(void);
int board_spi1_cs(int active_low);
int board_spi1_tx(const uint8_t *bytes, unsigned n);
int board_spi1_rx(uint8_t *bytes, unsigned n);
/* Exclusive single-master PB6/PB7, external pull-ups and working TIM2 required.
 * Standard-mode <=100kHz under documented timing assumptions; board unverified.
 * read_n accepts 1..255 bytes; failure leaves output unchanged. Hard transfer
 * faults latch unavailable until explicit init/recover; a clean NACK permits
 * later calls to other addresses. No automatic replay. */
void board_i2c1_init(void);
int board_i2c1_bus_recover(void);
int board_i2c1_write_u8(uint8_t addr7, uint8_t reg, uint8_t value);
int board_i2c1_read_n(uint8_t addr7, uint8_t reg, uint8_t *buf, unsigned n);

#endif
