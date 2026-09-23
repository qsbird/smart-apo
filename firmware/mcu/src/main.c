#include "app.h"

int main(void)
{
    sensors_status_t sensors;
    app_state_t state = app_boot(&sensors);
    /* Missing or failed HAL timebase prevents recording. */
    for (;;) {
        state = app_step_from_clock(state, &sensors);
    }
}
