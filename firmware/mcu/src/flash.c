#include "flash.h"

#include <stddef.h>
#include <string.h>

static int spi_cs(int low)
{
    return board_spi1_cs(low);
}

static int spi_tx(const uint8_t *bytes, unsigned n)
{
    return board_spi1_tx(bytes, n);
}

static int spi_rx(uint8_t *bytes, unsigned n)
{
    return board_spi1_rx(bytes, n);
}

static int flash_cmd(const uint8_t *tx, unsigned ntx, uint8_t *rx, unsigned nrx)
{
    if (spi_cs(1) != 0) {
        (void)spi_cs(0);
        return -1;
    }
    if (tx != 0 && ntx != 0 && spi_tx(tx, ntx) != 0) {
        (void)spi_cs(0);
        return -1;
    }
    if (rx != 0 && nrx != 0 && spi_rx(rx, nrx) != 0) {
        (void)spi_cs(0);
        return -1;
    }
    return spi_cs(0);
}

int flash_probe(void)
{
    uint8_t cmd = W25Q_CMD_JEDEC;
    uint8_t id[3];

    if (flash_cmd(&cmd, 1, id, 3) != 0) {
        return -1;
    }
    if (id[0] != W25Q_JEDEC0_WINBOND || id[1] != W25Q_JEDEC1_TYPE ||
        id[2] != W25Q_JEDEC2_256MBIT) {
        return -1;
    }
    cmd = W25Q_CMD_WREN;
    if (flash_cmd(&cmd, 1, 0, 0) != 0) {
        return -1;
    }
    cmd = W25Q_CMD_EN4B;
    if (flash_cmd(&cmd, 1, 0, 0) != 0) {
        return -1;
    }
    return 0;
}

static int flash_wait_not_busy(void)
{
    uint8_t cmd = W25Q_CMD_RDSR1, sr;
    uint32_t started, now, previous;
    unsigned stalled = 0;

    int clock_ok = board_time_us(&started) == 0;
    if (flash_cmd(&cmd, 1, &sr, 1) != 0) return -1;
    /* Already-ready flash remains readable after a TIM2 fault. */
    if ((sr & W25Q_SR1_BUSY) == 0u) return 0;
    if (!clock_ok) return -1;
    previous = started;
    for (;;) {
        if (board_time_us(&now) != 0)
            return -1;
        /* Unsigned subtraction accepts one natural TIM2 wrap. Backwards or
         * implausibly large jumps fail closed before accepting ready. */
        if (now - previous > INT32_MAX || now - started > FLASH_BUSY_TIMEOUT_US)
            return -1;
        if (now == previous) {
            if (++stalled >= FLASH_BUSY_STALL_MAX) return -1;
        } else {
            stalled = 0;
        }
        previous = now;
        /* After observing BUSY, require valid time progress before accepting ready. */
        if ((sr & W25Q_SR1_BUSY) == 0u && now != started) return 0;
        if (now - started == FLASH_BUSY_TIMEOUT_US) return -1;
        if (flash_cmd(&cmd, 1, &sr, 1) != 0) return -1;
    }
}
int flash_read(uint32_t addr, uint8_t *data, unsigned len)
{
    uint8_t hdr[5] = {W25Q_CMD_READ4, (uint8_t)(addr >> 24),
        (uint8_t)(addr >> 16), (uint8_t)(addr >> 8), (uint8_t)addr};
    if (data == 0 || len == 0 || addr >= W25Q_CAPACITY_BYTES ||
        len > W25Q_CAPACITY_BYTES - addr || flash_wait_not_busy() != 0) {
        return -1;
    }
    return flash_cmd(hdr, sizeof(hdr), data, len);
}

int flash_page_program(uint32_t addr, const uint8_t *data, unsigned len)
{
    uint8_t wren = W25Q_CMD_WREN;
    uint8_t hdr[5];
    uint8_t before[W25Q_PAGE_SIZE];
    uint8_t status_cmd = W25Q_CMD_RDSR1, status;
    uint32_t write_started, write_now;

    if (data == 0 || len == 0 || len > W25Q_PAGE_SIZE ||
        addr >= W25Q_CAPACITY_BYTES || len > W25Q_CAPACITY_BYTES - addr) {
        return -1;
    }
    if ((addr & (W25Q_PAGE_SIZE - 1u)) != 0u) {
        return -1; /* keep programs page-aligned; PP wraps inside a page */
    }
    if (flash_read(addr, before, sizeof(before)) != 0) {
        return -1;
    }
    /* A completed write whose response was lost can be acknowledged safely. */
    if (memcmp(before, data, len) == 0) {
        return 0;
    }
    for (unsigned i = 0; i < sizeof(before); ++i) {
        if (before[i] != 0xFFu) {
            return -1; /* never rewrite an occupied or partially programmed page */
        }
    }
    if (board_time_us(&write_started) != 0 || flash_cmd(&wren, 1, 0, 0) != 0) {
        return -1;
    }
    if (flash_cmd(&status_cmd, 1, &status, 1) != 0 ||
        (status & (W25Q_SR1_BUSY | W25Q_SR1_WEL)) != W25Q_SR1_WEL ||
        board_time_us(&write_now) != 0 || write_now == write_started ||
        write_now - write_started > FLASH_BUSY_TIMEOUT_US) {
        return -1;
    }
    hdr[0] = W25Q_CMD_PP4;
    hdr[1] = (uint8_t)(addr >> 24);
    hdr[2] = (uint8_t)(addr >> 16);
    hdr[3] = (uint8_t)(addr >> 8);
    hdr[4] = (uint8_t)addr;
    if (spi_cs(1) != 0) {
        (void)spi_cs(0);
        return -1;
    }
    if (spi_tx(hdr, 5) != 0 || spi_tx(data, len) != 0) {
        (void)spi_cs(0);
        return -1;
    }
    if (spi_cs(0) != 0) {
        return -1;
    }
    if (flash_read(addr, before, len) != 0) {
        return -1;
    }
    return memcmp(before, data, len) == 0 ? 0 : -1;
}
