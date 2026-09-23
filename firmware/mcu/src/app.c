#include "app.h"

#include "datalog.h"
#include "led.h"
#include "uart_dump.h"

#include <stdint.h>
#include <string.h>

static uint16_t g_sequence;
static int g_dump_done, g_dump_pending, g_unlogged_pending, g_dump_extra_done, g_recovery_only;
static int g_dump_header_pending;
static uint32_t g_errors;
static smart_apo_sample_t g_last, g_dump_sample;

uint32_t app_error_flags(void) {
    if (led_output_failed()) g_errors |= APP_ERROR_LED;
    return g_errors;
}

static app_state_t begin_dump(void)
{
    led_cancel();
    g_dump_done = g_dump_pending = g_dump_extra_done = 0;
    g_dump_header_pending = 1;
    if (datalog_dump_begin() != 0) {
        g_errors |= APP_ERROR_LOG_READ;
        return APP_ERROR;
    }
    return APP_DUMP;
}

static uint16_t crc16_ccitt(const uint8_t *data, unsigned len)
{
    uint16_t crc = 0xFFFFu;
    unsigned i, b;
    for (i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (b = 0; b < 8; b++) {
            crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u) : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

static void finish_sample(smart_apo_sample_t *s)
{
    s->sequence = g_sequence++;
    s->crc16 = crc16_ccitt((const uint8_t *)s, (unsigned)(sizeof(*s) - sizeof(s->crc16)));
}

app_state_t app_boot(sensors_status_t *sensors)
{
    int lse_ok, log_status;
    board_enable_syscfg();
    board_apply_pa9_pa10_remap();
    lse_ok = board_start_clocks();
    board_init_gpio();
    board_spi1_init();
    board_i2c1_init();
    board_reed_exti_setup();
    board_imu_int_exti_setup();
    board_usart2_init();
    log_status = datalog_init(0);
    led_init();
    sensors_init(sensors);
    sensors->lse_ok = lse_ok;
    g_sequence = 0;
    g_dump_done = g_dump_pending = g_unlogged_pending = 0;
    g_errors = 0;
    g_recovery_only = log_status != 0;
    memset(&g_last, 0, sizeof(g_last));
    if (log_status < 0) {
        g_errors |= APP_ERROR_LOG_INIT;
        return APP_ERROR;
    }
    return log_status == 1 ? begin_dump() : APP_RECORD;
}

static app_state_t clock_error(void)
{
    g_errors |= APP_ERROR_CLOCK;
    g_recovery_only = 1;
    led_cancel();
    return APP_ERROR;
}

app_state_t app_step_from_clock(app_state_t state, sensors_status_t *sensors)
{
    uint32_t now_us = 0;
    /* Software idle/dump still run on HSI/TIM2. Service the epoch even without
     * sampling, so long idle periods cannot hide timer wraps. Clock failure
     * forbids recording, but must not prevent read-only recovery attempts. */
    if (board_time_us(&now_us) != 0) {
        if (state == APP_RECORD) return clock_error();
        g_errors |= APP_ERROR_CLOCK;
        g_recovery_only = 1;
    }
    return app_step(state, now_us, sensors);
}

app_state_t app_step(app_state_t state, uint32_t now_us, sensors_status_t *sensors)
{
    smart_apo_sample_t sample;
    if (state == APP_ERROR) {
        /* A failed timebase cannot qualify a timed hold. A real closed input
         * may request read-only recovery; it never authorizes new writes. */
        int request = (g_errors & APP_ERROR_CLOCK) ? board_reed_is_closed()
                                                 : board_reed_held_for_sleep();
        return request ? begin_dump() : APP_ERROR;
    }
    if (state == APP_SLEEP) {
        if (!board_reed_is_closed()) return APP_SLEEP;
        /* APP_SLEEP is currently awake polling: no Stop was entered, and no
         * peripheral/timebase state was lost. Real Stop recovery stays separate. */
        return g_recovery_only ? begin_dump() : APP_RECORD;
    }
    if (state == APP_DUMP) {
        if (g_dump_header_pending) {
            datalog_header_t header;
            if (datalog_dump_header(&header) != 0) {
                g_errors |= APP_ERROR_LOG_READ;
                g_recovery_only = 1;
                return APP_ERROR;
            }
            if (uart_dump_send_header(&header) != 0) {
                g_errors |= APP_ERROR_UART;
                board_usart2_init();
                return APP_DUMP; /* No sample consumed before header succeeds. */
            }
            g_dump_header_pending = 0;
        }
        if (!g_dump_done) {
            if (!g_dump_pending) {
                int next = datalog_dump_next(&g_dump_sample);
                if (next < 0) {
                    g_errors |= APP_ERROR_LOG_READ;
                    g_recovery_only = 1;
                    return APP_ERROR;
                }
                if (next == 0 && g_unlogged_pending && !g_dump_extra_done) {
                    g_dump_sample = g_last; /* sample rejected by append, retained in RAM */
                    g_dump_extra_done = 1;
                    next = 1;
                }
                if (next == 0) g_dump_done = 1;
                else g_dump_pending = 1;
            }
            if (g_dump_pending) {
                if (uart_dump_send_sample(&g_dump_sample) != 0) {
                    g_errors |= APP_ERROR_UART;
                    /* TX backend latches faults. Explicitly reinitialize before
                     * the next whole-record retry; a prefix may already be sent. */
                    board_usart2_init();
                    return APP_DUMP; /* exact same record retried before advancing */
                }
                g_dump_pending = 0;
                return APP_DUMP; /* one frame per app step */
            }
        }
        return board_reed_is_closed() ? APP_DUMP : APP_SLEEP;
    }
    led_poll(now_us);
    if (led_output_failed()) g_errors |= APP_ERROR_LED;
    /* Bite detector is not implemented. After autotune, call
     * led_request_bite_flash(now_us) from the AWA event path only.
     */
    int poll_result = sensors_poll(now_us, &sample, sensors);
    if (poll_result < 0) return clock_error();
    if (poll_result > 0) {
        if (!sensors->lse_ok) {
            sample.flags |= SAMPLE_FLAG_LSE_FAIL;
        }
        finish_sample(&sample);
        g_last = sample;
        if (datalog_append(&sample) != 0) {
            g_errors |= APP_ERROR_LOG_APPEND;
            g_unlogged_pending = g_recovery_only = 1;
            led_cancel();
            return APP_ERROR; /* no further sampling can overwrite this pending sample */
        }
    }
    if (board_reed_held_for_sleep()) {
        led_cancel();
        if (datalog_flush_page() != 0) {
            g_errors |= APP_ERROR_LOG_FLUSH;
            g_recovery_only = 1;
        }
        return begin_dump();
    }
    return APP_RECORD;
}
