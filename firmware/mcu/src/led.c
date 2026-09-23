#include "led.h"

static int g_active, g_output_fault;
static uint32_t g_start_us;
static uint32_t g_end_us;

static void led_gate_set(int on)
{
    if (board_led_gate_set(on) != 0) {
        g_output_fault = 1;
        g_active = 0;
        (void)board_led_gate_set(0); /* best effort; a stuck output may stay on */
    }
}

void led_init(void)
{
    g_active = g_output_fault = 0;
    g_start_us = 0;
    g_end_us = 0;
    led_gate_set(0);
}

void led_cancel(void)
{
    g_active = 0;
    led_gate_set(0);
}

void led_request_bite_flash(uint32_t now_us)
{
    if (SMART_APO_VARIANT != SMART_APO_VARIANT_AWA || g_output_fault) {
        return;
    }
    g_active = 1;
    g_start_us = now_us;
    g_end_us = now_us + (LED_BURST_MS * 1000u);
}

void led_poll(uint32_t now_us)
{
    unsigned half;

    if (SMART_APO_VARIANT != SMART_APO_VARIANT_AWA || g_output_fault) {
        return;
    }
    if (!g_active) {
        return;
    }
    if ((int32_t)(now_us - g_end_us) >= 0) {
        led_cancel();
        return;
    }
    half = (unsigned)((now_us - g_start_us) / LED_HALF_PERIOD_US);
    led_gate_set((half & 1u) == 0u);
}

int led_output_failed(void) { return g_output_fault; }
