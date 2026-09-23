/* Register model, not a peripheral emulator or evidence of board operation. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static uint32_t rcc[32], tim[32];
static int counting, writes_seen;
static volatile uint32_t *model_reg(uintptr_t address)
{
    if (address >= 0x40021000u && address < 0x40021080u)
        return &rcc[(address - 0x40021000u) / 4u];
    assert(address >= 0x40000000u && address < 0x40000080u);
    if (address == 0x40000024u && counting && tim[0] == 1u) ++tim[9];
    ++writes_seen;
    return &tim[(address - 0x40000000u) / 4u];
}
#define BOARD_TIME_REG(address) (*model_reg(address))
/* SPI is outside this timebase model; STOP reinit stays isolated. */
#define BOARD_SPI_READ(a) ((void)(a), 0u)
#define BOARD_SPI_WRITE(a, v) ((void)(a), (void)(v))
#define BOARD_SPI_READ8(a) ((void)(a), (uint8_t)0u)
#define BOARD_SPI_WRITE8(a, v) ((void)(a), (void)(v))
/* I2C is separately modeled; Stop invalidation must not access host MMIO. */
#define BOARD_I2C_READ(a) ((void)(a), 0u)
#define BOARD_I2C_WRITE(a, v) ((void)(a), (void)(v))
/* LSE unavailable in this independent timebase model; no MMIO. */
#define BOARD_LSE_READ(a) ((void)(a), 4u)
#define BOARD_LSE_WRITE(a, v) ((void)(a), (void)(v))
#include "../src/board.c"
static void reset_model(void)
{
    memset(rcc, 0, sizeof rcc);
    memset(tim, 0, sizeof tim);
    rcc[0] = 0x500u;
    rcc[1] = 0x4000u;
    counting = 1;
    writes_seen = time_ready = time_attempted = 0;
    time_last = time_trim = 0;
}
static void expect_failure(void)
{
    uint32_t out = 0xA55A1234u;
    assert(board_time_us(&out) == -1 && out == 0xA55A1234u);
    assert(!time_ready);
}
int main(void)
{
    uint32_t out, prior;
    unsigned i;
    const uint32_t bad_cr[] = {0u, 0x100u, 0x400u, 0xD00u};
    const uint32_t bad_cfgr[] = {1u, 8u, 0x800u, 0x4000u};
    reset_model(); expect_failure();
    for (i = 0; i < sizeof bad_cr / sizeof *bad_cr; ++i) {
        reset_model(); rcc[0] = bad_cr[i]; board_start_clocks();
        expect_failure(); assert(writes_seen == 0);
    }
    for (i = 0; i < sizeof bad_cfgr / sizeof *bad_cfgr; ++i) {
        reset_model(); rcc[2] = bad_cfgr[i]; board_start_clocks();
        expect_failure(); assert(writes_seen == 0);
    }
    reset_model(); counting = 0; board_start_clocks(); expect_failure();
    counting = 1; board_start_clocks(); expect_failure(); /* latched */
    reset_model(); rcc[15] = 0x20000u; rcc[11] = 2u;
    assert(board_start_clocks() == 0); /* LSE remains unavailable */
    assert(time_ready && rcc[15] == 0x20001u && rcc[11] == 2u);
    assert(tim[10] == 15u && tim[11] == UINT32_MAX && tim[5] == 1u);
    assert(tim[2] == 0u && tim[3] == 0u && tim[4] == 0u);
    assert(board_time_us(0) == -1 && time_ready);
    assert(board_time_us(&out) == 0); prior = out;
    board_start_clocks(); assert(board_time_us(&out) == 0 && out > prior);
    /* Native 32-bit rollover; advance through valid bounded intervals. */
    tim[9] = 0x7FFFFFF0u; assert(board_time_us(&out) == 0);
    tim[9] = 0xFFFFFFE0u; assert(board_time_us(&out) == 0);
    tim[9] = UINT32_MAX; assert(board_time_us(&out) == 0 && out == 1u);
    tim[9] = 0x80000010u; expect_failure();
    /* Each observed configuration failure latches even after restoration. */
    for (i = 0; i < 11; ++i) {
        volatile uint32_t *reg;
        uint32_t value;
        reset_model(); board_start_clocks(); assert(time_ready);
        switch (i) {
        case 0: reg = &rcc[0]; break;
        case 1: reg = &rcc[1]; break;
        case 2: reg = &rcc[2]; break;
        case 3: reg = &rcc[15]; break;
        case 4: reg = &rcc[11]; break;
        case 5: reg = &rcc[19]; break;
        case 6: reg = &tim[0]; break;
        case 7: reg = &tim[2]; break;
        case 8: reg = &tim[3]; break;
        case 9: reg = &tim[10]; break;
        default: reg = &tim[11]; break;
        }
        value = *reg; *reg ^= i == 0 ? 0x400u : 1u;
        expect_failure(); *reg = value; expect_failure();
    }
    reset_model(); board_start_clocks(); counting = 0; expect_failure();
    reset_model(); board_start_clocks(); tim[9] = 100u;
    assert(board_time_us(&out) == 0); tim[9] = 0u; expect_failure();
    reset_model(); board_start_clocks(); board_buses_reinit_after_stop();
    expect_failure(); board_start_clocks(); expect_failure();
    puts("TIM2 model: clocks, initialization, progress, wrap, faults, Stop passed");
    return 0;
}
