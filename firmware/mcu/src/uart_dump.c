#include "uart_dump.h"

#include <string.h>

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

unsigned uart_dump_pack_sample(const smart_apo_sample_t *sample, uint8_t *out, unsigned out_len)
{
    unsigned n = UART_DUMP_MAX_FRAME;
    uint16_t crc;
    if (sample == 0 || out == 0 || out_len < n) {
        return 0;
    }
    out[0] = (uint8_t)UART_DUMP_SYNC0;
    out[1] = (uint8_t)UART_DUMP_SYNC1;
    out[2] = (uint8_t)UART_DUMP_VERSION;
    out[3] = (uint8_t)DATALOG_SAMPLE_SIZE;
    memcpy(out + 4, sample, DATALOG_SAMPLE_SIZE);
    crc = crc16_ccitt(out + 2, 2u + DATALOG_SAMPLE_SIZE);
    out[4 + DATALOG_SAMPLE_SIZE] = (uint8_t)(crc >> 8);
    out[5 + DATALOG_SAMPLE_SIZE] = (uint8_t)(crc & 0xFFu);
    return n;
}

int uart_dump_send_sample(const smart_apo_sample_t *sample)
{
    uint8_t frame[UART_DUMP_MAX_FRAME];
    unsigned n = uart_dump_pack_sample(sample, frame, sizeof(frame));
    if (n == 0) {
        return -1;
    }
    /* USART2 TX on PA2 AF1 after board_usart2_init(). */
    return board_usart2_write(frame, n);
}

unsigned uart_dump_pack_header(const datalog_header_t *header, uint8_t *out, unsigned out_len)
{
    uint16_t crc;
    if (header == 0 || out == 0 || out_len < UART_DUMP_HEADER_FRAME) return 0;
    out[0] = UART_DUMP_SYNC0;
    out[1] = UART_DUMP_SYNC1;
    out[2] = UART_DUMP_HEADER_VERSION;
    out[3] = (uint8_t)sizeof(*header);
    memcpy(out + 4, header, sizeof(*header));
    crc = crc16_ccitt(out + 2, 2u + sizeof(*header));
    out[4 + sizeof(*header)] = (uint8_t)(crc >> 8);
    out[5 + sizeof(*header)] = (uint8_t)crc;
    return UART_DUMP_HEADER_FRAME;
}

int uart_dump_send_header(const datalog_header_t *header)
{
    uint8_t frame[UART_DUMP_HEADER_FRAME];
    unsigned n = uart_dump_pack_header(header, frame, sizeof(frame));
    return n ? board_usart2_write(frame, n) : -1;
}
