/* Deterministic register model, not oscillator or crystal qualification. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static uint32_t rcc[32], tim[32], pwr;
static unsigned reads, writes, bd_writes, ready_after, polls;
static int counting, fault;
static volatile uint32_t *time_reg(uint32_t a) {
    if (a >= 0x40021000u && a < 0x40021080u) return &rcc[(a-0x40021000u)/4];
    assert(a >= 0x40000000u && a < 0x40000080u);
    if (a == 0x40000024u && counting && tim[0] == 1) tim[9] += 10000;
    return &tim[(a-0x40000000u)/4];
}
static uint32_t lse_read(uint32_t a);
static void lse_write(uint32_t a, uint32_t v);
#define BOARD_TIME_REG(a) (*time_reg(a))
#define BOARD_LSE_READ lse_read
#define BOARD_LSE_WRITE lse_write
#include "../src/board.c"
static uint32_t *slot(uint32_t a) {
    if (a == LSE_PWR_CR1) return &pwr;
    assert(a == LSE_BDCR || a == RCC_APBENR1_G0);
    return &rcc[(a-0x40021000u)/4];
}
static uint32_t lse_read(uint32_t a) {
    assert(++reads < 1000);
    if (a == LSE_BDCR && (rcc[23]&1) && ++polls == ready_after) rcc[23] |= 2;
    if (fault == 4 && bd_writes) counting = 0;
    if (fault == 5 && bd_writes) rcc[0] = 0;
    if (fault == 6 && bd_writes) rcc[23] |= 4;
    if (fault == 7 && bd_writes) rcc[23] |= 64;
    return *slot(a);
}
static void lse_write(uint32_t a, uint32_t v) {
    ++writes;
    if (a == RCC_APBENR1_G0 && fault == 1) return;
    if (a == LSE_PWR_CR1 && fault == 2) return;
    if (a == LSE_BDCR) {
        assert((rcc[15]&LSE_PWREN) && (pwr&LSE_DBP));
        assert((v & ~1u) == (rcc[23] & ~1u)); /* no RTC/drive/reset edits */
        ++bd_writes;
        if (fault == 3) return;
    }
    *slot(a) = v;
}
static void reset_model(void) {
    memset(rcc,0,sizeof rcc); memset(tim,0,sizeof tim);
    rcc[0]=0x500; rcc[1]=0x4000; rcc[15]=0x20000;
    rcc[23]=0x03008318; /* RTC, LSCO, high drive: all must survive */
    pwr=0x600; reads=writes=bd_writes=polls=0; ready_after=4;
    counting=1; fault=0; time_ready=time_attempted=0; time_last=time_trim=0;
}
int main(void) {
    uint32_t original, epoch; unsigned i;
    reset_model(); original=rcc[23];
    assert(board_start_clocks()==1 && time_ready);
    assert(rcc[23]==(original|3) && rcc[15]==0x20001 && pwr==0x600);
    epoch=tim[9]; original=writes;
    assert(board_start_clocks()==1 && tim[9]>epoch && writes==original);
    reset_model(); rcc[23]|=3; assert(board_start_clocks()==1 && writes==0);
    reset_model(); rcc[23]|=1; assert(board_start_clocks()==1);
    reset_model(); rcc[15]|=LSE_PWREN; pwr|=LSE_DBP;
    assert(board_start_clocks()==1 && (pwr&LSE_DBP) && (rcc[15]&LSE_PWREN));
    for (i=0;i<4;++i) {
        reset_model(); rcc[23]|=i==0?4:i==1?64:i==2?0x10000:2;
        original=rcc[23]; assert(board_start_clocks()==0 && writes==0 && rcc[23]==original);
    }
    reset_model(); rcc[0]=0; assert(board_start_clocks()==0 && reads==0 && writes==0);
    reset_model(); counting=0; assert(board_start_clocks()==0 && reads==0 && writes==0);
    reset_model(); ready_after=0; assert(board_start_clocks()==0 && time_ready);
    assert(tim[9]>=LSE_STARTUP_TIMEOUT_US && tim[9]<LSE_STARTUP_TIMEOUT_US+100000);
    assert((rcc[23]&1) && pwr==0x600 && rcc[15]==0x20001);
    for(i=1;i<=7;++i) {
        reset_model(); fault=(int)i; assert(board_start_clocks()==0);
        assert(pwr==0x600 && rcc[15]==0x20001);
        if(i<=2) assert(bd_writes==0);
    }
    reset_model(); time_start(); tim[9]=0xffff0000; time_last=tim[9];
    assert(board_start_clocks()==1 && tim[9]<0xffff0000); /* deadline wraps */
    puts("LSE model: TIM2, ready, timeout, bypass, CSS, DBP, protection, preserve, wrap passed");
}
