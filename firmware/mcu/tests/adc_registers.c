#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static uint32_t read_reg(uint32_t a);
static void write_reg(uint32_t a, uint32_t v);
static int get_time(uint32_t *v);
#define BOARD_ADC_READ read_reg
#define BOARD_ADC_WRITE write_reg
#define BOARD_ADC_TIME get_time
#include "../src/board.c"
static uint32_t adc[17], cr, cfgr, trim, en, reset, gpioen, mode, pulls;
static unsigned ticks, calls, calibrations, starts, dr_reads, phase, delay;
static uint32_t sample, regulator_at, calibrated_at;
static int fault;
static uint32_t *slot(uint32_t a) {
    switch(a) {
    case 0x40021000: return &cr; case 0x40021004: return &trim;
    case 0x40021008: return &cfgr; case RCC_APBENR2_G0: return &en;
    case ADC_RCC_RESET: return &reset; case RCC_IOPENR_G0: return &gpioen;
    case 0x50000000: return &mode; case 0x5000000C: return &pulls;
    default: assert(a >= ADC_REG(0) && a <= ADC_REG(64) && a % 4 == 0);
        return &adc[(a - ADC_REG(0))/4];
    }
}
static uint32_t read_reg(uint32_t a) {
    assert(++calls < 200000);
    if (phase && ++delay == 3) {
        if (phase == 1 && fault != 1) { adc[2] &= ~0x80000000u; if(fault!=13) adc[0] |= 0x800u; calibrated_at=ticks; }
        if (phase == 2 && fault != 2) adc[0] |= 1u;
        if (phase == 3 && fault != 3) {
            adc[0] |= 12u; adc[2] &= ~4u; adc[16]=sample;
            if(fault==4) adc[0] |= 16u;
            if(fault==5) cr=0;
            if(fault==6) adc[3]=32;
            if(fault==7) ++trim;
            if(fault==12) adc[2] |= 4u;
            if(fault==14) adc[0] &= ~8u;
            if(fault==15) adc[2] |= 16u;
        }
    }
    uint32_t v=*slot(a);
    if(a == ADC_REG(64)) { ++dr_reads; adc[0] &= ~4u; }
    return v;
}
static void write_reg(uint32_t a,uint32_t v) {
    if(a == ADC_RCC_RESET && (v & ADC_RCC_BIT)) { memset(adc,0,sizeof adc); phase=0; }
    if(a == ADC_REG(0)) { adc[0] &= ~v; return; }
    if(a == ADC_REG(40) && fault!=8) adc[0] |= 0x2000;
    if(a == ADC_REG(8)) {
        if(v == ADC_REGULATOR) regulator_at=ticks;
        if(v & 0x80000000u) {
            assert(ticks-regulator_at >= 30); assert(!(adc[2]&1));
            ++calibrations; phase=1; delay=0;
        } else if(v & 4) {
            assert(calibrations && (adc[0]&1)); ++starts; phase=3; delay=0;
        } else if(v & 1) {
            assert(ticks-calibrated_at >= 2); phase=2; delay=0;
        }
    }
    *slot(a)=v;
}
static int get_time(uint32_t *v) {
    if(fault==9) return -1;
    if(fault!=10) ++ticks;
    *v=ticks;
    return 0;
}
static void fresh(int f) {
    memset(adc,0,sizeof adc); cr=0x500; cfgr=0; trim=123; en=0x1234;
    reset=0x400; gpioen=4; mode=0xAA55AA55; pulls=0x55AA55AA;
    ticks=VBAT_STARTUP_SETTLE_US; adc_input_settled=0;
    calls=calibrations=starts=dr_reads=phase=delay=0;
    fault=f; sample=f==11?4096:2048;
}
int main(void) {
    uint16_t out;
    /* Independent physical-divider oracle: every ADC code, plus clamp. */
    for (unsigned code=0; code<=4095; ++code) {
        uint16_t expected=(uint16_t)(((uint64_t)code*3300u*240400u)/(60400u*4095u));
        assert(board_vbat_mv_from_adc(code)==expected);
    }
    assert(board_vbat_mv_from_adc(4095)==13134u);
    assert(board_vbat_mv_from_adc(4096)==13134u);
    assert(board_vbat_mv_from_adc(UINT32_MAX)==13134u);
    fresh(0); assert(board_adc_read_vbat(0)==-1); assert(calls==0);
    fresh(0); ticks=0; out=0xA55A;
    assert(board_adc_read_vbat(&out)==-1 && out==0xA55A);
    assert(calibrations==0 && starts==0 && !adc_input_settled);
    ticks=VBAT_STARTUP_SETTLE_US-2u;
    assert(board_adc_read_vbat(&out)==-1 && out==0xA55A);
    assert(calibrations==0 && starts==0);
    ticks=VBAT_STARTUP_SETTLE_US-1u;
    assert(board_adc_read_vbat(&out)==0 && out==sample && adc_input_settled);
    ticks=1u; /* A later 32-bit timer wrap does not restart the boot guard. */
    assert(board_adc_read_vbat(&out)==0);

    for(unsigned s=0;s<=4095;s+=1365) {
        fresh(0); sample=s; out=0xA55A;
        assert(board_adc_read_vbat(&out)==0 && out==s);
        assert(calibrations==1 && starts==1 && dr_reads==1 && adc[2]==0);
        assert(mode==((0xAA55AA55u&~12u)|12u)); assert(pulls==(0x55AA55AAu&~12u));
        assert(en==(0x1234|ADC_RCC_BIT) && reset==0x400 && gpioen==5);
        assert(board_adc_read_vbat(&out)==0 && calibrations==2);
    }
    fresh(0); ticks=UINT32_MAX-10u; assert(board_adc_read_vbat(&out)==0);
    for(int f=1;f<=15;++f) {
        fresh(f); out=0xA55A;
        assert(board_adc_read_vbat(&out)==-1 && out==0xA55A);
        assert(adc[2]==0);
        fault=0; cr=0x500; sample=123;
        assert(board_adc_read_vbat(&out)==0 && out==123);
    }
    for(unsigned k=0;k<5;++k) {
        fresh(0); if(k==0) cr=0; if(k==1) cr|=0x800;
        if(k==2) cfgr=1; if(k==3) cfgr=0x100; if(k==4) cfgr=0x1000;
        out=1234; assert(board_adc_read_vbat(&out)==-1 && out==1234 && !starts);
    }
    puts("ADC model: both endpoints, sequence/calibration/delays, GPIO preservation, 15 injected faults, clock rejection passed");
    return 0;
}
