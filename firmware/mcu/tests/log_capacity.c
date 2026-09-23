#include "datalog.h"
#include "flash.h"
#include <assert.h>
#include <string.h>
static unsigned programs;
int flash_probe(void) {return 0;}
int flash_read(uint32_t a, uint8_t *p, unsigned n) {
    assert(a==0); memset(p,0xff,n); return 0;
}
int flash_page_program(uint32_t a, const uint8_t *p, unsigned n) {
    (void)p; assert(a==programs*256u && n==256u);
    assert(a<W25Q_CAPACITY_BYTES); ++programs; return 0;
}
int main(void) {
    smart_apo_sample_t s={0};
    uint16_t crc=0xffff;
    for(unsigned i=0;i<sizeof(s)-2;++i) {
        for(unsigned b=0;b<8;++b) crc=(crc&0x8000)?(uint16_t)((crc<<1)^0x1021):(uint16_t)(crc<<1);
    }
    s.crc16=crc;
    assert(datalog_init(0)==0);
    unsigned pages=W25Q_CAPACITY_BYTES/DATALOG_PAGE_SIZE;
    /* Both header page and ordinary pages hold seven 34-byte records. */
    for(unsigned i=0;i<pages*7u;++i) assert(datalog_append(&s)==0);
    assert(programs==pages-1u);
    /* This append flushes the last full page: do not accept an unexportable RAM tail. */
    assert(datalog_append(&s)==-1 && programs==pages);
    assert(datalog_append(&s)==-1 && programs==pages);
    assert(datalog_flush_page()==0 && programs==pages);
    return 0;
}
