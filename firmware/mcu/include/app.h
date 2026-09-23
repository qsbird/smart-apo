#ifndef APP_REVA2_H
#define APP_REVA2_H

#include "board_revA2.h"
#include "sensors.h"

typedef enum {
    APP_BOOT = 0,
    APP_RECORD,
    APP_SLEEP, /* Software idle only; hardware Stop is not implemented. */
    APP_DUMP,
    APP_ERROR
} app_state_t;

#define APP_ERROR_LOG_INIT   (1u << 0)
#define APP_ERROR_LOG_APPEND (1u << 1)
#define APP_ERROR_LOG_FLUSH  (1u << 2)
#define APP_ERROR_LOG_READ   (1u << 3)
#define APP_ERROR_UART       (1u << 4)
#define APP_ERROR_CLOCK      (1u << 5)
#define APP_ERROR_LED        (1u << 6)
uint32_t app_error_flags(void);

app_state_t app_boot(sensors_status_t *sensors);
app_state_t app_step_from_clock(app_state_t state, sensors_status_t *sensors);
app_state_t app_step(app_state_t state, uint32_t now_us, sensors_status_t *sensors);

#endif
