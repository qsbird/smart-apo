#include "datalog.h"
#include "flash.h"
#include <assert.h>
#include <string.h>
static uint8_t storage[1024];
static int probe_result, program_result, read_result, calls;
int flash_probe(void) {return probe_result;}
int flash_read(uint32_t a, uint8_t *p, unsigned n) {
    assert(a+n<=sizeof(storage));
    if (read_result) return -1;
    memcpy(p, storage+a, n); return 0;
}
int flash_page_program(uint32_t a, const uint8_t *p, unsigned n) {
    assert(a+n<=sizeof(storage)); ++calls;
    if (program_result) return -1;
    memcpy(storage+a, p, n); return 0;
}
static smart_apo_sample_t sample(unsigned seq) {
    smart_apo_sample_t s = {.sequence=(uint16_t)seq, .timestamp_us=seq*1000};
    uint16_t crc=0xffff;
    const uint8_t *p=(const uint8_t *)&s;
    for (unsigned i=0;i<sizeof(s)-2;++i) {
        crc ^= (uint16_t)p[i]<<8;
        for(unsigned b=0;b<8;++b) crc=(crc&0x8000)?(uint16_t)((crc<<1)^0x1021):(uint16_t)(crc<<1);
    }
    s.crc16=crc; return s;
}
int main(void) {
    smart_apo_sample_t s=sample(0), out;
    memset(storage,0xff,sizeof(storage));
    probe_result=-1;
    assert(datalog_init(123)==-1);
    assert(datalog_append(&s)==-1 && datalog_flush_page()==-1 && calls==0);
    assert(datalog_dump_begin()==-1);
    probe_result=0; read_result=-1;
    assert(datalog_init(123)==-1 && datalog_append(&s)==-1);
    read_result=0;
    assert(datalog_init(123)==0);
    for(unsigned i=0;i<7;++i) {s=sample(i); assert(datalog_append(&s)==0);}
    program_result=-1; s=sample(7);
    assert(datalog_append(&s)==-1);
    assert(datalog_dump_begin()==0);
    for(unsigned i=0;i<7;++i) {assert(datalog_dump_next(&out)==1); assert(out.sequence==i);}
    assert(datalog_dump_next(&out)==0);
    program_result=0;
    assert(datalog_append(&s)==0); /* commits first full page, retains sample 7 */
    assert(datalog_flush_page()==0); /* commits partial second page */
    s=sample(8); assert(datalog_append(&s)==0);
    assert(datalog_dump_begin()==0);
    for(unsigned i=0;i<9;++i) {assert(datalog_dump_next(&out)==1); assert(out.sequence==i);}
    assert(datalog_dump_next(&out)==0); /* includes RAM tail */
    assert(datalog_flush_page()==0);
    uint8_t saved[1024]; memcpy(saved,storage,sizeof(saved)); int previous_calls=calls;
    assert(datalog_init(999)==1); /* power cycle: historical voyage */
    assert(datalog_append(&s)==-1 && datalog_flush_page()==-1);
    assert(calls==previous_calls && memcmp(saved,storage,sizeof(saved))==0);
    assert(datalog_dump_begin()==0);
    for(unsigned i=0;i<9;++i) {assert(datalog_dump_next(&out)==1); assert(out.sequence==i);}
    assert(datalog_dump_next(&out)==0);
    read_result=-1; assert(datalog_dump_begin()==0); assert(datalog_dump_next(&out)==-1);
    read_result=0; assert(datalog_dump_next(&out)==1 && out.sequence==0);
    storage[16]^=1; assert(datalog_dump_begin()==0);
    out=sample(999); smart_apo_sample_t last_good=out;
    assert(datalog_dump_next(&out)==-1);
    assert(memcmp(&out,&last_good,sizeof(out))==0); /* corrupt bytes never escape */
    storage[16]^=1; /* repair the model storage; failed read did not advance */
    assert(datalog_dump_begin()==0); /* reload repaired page rather than cached corruption */
    assert(datalog_dump_next(0)==-1); /* invalid destination must not consume a record */
    assert(datalog_dump_next(&out)==1 && out.sequence==0);
    storage[0]^=1; assert(datalog_init(123)==-1 && datalog_append(&s)==-1);
    assert(calls==previous_calls);
    return 0;
}
