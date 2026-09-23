#include "datalog.h"
#include "flash.h"

#include <string.h>

_Static_assert(sizeof(datalog_header_t) == 16, "APO2 header layout changed");
_Static_assert(sizeof(smart_apo_sample_t) == 34, "APO2 sample layout changed");
static uint8_t g_page[DATALOG_PAGE_SIZE];
static unsigned g_used;
static uint32_t g_next_addr;
static int g_readable, g_current_session;
static datalog_header_t g_header;
static uint8_t g_dump_page[DATALOG_PAGE_SIZE];
static uint32_t g_dump_addr;
static unsigned g_dump_offset, g_dump_used;
static int g_dump_loaded;

static int erased(const uint8_t *p, unsigned n)
{
    for (unsigned i = 0; i < n; ++i) {
        if (p[i] != 0xFFu) return 0;
    }
    return 1;
}

static int valid_sample(const smart_apo_sample_t *s)
{
    uint16_t crc = 0xFFFFu;
    const uint8_t *p = (const uint8_t *)s;
    for (unsigned i = 0; i < sizeof(*s) - 2u; ++i) {
        crc ^= (uint16_t)p[i] << 8;
        for (unsigned b = 0; b < 8; ++b) {
            crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u) : (uint16_t)(crc << 1);
        }
    }
    return crc == s->crc16;
}

int datalog_init(uint32_t firmware_hash)
{
    datalog_header_t header;
    g_readable = g_current_session = 0;
    g_used = 0;
    g_next_addr = 0;
    if (flash_probe() != 0 || flash_read(0, g_page, sizeof(g_page)) != 0) {
        return -1;
    }
    if (!erased(g_page, sizeof(g_page))) {
        memcpy(&header, g_page, sizeof(header));
        if (header.magic != DATALOG_MAGIC || header.variant > SMART_APO_VARIANT_UW ||
            header.press_fs_mode > 1u) {
            return -1; /* unknown/partial header: preserve, never overwrite */
        }
        g_readable = 1;
        g_header = header;
        return 1; /* historical voyage, even a compatible one, is read-only */
    }
    memset(&header, 0, sizeof(header));
    header.magic = DATALOG_MAGIC;
    header.firmware_hash = firmware_hash;
    header.variant = (uint8_t)SMART_APO_VARIANT;
    header.imu_odr_hz = (uint8_t)(SMART_APO_VARIANT == SMART_APO_VARIANT_UW ? ODR_IMU_UW_HZ : ODR_IMU_AWA_HZ);
    header.press_odr_hz = (uint8_t)(SMART_APO_VARIANT == SMART_APO_VARIANT_UW ? ODR_PRESS_UW_HZ : ODR_PRESS_AWA_HZ);
    header.press_fs_mode = (uint8_t)(SMART_APO_VARIANT == SMART_APO_VARIANT_UW ? 1u : 0u);
    memcpy(g_page, &header, sizeof(header));
    g_header = header;
    g_used = sizeof(header);
    g_readable = g_current_session = 1;
    return 0;
}

int datalog_flush_page(void)
{
    if (!g_current_session) return -1;
    if (g_used == 0u) return 0;
    if (g_next_addr >= W25Q_CAPACITY_BYTES ||
        flash_page_program(g_next_addr, g_page, DATALOG_PAGE_SIZE) != 0) {
        return -1; /* keep RAM and address; driver refuses occupied pages */
    }
    memset(g_page, 0xFF, sizeof(g_page));
    g_used = 0;
    g_next_addr += DATALOG_PAGE_SIZE;
    return 0;
}

int datalog_append(const smart_apo_sample_t *sample)
{
    if (!g_current_session || sample == 0 || !valid_sample(sample) ||
        g_next_addr >= W25Q_CAPACITY_BYTES) return -1;
    if (g_used + DATALOG_SAMPLE_SIZE > DATALOG_PAGE_SIZE && datalog_flush_page() != 0) {
        return -1;
    }
    /* An implicit flush may have committed the final physical page. */
    if (g_next_addr >= W25Q_CAPACITY_BYTES) return -1;
    memcpy(g_page + g_used, sample, DATALOG_SAMPLE_SIZE);
    g_used += DATALOG_SAMPLE_SIZE;
    return 0;
}

int datalog_dump_begin(void)
{
    g_dump_addr = 0;
    g_dump_offset = sizeof(datalog_header_t);
    g_dump_loaded = 0;
    return g_readable ? 0 : -1;
}

int datalog_dump_header(datalog_header_t *header)
{
    if (!g_readable || header == 0) return -1;
    *header = g_header; /* Historical metadata, not the currently running variant. */
    return 0;
}

int datalog_dump_next(smart_apo_sample_t *sample)
{
    if (!g_readable || sample == 0) return -1;
    while (g_dump_addr < W25Q_CAPACITY_BYTES) {
        if (!g_dump_loaded) {
            if (g_current_session && g_dump_addr >= g_next_addr) {
                if (g_dump_addr > g_next_addr || g_used == 0u) return 0;
                memcpy(g_dump_page, g_page, sizeof(g_dump_page));
                g_dump_used = g_used; /* uncommitted RAM tail, including failed flush */
            } else {
                if (flash_read(g_dump_addr, g_dump_page, sizeof(g_dump_page)) != 0) return -1;
                if (erased(g_dump_page, sizeof(g_dump_page))) return 0;
                g_dump_used = sizeof(g_dump_page);
            }
            g_dump_loaded = 1;
        }
        if (g_dump_offset + DATALOG_SAMPLE_SIZE <= g_dump_used &&
            !erased(g_dump_page + g_dump_offset, DATALOG_SAMPLE_SIZE)) {
            smart_apo_sample_t candidate;
            memcpy(&candidate, g_dump_page + g_dump_offset, DATALOG_SAMPLE_SIZE);
            if (!valid_sample(&candidate)) return -1; /* preserve caller's last valid record */
            memcpy(sample, &candidate, DATALOG_SAMPLE_SIZE);
            g_dump_offset += DATALOG_SAMPLE_SIZE;
            return 1;
        }
        if (g_dump_offset < g_dump_used &&
            !erased(g_dump_page + g_dump_offset, g_dump_used - g_dump_offset)) {
            return -1; /* non-FF padding/hole is corruption, not a normal end */
        }
        /* A flushed partial page has FF padding; next page can still contain records. */
        g_dump_addr += DATALOG_PAGE_SIZE;
        g_dump_offset = 0;
        g_dump_loaded = 0;
    }
    return 0;
}
