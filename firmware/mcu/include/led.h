#ifndef LED_REVA2_H
#define LED_REVA2_H

#include "board_revA2.h"

/* AWA-only bite-alert flash on PB0 / LED_GATE (MOSFET, active-high).
 * This is the output driver, not a bite detector. Detection thresholds
 * come from autotune.py after a labelled voyage; do not hard-code a
 * "fish" classifier here.
 *
 * Burst: 10 Hz, 50% duty, 2 s, then off. Cancel on DUMP/SLEEP.
 * Underwater assembly is a teacher logger: led_* is a no-op there.
 */

#define LED_FLASH_HZ           10u
#define LED_BURST_MS         2000u
#define LED_HALF_PERIOD_US  (1000000u / (LED_FLASH_HZ * 2u))

/* Latched until explicit led_init(); readback is not optical verification. */
int led_output_failed(void);
void led_init(void);
void led_request_bite_flash(uint32_t now_us);
void led_cancel(void);
void led_poll(uint32_t now_us);

#endif
