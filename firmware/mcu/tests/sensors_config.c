#include "sensors.h"
#include "datalog.h"
#include <assert.h>
#include <string.h>
static unsigned nau_writes, bdu, cal_requested, ready, cal_error, cal_busy, pur_missing, fail_write;
int board_i2c1_write_u8(uint8_t a, uint8_t r, uint8_t v) {
    if(fail_write) return -1;
    if(a==I2C_ADDR_LSM6DSO_SA0_GND && r==LSM6DSO_CTRL3_C) bdu=v;
    if(a==I2C_ADDR_NAU7802) {
        ++nau_writes;
        if(r==NAU7802_CTRL2 && (v&NAU7802_CTRL2_CALS)) cal_requested=1;
    }
    return 0;
}
int board_i2c1_read_n(uint8_t a, uint8_t r, uint8_t *p, unsigned n) {
    memset(p,0,n);
    if(a==I2C_ADDR_LSM6DSO_SA0_GND && r==LSM6DSO_WHO_AM_I_REG) *p=LSM6DSO_WHO_AM_I_VAL;
    if(a==I2C_ADDR_LPS28DFW && r==LPS28DFW_WHOAMI_REG) *p=LPS28DFW_WHOAMI_VAL;
    if(a==I2C_ADDR_NAU7802 && r==NAU7802_PU_CTRL)
        *p=(pur_missing?0:NAU7802_PU_PUR)|(ready?NAU7802_PU_CR:0);
    if(a==I2C_ADDR_NAU7802 && r==NAU7802_CTRL2)
        *p=(cal_error?NAU7802_CTRL2_CAL_ERR:0)|(cal_busy?NAU7802_CTRL2_CALS:0);
    if(a==I2C_ADDR_NAU7802 && r==NAU7802_ADCO_B2) {assert(ready); memset(p,0xff,n);}
    return 0;
}
int board_adc_read_vbat(uint16_t *p) {(void)p; return -1;}
uint16_t board_vbat_mv_from_adc(unsigned n) {return (uint16_t)n;}
int main(void) {
    sensors_status_t st; smart_apo_sample_t s;
    sensors_init(&st); assert(st.imu_ok && st.press_ok && bdu==0x44);
    if(SMART_APO_VARIANT==SMART_APO_VARIANT_UW) {
        assert(st.strain_ok && cal_requested);
        assert(sensors_poll(0,&s,&st)); assert(!(s.flags&SAMPLE_FLAG_STRAIN_OK));
        ready=1; assert(sensors_poll(10000,&s,&st));
        assert((s.flags&SAMPLE_FLAG_STRAIN_OK) && s.tension_raw==-1);
        cal_error=1; sensors_init(&st); assert(!st.strain_ok);
        cal_error=0; cal_busy=1; sensors_init(&st); assert(!st.strain_ok);
        cal_busy=0; pur_missing=1; sensors_init(&st); assert(!st.strain_ok);
    } else assert(nau_writes==0 && !st.strain_ok);
    fail_write=1; sensors_init(&st); assert(!st.imu_ok && !st.press_ok && !st.strain_ok);
    return 0;
}
