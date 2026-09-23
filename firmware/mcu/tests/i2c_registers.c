#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static uint32_t read_reg(uint32_t a);
static void write_reg(uint32_t a, uint32_t v);
static int get_time(uint32_t *v);
#define BOARD_I2C_READ read_reg
#define BOARD_I2C_WRITE write_reg
#define BOARD_I2C_TIME get_time
#include "../src/board.c"
static uint32_t regs[11], gpio[9], cr, cfgr, trim, en, rst, gpioen, mux;
static unsigned ticks, calls, starts, stops, sent, received, remaining, delay;
static unsigned pulses, scl_low_at, sda_release_after;
static int fault, active, reading, autoend, scl_stuck, sda_stuck, stretch;
static uint8_t tx[2];
static unsigned expected_addr;
static int stop_fault;
static uint32_t *slot(uint32_t a) {
    switch(a) {
    case 0x40021000: return &cr; case 0x40021004: return &trim;
    case 0x40021008: return &cfgr; case RCC_APBENR1_G0: return &en;
    case I2C_RESET: return &rst; case RCC_IOPENR_G0: return &gpioen;
    case I2C_CCIPR: return &mux;
    default:
        if(a>=I2C_GPIO && a<=I2C_GPIO+32 && a%4==0) return &gpio[(a-I2C_GPIO)/4];
        assert(a>=I2C_REG(0) && a<=I2C_REG(40) && a%4==0);
        return &regs[(a-I2C_REG(0))/4];
    }
}
static void progress(void) {
    if (!active || ++delay < 3 || (fault==7 || fault==16)) return;
    if(fault>=1 && fault<=6) {
        const unsigned errors[]={0,16,256,512,1024,4096,2048};
        regs[6] |= errors[fault]; return;
    }
    if(fault==20) { regs[6]|=0x110; return; }
    if(fault==8) cr=0;
    if(fault==9) ++trim;
    if(fault==10) regs[4]^=1;
    if(fault==11) mux |= 0x1000;
    if(fault==12) { regs[6]=32; return; }
    if(remaining) {
        regs[6] |= reading?4:2;
        if(reading) {
            regs[9]=(0xA0u+received)&255;
            if(remaining==1 && autoend && fault!=13) regs[6]=(regs[6]&~0x8000u)|32u;
            if(fault==14 && received==1) regs[6]|=16;
        }
    } else if(autoend) {
        if(fault!=13) regs[6]=32;
    } else if(fault!=15) regs[6]=0x8040;
}
static uint32_t read_reg(uint32_t a) {
    assert(++calls < 1000000);
    if(a==I2C_REG(24)) progress();
    if(a==I2C_GPIO+16) {
        uint32_t value=gpio[5]&0xC0;
        if(scl_stuck || stretch-- > 0) value &= ~I2C_SCL;
        if(sda_stuck && pulses<sda_release_after) value &= ~I2C_SDA;
        return value;
    }
    uint32_t v=*slot(a);
    if(a==I2C_REG(36)) {
        assert(reading && remaining && (regs[6]&4));
        --remaining; ++received; regs[6]&=~4u; delay=0;
    }
    return v;
}
static void write_reg(uint32_t a,uint32_t v) {
    if(a==I2C_RESET && (v&RCC_I2C1EN)) { memset(regs,0,sizeof regs); active=0; }
    if(a==I2C_REG(28)) { regs[6]&=~v; return; }
    if(a==I2C_REG(0) && !v) { active=0; regs[6]=0; }
    if(a==I2C_GPIO+24) {
        uint32_t before=gpio[5];
        gpio[5]=(gpio[5]|(v&65535))&~(v>>16);
        if((before&I2C_SCL) && !(gpio[5]&I2C_SCL)) scl_low_at=ticks;
        if(!(before&I2C_SCL) && (gpio[5]&I2C_SCL)) {
            assert(ticks-scl_low_at>=6); ++pulses;
        }
        return;
    }
    if(a==I2C_REG(4) && (v&I2C_STOP)) {
        assert(!(regs[6]&512)); ++stops;
        if(fault!=16 && stop_fault!=1) regs[6]=stop_fault==2?0x8020:32;
        return;
    }
    if(a==I2C_REG(4) && (v&I2C_START)) {
        assert(regs[0]==1 && (v&0x3FF)==(expected_addr<<1));
        reading=(v&1024)!=0; autoend=(v&I2C_AUTOEND)!=0;
        if(reading) assert(starts==1 && regs[6]&64 && sent==1 && !stops);
        else assert(!active && !starts);
        remaining=(v>>16)&255; assert(remaining); ++starts;
        regs[6]=0x8000; active=1; delay=0;
        v &= ~I2C_START;
    }
    if(a==I2C_REG(40)) {
        assert(!reading && (regs[6]&2) && remaining && sent<2);
        tx[sent++]=(uint8_t)v; --remaining; regs[6]&=~2u; delay=0;
    }
    *slot(a)=v;
    if(a==I2C_REG(4) && !v) active=0;
}
static int get_time(uint32_t *v) {
    if(fault==17) return -1;
    if(fault!=18) ticks+=fault==19?30000:1;
    *v=ticks; return 0;
}
static void fresh(void) {
    memset(regs,0,sizeof regs); memset(gpio,0,sizeof gpio);
    gpio[0]=0x12345678; gpio[1]=0x1234; gpio[2]=0x87654321;
    gpio[3]=0xFFFFFFFF; gpio[5]=0xC0; gpio[8]=0xAABBCCDD;
    cr=0x500; cfgr=0; trim=123; en=0x1234; rst=0x400; gpioen=4; mux=0xFFFFFFFF;
    ticks=calls=starts=stops=sent=received=remaining=delay=pulses=0;
    fault=active=reading=autoend=scl_stuck=sda_stuck=stretch=0;
    sda_release_after=3; expected_addr=0x6A; stop_fault=0; i2c_ready=i2c_active=0;
}
static void initialize(void) {
    board_i2c1_init(); assert(i2c_ready);
    assert(gpio[0]==((0x12345678u&~0xF000u)|0xA000u));
    assert(gpio[1]==(0x1234|0xC0)); assert(gpio[8]==0x66BBCCDD);
    assert(en==(0x1234|RCC_I2C1EN) && rst==0x400 && gpioen==6);
    assert(mux==(0xFFFFFFFFu&~0x3000u));
}
int main(void) {
    uint8_t out[255];
    fresh(); initialize();
    assert(board_i2c1_write_u8(0x6A,0x10,0x55)==0);
    assert(sent==2 && tx[0]==0x10 && tx[1]==0x55 && starts==1);
    for(unsigned n=1;n<=255;n+=(n<14?1:241)) {
        fresh(); initialize(); ticks=UINT32_MAX-2; memset(out,0,sizeof out);
        assert(board_i2c1_read_n(0x6A,0x20,out,n)==0);
        assert(starts==2 && sent==1 && tx[0]==0x20 && received==n);
        for(unsigned i=0;i<n;++i) assert(out[i]==(uint8_t)(0xA0+i));
    }
    for(int f=1;f<=20;++f) {
        fresh(); initialize(); fault=f; memset(out,0x55,sizeof out);
        if(f==18) { /* stalled time must also bound recovery */
            assert(board_i2c1_bus_recover()==-1); continue;
        }
        assert(board_i2c1_read_n(0x6A,0x20,out,3)==-1);
        if(f==1 || f==14) assert(i2c_ready && regs[0]==1);
        else assert(!i2c_ready && regs[0]==0);
        for(unsigned i=0;i<sizeof out;++i) assert(out[i]==0x55);
        if(f==3) assert(stops==0);
    }
    fresh(); initialize(); fault=1;
    assert(board_i2c1_read_n(0x6A,0x0F,out,1)==-1 && i2c_ready);
    fault=0; starts=stops=sent=received=0; expected_addr=0x5C;
    assert(board_i2c1_read_n(0x5C,0x0F,out,1)==0 && out[0]==0xA0);
    for(int f=1;f<=2;++f) {
        fresh(); initialize(); fault=1; stop_fault=f;
        assert(board_i2c1_write_u8(0x6A,0,0)==-1 && !i2c_ready);
    }
    fresh(); initialize(); regs[6]=0x8000; assert(board_i2c1_write_u8(0x6A,0,0)==-1);
    fresh(); initialize(); regs[6]=32; assert(board_i2c1_write_u8(0x6A,0,0)==-1);
    const unsigned addresses[]={0,0x2A,0x5C,0x7F};
    for(unsigned a=0;a<sizeof addresses/sizeof addresses[0];++a) {
        fresh(); initialize(); expected_addr=addresses[a];
        assert(board_i2c1_write_u8((uint8_t)expected_addr,0x10,0x55)==0);
        starts=stops=sent=received=0;
        assert(board_i2c1_read_n((uint8_t)expected_addr,0x20,out,1)==0);
    }
    fresh(); initialize(); unsigned old=calls;
    assert(board_i2c1_read_n(0x80,0,out,1)==-1);
    assert(board_i2c1_read_n(0x6A,0,out,0)==-1);
    assert(board_i2c1_read_n(0x6A,0,out,256)==-1);
    assert(board_i2c1_read_n(0x6A,0,0,1)==-1);
    assert(board_i2c1_write_u8(0x80,0,0)==-1 && calls==old);
    fresh(); sda_stuck=1; stretch=4; initialize(); assert(pulses==4);
    fresh(); sda_stuck=1; sda_release_after=100; assert(board_i2c1_bus_recover()==-1);
    assert(pulses==10 && gpio[5]==0xC0 && !i2c_ready);
    fresh(); scl_stuck=1; assert(board_i2c1_bus_recover()==-1 && !pulses);
    fresh(); fault=17; assert(board_i2c1_bus_recover()==-1);
    fresh(); cr=0; assert(board_i2c1_bus_recover()==-1);
    puts("I2C state model: transactions, atomic output, faults, timed open-drain recovery passed");
    return 0;
}
