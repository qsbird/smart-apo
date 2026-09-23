#ifndef DATALOG_REVA2_H
#define DATALOG_REVA2_H

#include "board_revA2.h"

/* W25Q256JV: 256-byte pages, 4 KB sectors. Sample records are packed and
 * appended; the log is append-only. This is a source skeleton, not a
 * verified flash driver.
 */

#define DATALOG_PAGE_SIZE     256u
#define DATALOG_SAMPLE_SIZE   ((unsigned)sizeof(smart_apo_sample_t))
#define DATALOG_MAGIC         0x41504F32u /* "APO2" */

#define SAMPLE_FLAG_LSE_FAIL  (1u << 0)
#define SAMPLE_FLAG_IMU_OK    (1u << 1)
#define SAMPLE_FLAG_PRESS_OK  (1u << 2)
#define SAMPLE_FLAG_STRAIN_OK (1u << 3)
#define SAMPLE_FLAG_SYNC_TAP  (1u << 4)

typedef struct {
    uint32_t magic;
    uint32_t firmware_hash;
    uint8_t variant;
    uint8_t imu_odr_hz;
    uint8_t press_odr_hz;
    uint8_t press_fs_mode; /* 0 = 1260 hPa / 4096 LSB; 1 = 4060 hPa / 2048 LSB */
    uint32_t start_unix_optional;
} datalog_header_t;

/* init: 0 = writable fresh voyage, 1 = existing voyage read-only, -1 = fault.
 * Existing format remains APO2: 16-byte header, 34-byte records, FF page padding.
 * No erase or automatic reuse is provided. */
int datalog_init(uint32_t firmware_hash);
int datalog_dump_begin(void);
/* Original voyage metadata; failure leaves output unchanged. */
int datalog_dump_header(datalog_header_t *header);
/* next: 1 = CRC-checked record, 0 = end, -1 = read/corruption fault.
 * Output is unchanged on 0/-1; a null destination returns -1 without advancing.
 * Caller retains returned record until UART succeeds. */
int datalog_dump_next(smart_apo_sample_t *sample);
int datalog_append(const smart_apo_sample_t *sample);
int datalog_flush_page(void);

#endif
