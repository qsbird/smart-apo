/* Deterministic FIFO/status model: not a board or analogue bus simulation. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static uint32_t rcc[32], gpio[16], regs[16];
static unsigned writes, reads, polls, failure_after, shifting, tail;
static int fault, pending, cs_high, saw_cs_before_enable, dr_then_sr;
static uint8_t sent[64];
static uint32_t *regptr(uint32_t a)
{
    if (a >= 0x40021000u && a < 0x40021080u) return &rcc[(a-0x40021000u)/4];
    if (a >= 0x50000000u && a < 0x50000040u) return &gpio[(a-0x50000000u)/4];
    assert(a >= 0x40013000u && a < 0x40013040u);
    return &regs[(a-0x40013000u)/4];
}
static uint32_t read32(uint32_t a)
{
    assert(a != 0x4001300Cu); /* forbid packed/wide DR accesses */
    if (a == 0x40013008u) {
        uint32_t sr = 2u | (pending ? 1u : 0u);
        if (shifting) { --shifting; sr = 0x80u; }
        else if (tail) { --tail; sr |= 0x80u; }
        ++polls;
        if (writes >= failure_after) {
            if (fault == 1) sr &= ~2u;
            if (fault == 2) sr &= ~1u;
            if (fault == 3) sr |= 0x80u;
            if (fault == 4) sr |= 0x40u;
            if (fault == 5) { sr |= 0x20u; regs[0] &= ~0x44u; }
            if (fault == 6) sr |= 0x100u;
        }
        if (dr_then_sr == 1) dr_then_sr = 2;
        return sr;
    }
    return *regptr(a);
}
static void write32(uint32_t a, uint32_t v)
{
    assert(a != 0x4001300Cu);
    if (a == 0x50000018u) {
        if (v & 0x10u) cs_high=1;
        if (v & 0x100000u) cs_high=0;
    }
    if (a == 0x40021030u && (v & 0x1000u)) { memset(regs, 0, sizeof regs); pending=0; shifting=tail=0; }
    if (a == 0x40013000u && (v & 0x40u)) {
        assert(cs_high); saw_cs_before_enable=1;
    }
    *regptr(a)=v;
}
static uint8_t read8(uint32_t a)
{
    assert(a == 0x4001300Cu); ++reads; pending=0; dr_then_sr=1; tail=2;
    return (uint8_t)(0xA0u + writes);
}
static void write8(uint32_t a, uint8_t v)
{
    assert(a == 0x4001300Cu && !cs_high && !pending && writes < sizeof sent);
    assert(regs[1] == 0x1700u && (regs[0] & 0x40u));
    sent[writes++] = v; pending=1; shifting=2;
}
#define BOARD_SPI_READ(a) read32(a)
#define BOARD_SPI_WRITE(a,v) write32(a,v)
#define BOARD_SPI_READ8(a) read8(a)
#define BOARD_SPI_WRITE8(a,v) write8(a,v)
#include "../src/board.c"
static void reset(void)
{
    memset(rcc,0,sizeof rcc); memset(gpio,0,sizeof gpio); memset(regs,0,sizeof regs);
    rcc[0]=0x500u; rcc[1]=0x4000u;
    writes=reads=polls=failure_after=shifting=tail=0; fault=pending=cs_high=saw_cs_before_enable=dr_then_sr=0;
    spi_ready=spi_gpio_ready=spi_selected=0;
}
static void begin(void) { reset(); board_spi1_init(); assert(spi_ready && cs_high); assert(board_spi1_cs(1)==0); }
static void failed(void)
{
    assert(cs_high && !spi_ready && !spi_selected);
    assert(board_spi1_cs(1)==-1 && cs_high);
    assert(polls < SPI_XFER_POLL_MAX + 32u);
}
int main(void)
{
    unsigned i; uint8_t out[3], tx[]={0x9Fu, 0x00u, 0xFFu};
    reset(); assert(board_spi1_tx(tx,1)==-1 && !writes);
    reset(); gpio[0]=0xABCD1234u; gpio[1]=0x87654321u; gpio[2]=0x98761234u;
    gpio[3]=0x12345678u; gpio[8]=0xABCDEF12u; rcc[13]=0x40u; rcc[16]=0x80u; rcc[12]=0x20u;
    board_spi1_init(); assert(spi_ready && saw_cs_before_enable);
    assert(gpio[0]==((0xABCD1234u & ~0xFF00u)|0xA900u));
    assert(gpio[1]==(0x87654321u & ~0xF0u));
    assert(gpio[2]==(0x98761234u & ~0xFF00u));
    assert(gpio[3]==(0x12345678u & ~0xFF00u));
    assert(gpio[8]==(0xABCDEF12u & ~0xFFF00000u));
    assert(rcc[13]==0x41u && rcc[16]==0x1080u && rcc[12]==0x20u);
    assert(regs[0]==0x35Cu && regs[1]==0x1700u);
    assert(board_spi1_cs(1)==0 && !cs_high);
    assert(board_spi1_tx(tx,3)==0 && reads==3 && !memcmp(tx,sent,3));
    assert(board_spi1_rx(out,3)==0 && out[0]==0xA4u && out[2]==0xA6u);
    assert(sent[3]==0xFFu && sent[5]==0xFFu && !pending);
    assert(board_spi1_tx(0,0)==0 && board_spi1_rx(0,0)==0);
    assert(board_spi1_cs(0)==0 && cs_high);
    for(i=0;i<5;++i) {
        reset(); if(i==0) rcc[0]=0x100u; if(i==1) rcc[0]|=0x800u;
        if(i==2) rcc[2]=1u; if(i==3) rcc[2]=0x100u; if(i==4) rcc[2]=0x1000u;
        board_spi1_init(); assert(!spi_ready && cs_high && !(regs[0]&0x40u));
    }
    for(i=1;i<=6;++i) {
        begin(); fault=(int)i; failure_after=0;
        assert(board_spi1_tx(tx,1)==-1); failed();
        if(i==4 || i==5) assert(dr_then_sr==2 && !(regs[0]&0x40u));
        fault=0; board_spi1_init(); assert(spi_ready && cs_high);
    }
    begin(); memset(out,0xCC,sizeof out); fault=2; failure_after=2;
    assert(board_spi1_rx(out,3)==-1); failed();
    assert(out[0]==0xA1 && out[1]==0xCC && out[2]==0xCC && writes==2);
    begin(); assert(board_spi1_tx(0,1)==-1); failed();
    begin(); assert(board_spi1_rx(0,1)==-1); failed();
    begin(); rcc[2]=1; assert(board_spi1_tx(tx,1)==-1); failed();
    begin(); regs[1]=0; assert(board_spi1_tx(tx,1)==-1); failed();
    begin(); rcc[1]^=1; assert(board_spi1_cs(0)==-1); failed();
    begin(); board_spi1_init(); assert(spi_ready && cs_high && !spi_selected);
    puts("SPI model: init, isolation, byte FIFO, CS, clock checks, bounded faults, partial RX passed");
    return 0;
}
