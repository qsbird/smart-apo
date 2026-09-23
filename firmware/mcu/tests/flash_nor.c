#include "flash.h"
#include <assert.h>
#include <string.h>
static uint8_t memory[512], opcode, status;
static uint32_t address;
static int selected, pp_count, deny_wel, corrupt_write, read_fail;
static uint32_t now_us, program_start, program_duration, tick_us = 10;
static unsigned polls, time_calls, time_fail_call;
static int time_fail, freeze_time, backwards_time, status_fail, tx_fail, cs_fail, fail_after_program;
int board_time_us(uint32_t *out) {
    ++time_calls;
    if (time_fail || (time_fail_call && time_calls>=time_fail_call)) return -1;
    *out = backwards_time && time_calls == 3 ? now_us - 1000u : now_us;
    return 0;
}
int board_spi1_cs(int active) {
    selected=active;
    if(active) { opcode=0; if(cs_fail) return -1; }
    else if(opcode==W25Q_CMD_PP4) { status &= (uint8_t)~W25Q_SR1_WEL; program_start=now_us; if(fail_after_program) time_fail=1; }
    return 0;
}
int board_spi1_tx(const uint8_t *p, unsigned n) {
    assert(selected);
    if(tx_fail) return -1;
    if(!opcode) {
        opcode=p[0];
        if(opcode==W25Q_CMD_WREN && !deny_wel) status|=W25Q_SR1_WEL;
        if(opcode==W25Q_CMD_READ4 || opcode==W25Q_CMD_PP4) {
            assert(n==5);
            address=((uint32_t)p[1]<<24)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<8)|p[4];
            assert(address<sizeof(memory));
        }
    } else {
        assert(opcode==W25Q_CMD_PP4 && (status&W25Q_SR1_WEL));
        assert(address+n<=sizeof(memory)); ++pp_count;
        for(unsigned i=0;i<(corrupt_write?n/2:n);++i) memory[address+i]&=p[i];
    }
    return 0;
}
int board_spi1_rx(uint8_t *p, unsigned n) {
    assert(selected);
    if(opcode==W25Q_CMD_RDSR1) {
        assert(n==1); ++polls;
        if(!freeze_time) now_us += tick_us;
        if(status_fail) return -1;
        *p=status;
        if(pp_count && now_us-program_start < program_duration) *p |= W25Q_SR1_BUSY;
    }
    else if(opcode==W25Q_CMD_JEDEC) {assert(n==3); p[0]=0xef;p[1]=0x40;p[2]=0x19;}
    else {
        assert(opcode==W25Q_CMD_READ4 && address+n<=sizeof(memory));
        if(read_fail) return -1;
        memcpy(p,memory+address,n);
    }
    return 0;
}
#include "../tests/flash_time_cases.h"

int main(void) {
    uint8_t data[256], out[256]; memset(memory,0xff,sizeof(memory)); memset(data,0xa5,sizeof(data));
    assert(flash_probe()==0);
    deny_wel=1; status=0;
    assert(flash_page_program(0,data,256)==-1 && pp_count==0);
    deny_wel=0;
    assert(flash_page_program(0,data,256)==0 && pp_count==1);
    assert(flash_read(0,out,256)==0 && memcmp(out,data,256)==0);
    assert(flash_page_program(0,data,256)==0 && pp_count==1); /* response-lost retry */
    data[0]=0;
    assert(flash_page_program(0,data,256)==-1 && pp_count==1); /* existing content */
    corrupt_write=1;
    assert(flash_page_program(256,data,256)==-1 && pp_count==2); /* torn write readback */
    corrupt_write=0;
    assert(flash_page_program(256,data,256)==-1 && pp_count==2); /* never rewrite torn page */
    read_fail=1; assert(flash_read(0,out,256)==-1 && selected==0);
    read_fail=0; status=W25Q_SR1_BUSY;
    assert(flash_read(0,out,256)==-1 && selected==0);
    /* A valid 1ms page program needs 100 ten-us status polls, not 32. */
    memset(memory,0xff,sizeof(memory)); status=0; pp_count=0; polls=0;
    program_duration=1000;
    assert(flash_page_program(0,data,256)==0 && pp_count==1 && polls>32 && selected==0);
    flash_time_cases();
    return 0;
}
