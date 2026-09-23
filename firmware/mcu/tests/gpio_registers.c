#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static uint32_t read_reg(uint32_t a);
static void write_reg(uint32_t a, uint32_t v);
static int get_time(uint32_t *v);
#define BOARD_GPIO_READ read_reg
#define BOARD_GPIO_WRITE write_reg
#define BOARD_GPIO_TIME get_time
#include "../src/board.c"
#include "../src/led.c"
static uint32_t ga[11], gb[11], exti[34], en, apben, remap, ticks;
static unsigned calls, writes;
static int fault, release_in_time;
static uint32_t *slot(uint32_t a) {
    if(a==RCC_IOPENR_G0) return &en;
    if(a==RCC_APBENR2_G0) return &apben;
    if(a==GPIO_SYSCFG) return &remap;
    if(a>=GPIO_A && a<=GPIO_A+40 && a%4==0) return &ga[(a-GPIO_A)/4];
    if(a>=GPIO_B && a<=GPIO_B+40 && a%4==0) return &gb[(a-GPIO_B)/4];
    assert(a>=EXTI_BASE_G0 && a<=EXTI_BASE_G0+0x84 && a%4==0);
    return &exti[(a-EXTI_BASE_G0)/4];
}
static uint32_t read_reg(uint32_t a) { assert(++calls<100000); return *slot(a); }
static void write_reg(uint32_t a,uint32_t v) {
    ++writes;
    if(fault==5 && a==GPIO_B+24 && v==1u) return;
    if(fault==6 && a==GPIO_B+24 && v==(1u<<16)) return;
    if(fault==1 && a==RCC_IOPENR_G0) return;
    if(fault==2 && a==GPIO_SYSCFG) return;
    if(fault==3 && a==GPIO_A) return;
    if(a==GPIO_SYSCFG) assert(apben&1);
    if(a==GPIO_A || a==GPIO_B) {
        uint32_t old=*slot(a);
        if(a==GPIO_A && (old&(3u<<8))!=(1u<<8) && (v&(3u<<8))==(1u<<8)) assert(ga[5]&16);
        if(a==GPIO_B && (old&3)!=1 && (v&3)==1) assert(!(gb[5]&1));
        if(a==GPIO_A && ((old^v)&GPIO_INPUT_MODES)) assert((remap&GPIO_REMAP)==GPIO_REMAP);
    }
    if(a==GPIO_A+24 || a==GPIO_B+24) {
        uint32_t *odr=a==GPIO_A+24?&ga[5]:&gb[5];
        *odr=(*odr | (v&0xFFFF)) & ~(v>>16); return;
    }
    if(a==EXTI_BASE_G0+12 || a==EXTI_BASE_G0+16) { *slot(a)&=~v; return; }
    *slot(a)=v;
}
static int get_time(uint32_t *v) {
    if(fault==4) return -1;
    if(release_in_time) { ga[4]|=GPIO_REED; exti[3]|=GPIO_REED; }
    *v=ticks; return 0;
}
static void fresh(int f) {
    for(unsigned i=0;i<11;++i) {ga[i]=0xAA55FFFF;gb[i]=0x55AAAAFF;}
    memset(exti,0xFF,sizeof exti); en=0x40;apben=0x100;remap=0x100;
    ticks=10;calls=writes=0;fault=f;release_in_time=0;
    gpio_ready=reed_edges_ready=reed_tracking=0;
}
static void init(void) {board_enable_syscfg();board_apply_pa9_pa10_remap();board_init_gpio();board_reed_exti_setup();}
static void close_reed(void) {ga[4]&=~GPIO_REED;}
int main(void) {
    fresh(0); unsigned w=writes;board_apply_pa9_pa10_remap();assert(writes==w);
    board_init_gpio();assert(!board_reed_is_closed() && !board_imu_int_pending());
    fresh(0);init();
    assert((ga[5]&16) && !(gb[5]&1));
    assert(ga[0]==((0xAA55FFFFu&~(GPIO_INPUT_MODES|(3u<<8)))|(1u<<8)));
    assert(gb[0]==((0x55AAAAFFu&~3u)|1));
    assert(ga[1]==(0xAA55FFFFu&~16u) && gb[1]==(0x55AAAAFFu&~1u));
    assert(ga[2]==(0xAA55FFFFu&~(3u<<8)) && gb[2]==(0x55AAAAFFu&~3u));
    assert(ga[3]==(0xAA55FFFFu&~(GPIO_INPUT_MODES|(3u<<8))) && gb[3]==(0x55AAAAFFu&~3u));
    assert(en==0x43 && apben==0x101 && remap==0x118);
    assert(exti[26]==(UINT32_MAX&~0x700u) && exti[32]==(UINT32_MAX&~GPIO_REED));
    assert(exti[33]==(UINT32_MAX&~GPIO_REED) && exti[3]==(UINT32_MAX&~GPIO_REED));
    assert(exti[4]==(UINT32_MAX&~GPIO_REED) && exti[0]==UINT32_MAX);
    assert(!board_reed_is_closed()); close_reed();assert(board_reed_is_closed());
    ga[4]&=~1u;assert(!board_imu_int_pending());ga[4]|=1;assert(board_imu_int_pending());
    assert(!board_reed_held_for_sleep());ticks+=1499999;assert(!board_reed_held_for_sleep());
    ++ticks;assert(board_reed_held_for_sleep());
    exti[3]|=GPIO_REED; ++ticks;assert(!board_reed_held_for_sleep());
    ++ticks;assert(!board_reed_held_for_sleep());
    ticks+=1500000;assert(board_reed_held_for_sleep());
    ga[4]|=GPIO_REED;assert(!board_reed_is_closed());close_reed();++ticks;assert(!board_reed_held_for_sleep());
    ticks+=1500000;release_in_time=1;assert(!board_reed_held_for_sleep());
    for(int f=1;f<=3;++f) {fresh(f);init();close_reed();assert(!board_reed_is_closed()&&!board_reed_held_for_sleep());}
    fresh(0);init();close_reed();ticks=UINT32_MAX-999999;assert(!board_reed_held_for_sleep());
    ticks+=1500000;assert(board_reed_held_for_sleep());
    for(unsigned i=0;i<8;++i) {ticks+=1000000000;assert(board_reed_held_for_sleep());}
    fault=4;++ticks;assert(!board_reed_held_for_sleep());fault=0;++ticks;assert(!board_reed_held_for_sleep());
    ticks+=1500000;assert(board_reed_held_for_sleep());assert(!board_reed_held_for_sleep()); /* stalled */
    ++ticks;assert(!board_reed_held_for_sleep());--ticks;assert(!board_reed_held_for_sleep()); /* reversed */
    for(unsigned k=0;k<7;++k) {
        fresh(0);init();close_reed();assert(!board_reed_held_for_sleep());ticks+=1500000;
        if(k==0) en=0;if(k==1) remap=0;if(k==2) ga[0]|=3u<<18;
        if(k==3) exti[0]&=~GPIO_REED;if(k==4) exti[26]|=1u<<8;
        if(k==5) exti[32]|=GPIO_REED;if(k==6) ga[3]|=1u<<18;
        assert(!board_reed_held_for_sleep());
    }
    fresh(0);init();led_init();assert(!led_output_failed() && !(gb[5]&1));
    uint32_t start=UINT32_MAX-100000u;
    led_request_bite_flash(start);
    for(unsigned j=0;j<40;++j) {
        led_poll(start+j*50000u);
        unsigned expected=SMART_APO_VARIANT==SMART_APO_VARIANT_AWA && !(j&1u);
        assert((gb[5]&1u)==expected);
    }
    led_poll(start+2000000u);assert(!(gb[5]&1) && !led_output_failed());
    led_request_bite_flash(3000000);led_poll(3000000);led_cancel();assert(!(gb[5]&1));
    if(SMART_APO_VARIANT==SMART_APO_VARIANT_AWA) {
        led_request_bite_flash(4000000);fault=5;led_poll(4000000);
        assert(led_output_failed() && !(gb[5]&1));
        fault=0;led_request_bite_flash(5000000);led_poll(5000000);assert(!(gb[5]&1));
        led_init();led_request_bite_flash(6000000);led_poll(6000000);assert(gb[5]&1);
        fault=6;led_cancel();assert(led_output_failed() && (gb[5]&1));
        fault=0;led_init();assert(!(gb[5]&1));
        gb[0]&=~3u;led_request_bite_flash(7000000);led_poll(7000000);
        assert(led_output_failed());
    }
    puts("GPIO model: latch-before-mode/remap order, preservation, IDR, release edges, 1.5s/wrap, configuration/write/time faults passed");
    return 0;
}
