/* Delayed TDR/shift-register model, not proof of real wire timing. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static uint32_t rcc[32], gpio[16], regs[16];
static uint8_t sent[128];
static unsigned writes, completed, polls, delay, ack_delay, fail_after;
static int fault, tdr_pending;
static uint32_t *regptr(uint32_t a)
{
    assert((a & 3u) == 0);
    if (a >= 0x40021000u && a < 0x40021080u) return &rcc[(a-0x40021000u)/4];
    if (a >= 0x50000000u && a < 0x50000040u) return &gpio[(a-0x50000000u)/4];
    assert(a >= 0x40004400u && a < 0x40004440u);
    return &regs[(a-0x40004400u)/4];
}
static uint32_t read32(uint32_t a)
{
    if (a == 0x4000441Cu) {
        uint32_t status = 0;
        ++polls;
        if (regs[0] == 9u) {
            if (ack_delay) --ack_delay;
            else status |= 1u << 21;
            if (delay && --delay == 0) ++completed;
            if (!delay && tdr_pending) { tdr_pending=0; delay=5; }
            if (!tdr_pending) status |= 0x80u;
            if (!delay && !tdr_pending) status |= 0x40u;
        }
        if (writes >= fail_after) {
            if (fault == 1) status &= ~0x80u;
            if (fault == 2) status &= ~0x40u;
            if (fault >= 3 && fault <= 6) status |= 1u << (fault-3);
            if (fault == 7) status &= ~(1u << 21);
            if (fault == 8) rcc[2] = 1u;
            if (fault == 9) rcc[1] ^= 1u;
        }
        regs[7] = status;
    }
    return *regptr(a);
}
static void write32(uint32_t a, uint32_t v)
{
    if (a == 0x4002102Cu && (v & (1u << 17))) {
        memset(regs,0,sizeof regs); delay=ack_delay=0; tdr_pending=0;
    }
    if (a == 0x40004400u) {
        if (v == 9u) {
            assert(regs[3] == 139u && regs[11] == 0u);
            assert((gpio[0] & 0xF0u) == 0xA0u);
            assert((gpio[8] & 0xFF00u) == 0x1100u);
            ack_delay=3;
        } else { delay=0; tdr_pending=0; } /* UE clear discards pending data. */
    }
    if (a == 0x40004428u) {
        assert(regs[0] == 9u && (regs[7] & 0x80u));
        assert(writes < sizeof sent && v <= 255u);
        sent[writes++]=(uint8_t)v;
        assert(!tdr_pending);
        tdr_pending=1;
        regs[7] &= ~0xC0u; /* TDR write clears TC/TXE. */
    }
    *regptr(a)=v;
}
#define BOARD_UART_READ(a) read32(a)
#define BOARD_UART_WRITE(a,v) write32(a,v)
#include "../src/board.c"
static void reset(void)
{
    memset(rcc,0,sizeof rcc); memset(gpio,0,sizeof gpio); memset(regs,0,sizeof regs);
    rcc[0]=0x500u; rcc[1]=0x4000u;
    writes=completed=polls=delay=ack_delay=fail_after=0; fault=tdr_pending=0; uart_ready=0;
}
static void begin(void) { reset(); board_usart2_init(); assert(uart_ready); polls=0; }
static void failed(void)
{
    unsigned before=polls;
    assert(!uart_ready && regs[0]==0);
    assert(board_usart2_write((const uint8_t *)"x",1)==-1 && polls==before);
    assert(polls < USART_XFER_POLL_MAX + 40u);
}
int main(void)
{
    unsigned i; const uint8_t tx[]={0xA5,0x5A,0,0xFF,0x80};
    /* Uninitialized API must avoid MMIO entirely (reg model has no calls). */
    assert(board_usart2_write(tx,1)==-1 && polls==0);
    reset(); gpio[0]=0xABCD1234u; gpio[1]=0x87654321u;
    gpio[2]=0x98761234u; gpio[3]=0x12345678u; gpio[8]=0xABCDEF12u;
    rcc[13]=0x40u; rcc[15]=0x80u; rcc[11]=0x20u;
    board_usart2_init(); assert(uart_ready);
    assert(gpio[0]==((0xABCD1234u & ~0xF0u)|0xA0u));
    assert(gpio[1]==(0x87654321u & ~0xCu));
    assert(gpio[2]==(0x98761234u & ~0xF0u));
    assert(gpio[3]==(0x12345678u & ~0xF0u));
    assert(gpio[8]==((0xABCDEF12u & ~0xFF00u)|0x1100u));
    assert(rcc[13]==0x41u && rcc[15]==0x20080u && rcc[11]==0x20u);
    assert(board_usart2_write(tx,sizeof tx)==0);
    assert(writes==sizeof tx && completed==writes && !memcmp(tx,sent,sizeof tx));
    assert(board_usart2_write(NULL,0)==0);
    for(i=0;i<5;++i) {
        reset(); if(i==0) rcc[0]=0x100; if(i==1) rcc[0]|=0x800;
        if(i==2) rcc[2]=1; if(i==3) rcc[2]=0x100; if(i==4) rcc[2]=0x1000;
        board_usart2_init(); assert(!uart_ready && !writes && regs[0]==0);
    }
    for(i=1;i<=9;++i) {
        begin(); fault=(int)i;
        assert(board_usart2_write(tx,1)==-1); failed();
        fault=0; rcc[2]=0; board_usart2_init(); assert(uart_ready);
    }
    reset(); fault=7; board_usart2_init(); failed(); /* missing TEACK */
    begin(); fault=1; fail_after=2;
    assert(board_usart2_write(tx,sizeof tx)==-1 && writes==2);
    assert(!memcmp(tx,sent,2)); failed();
    begin(); fault=2; assert(board_usart2_write(tx,sizeof tx)==-1);
    assert(writes==sizeof tx && completed==writes); failed(); /* entire frame possible */
    begin(); assert(board_usart2_write(NULL,1)==-1 && !writes); failed();
    for(i=0;i<10;++i) {
        begin();
        if(i==0) regs[0]^=4; if(i==1) regs[1]=1; if(i==2) regs[2]=1;
        if(i==3) regs[3]=1; if(i==4) regs[11]=1; if(i==5) gpio[0]^=0x10;
        if(i==6) gpio[8]^=0x100; if(i==7) rcc[13]&=~1u;
        if(i==8) rcc[15]&=~0x20000u; if(i==9) rcc[11]|=0x20000u;
        assert(board_usart2_write(tx,1)==-1 && !writes && !uart_ready);
    }
    begin(); board_usart2_init(); assert(uart_ready && !writes);
    puts("UART model: reset, pin isolation, TEACK, delayed TXE/TC, partial/full failure, clock/config faults passed");
    return 0;
}
