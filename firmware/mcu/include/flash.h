#ifndef FLASH_W25Q256_REVA2_H
#define FLASH_W25Q256_REVA2_H

#include "board_revA2.h"

/* Winbond W25Q256JV opcodes (rev L / JVEIQ). PA4 = /CS, R12 10 kΩ to 3V3.
 * /WP and /HOLD are strapped to 3V3. This is a command skeleton, not a
 * verified SPI driver. Do not erase a sector that still holds unread log.
 */

#define W25Q_CMD_WREN        0x06u
#define W25Q_CMD_WRDI        0x04u
#define W25Q_CMD_RDSR1       0x05u
#define W25Q_CMD_JEDEC       0x9Fu
#define W25Q_CMD_EN4B        0xB7u /* enter 4-byte address; chip is 32 MB */
#define W25Q_CMD_READ4       0x13u /* read with 4-byte address, either address mode */
#define W25Q_CMD_PP4         0x12u /* page program with 4-byte address */
#define W25Q_SR1_BUSY        (1u << 0)
#define W25Q_SR1_WEL         (1u << 1)
#define W25Q_JEDEC0_WINBOND  0xEFu
#define W25Q_JEDEC1_TYPE     0x40u
#define W25Q_JEDEC2_256MBIT  0x19u
#define W25Q_PAGE_SIZE       256u
#define W25Q_CAPACITY_BYTES  (32u * 1024u * 1024u)

#if W25Q_CMD_WREN != 0x06u || W25Q_CMD_JEDEC != 0x9Fu || W25Q_CMD_PP4 != 0x12u
#error "W25Q256 opcodes do not match Winbond W25Q256JV"
#endif

int flash_probe(void);
int flash_read(uint32_t addr, uint8_t *data, unsigned len);
int flash_page_program(uint32_t addr, const uint8_t *data, unsigned len);

#endif
