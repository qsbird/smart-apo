#include "sensors.h"
#include "datalog.h"
#include <assert.h>
#include <string.h>

int board_i2c1_write_u8(uint8_t a,uint8_t r,uint8_t v) {(void)a;(void)r;(void)v;return 0;}
int board_i2c1_read_n(uint8_t a,uint8_t r,uint8_t *p,unsigned n) {
    memset(p,0,n);
    if(a==I2C_ADDR_LSM6DSO_SA0_GND && r==LSM6DSO_WHO_AM_I_REG) *p=LSM6DSO_WHO_AM_I_VAL;
    if(a==I2C_ADDR_LPS28DFW && r==LPS28DFW_WHOAMI_REG) *p=LPS28DFW_WHOAMI_VAL;
    if(a==I2C_ADDR_NAU7802 && r==NAU7802_PU_CTRL) *p=NAU7802_PU_PUR|NAU7802_PU_CR;
    return 0;
}
int board_adc_read_vbat(uint16_t *p) {*p=1000;return 0;}
uint16_t board_vbat_mv_from_adc(unsigned n) {return (uint16_t)n;}

int main(void) {
    sensors_status_t st; smart_apo_sample_t s; sensors_timing_stats_t stats;
    const unsigned hz=SMART_APO_VARIANT==SMART_APO_VARIANT_UW ? 208u:104u;
    const unsigned phz=SMART_APO_VARIANT==SMART_APO_VARIANT_UW ? 100u:50u;
    unsigned imu=0,press=0,strain=0,batt=0;
    uint32_t start=UINT32_MAX-999u;
    sensors_init(&st);
    /* Three hours at 1 ms polling, crossing the microsecond counter twice.
     * Includes the initial sample and exact endpoint, hence +1 samples. */
    for(uint64_t elapsed=0;elapsed<=10800000000ULL;elapsed+=1000u) {
        uint32_t now=start+(uint32_t)elapsed;
        assert(sensors_poll(now,&s,&st)>=0);
        assert(s.timestamp_us==now);
        imu+=(s.flags&SAMPLE_FLAG_IMU_OK)!=0;
        press+=(s.flags&SAMPLE_FLAG_PRESS_OK)!=0;
        strain+=(s.flags&SAMPLE_FLAG_STRAIN_OK)!=0;
        batt+=s.battery_mv!=0;
        assert(sensors_poll(now,&s,&st)==0); /* repeated timestamp is idle */
    }
    assert(imu==10800u*hz+1u && press==10800u*phz+1u && batt==10801u);
    assert(strain==(SMART_APO_VARIANT==SMART_APO_VARIANT_UW ? 10800u*320u+1u:0u));
    sensors_timing_stats(&stats);
    for(unsigned i=0;i<4;++i) assert(stats.skipped_slots[i]==0);
    sensors_init(&st); assert(sensors_poll(start,&s,&st)==1);
    assert(sensors_poll(start+1000000u,&s,&st)==1);
    sensors_timing_stats(&stats);
    assert(stats.skipped_slots[0]==hz-1u && stats.skipped_slots[1]==phz-1u);
    assert(stats.skipped_slots[2]==(SMART_APO_VARIANT==SMART_APO_VARIANT_UW ? 319u:0u));
    assert(stats.skipped_slots[3]==0);
    assert(sensors_poll(start+1000000u,&s,&st)==0); /* no catch-up burst */
    assert(sensors_poll(start+1000000u+(1000000u+hz-1u)/hz,&s,&st)==1);
    assert(s.flags&SAMPLE_FLAG_IMU_OK); /* phase retained after overrun */
    assert(sensors_poll(start,&s,&st)==-1); /* backward clock */
    assert(s.flags==0);
    assert(sensors_poll(start+2000000u,&s,&st)==-1); /* fault latches */
    sensors_init(&st); assert(sensors_poll(42,&s,&st)==1);
    assert(sensors_poll(42u+0x80000000u,&s,&st)==-1); /* ambiguous long gap */
    return 0;
}
