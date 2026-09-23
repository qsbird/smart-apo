#ifndef UART_DUMP_REVA2_H
#define UART_DUMP_REVA2_H

#include "datalog.h"

/* Recovery dump over USART2 (PA2/PA3). One sample per frame so a noisy
 * cable cannot desync a whole voyage. Host decoder: firmware/host/dump_decode.py
 *
 * Byte order is little-endian, matching the packed smart_apo_sample_t.
 *
 *  0-1  sync            0xA5 0x5A
 *  2    version         1
 *  3    payload_len     sizeof(smart_apo_sample_t)
 *  4..  payload         sample bytes
 *  last crc16_ccitt of (version..payload), big-endian
 */

#define UART_DUMP_SYNC0     0xA5u
#define UART_DUMP_SYNC1     0x5Au
#define UART_DUMP_VERSION   1u
#define UART_DUMP_HEADER_VERSION 2u
#define UART_DUMP_HEADER_FRAME (4u + sizeof(datalog_header_t) + 2u)
#define UART_DUMP_MAX_FRAME (4u + DATALOG_SAMPLE_SIZE + 2u)

unsigned uart_dump_pack_sample(const smart_apo_sample_t *sample, uint8_t *out, unsigned out_len);
int uart_dump_send_sample(const smart_apo_sample_t *sample);
/* Version 2 carries the original 16-byte APO2 header; v1 samples are unchanged. */
unsigned uart_dump_pack_header(const datalog_header_t *header, uint8_t *out, unsigned out_len);
int uart_dump_send_header(const datalog_header_t *header);

#endif
