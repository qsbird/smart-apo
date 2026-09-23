#ifndef SENSORS_REVA2_H
#define SENSORS_REVA2_H

#include "board_revA2.h"

/* Register maps from ST LSM6DSO, ST LPS28DFW, Nuvoton NAU7802. No I2C
 * transactions until CubeMX/HAL exists; these helpers only pack samples.
 */

#define LSM6DSO_WHO_AM_I_REG  0x0Fu
#define LSM6DSO_WHO_AM_I_VAL  0x6Cu
#define LSM6DSO_CTRL1_XL      0x10u
#define LSM6DSO_CTRL2_G       0x11u
#define LSM6DSO_CTRL3_C       0x12u
#define LSM6DSO_CTRL3_C_IFINC 0x04u /* bit2 IF_INC; needed for OUT burst */
#define LSM6DSO_CTRL3_C_BDU   (1u << 6)
#define LSM6DSO_CTRL3_C_CONFIG (LSM6DSO_CTRL3_C_IFINC | LSM6DSO_CTRL3_C_BDU)
#define LSM6DSO_INT1_CTRL     0x0Du
#define LSM6DSO_INT1_DRDY_XL  (1u << 0)
#define LSM6DSO_INT1_DRDY_G   (1u << 1)
#define LSM6DSO_INT1_CTRL_DRDY (LSM6DSO_INT1_DRDY_XL | LSM6DSO_INT1_DRDY_G) /* 0x03, active-high PP */
#define LSM6DSO_OUT_TEMP_L    0x20u
#define LSM6DSO_OUTX_L_G      0x22u
#define LSM6DSO_OUTX_L_A      0x28u

#define LPS28DFW_WHOAMI_REG   0x0Fu
#define LPS28DFW_WHOAMI_VAL   0xB4u
#define LPS28DFW_CTRL_REG1    0x10u
#define LPS28DFW_CTRL_REG2    0x11u
#define LPS28DFW_PRESS_OUT_XL 0x28u
#define LPS28DFW_TEMP_OUT_L   0x2Bu
#define LPS28DFW_TEMP_LSB_C   100 /* DS13317: 100 LSB/°C; equals sample 0.01°C units */

#define NAU7802_PU_CTRL       0x00u
#define NAU7802_CTRL1         0x01u
#define NAU7802_CTRL2         0x02u
#define NAU7802_ADCO_B2       0x12u

/* Candidate full-scale until CubeMX writes CTRL registers. Host dump_decode
 * uses the same numbers. Do not treat these as calibrated voyage units.
 */
#define LSM6DSO_ACCEL_FS_G        4
#define LSM6DSO_GYRO_FS_DPS     500

/* DS13317 Rev 1 §9.6: CTRL_REG1 bit7=0, ODR[3:0]=bits6:3, AVG[2:0]=bits2:0.
 * Table 19: 0101=50 Hz, 0111=100 Hz. Table 20: 100=AVG 64 (valid at 50 and 100 Hz
 * per Table 21; AVG 128 is not valid at 100 Hz).
 */
#define LPS28DFW_CTRL1_ODR_50HZ   (0x5u << 3)
#define LPS28DFW_CTRL1_ODR_100HZ  (0x7u << 3)
#define LPS28DFW_CTRL1_AVG_64     (0x4u << 0)
#define LPS28DFW_CTRL_REG1_AWA    (LPS28DFW_CTRL1_ODR_50HZ | LPS28DFW_CTRL1_AVG_64)  /* 0x2C */
#define LPS28DFW_CTRL_REG1_UW     (LPS28DFW_CTRL1_ODR_100HZ | LPS28DFW_CTRL1_AVG_64) /* 0x3C */

/* DS13317 §9.7 CTRL_REG2: bit6 FS_MODE, bit3 BDU. Mode 1 = 1260 hPa / 4096 LSB/hPa;
 * mode 2 = 4060 hPa / 2048 LSB/hPa. 15 m seawater is ~2500 hPa abs, so underwater
 * must use mode 2. Do not set BOOT/SWRESET/ONESHOT here.
 */
#define LPS28DFW_CTRL2_BDU        (1u << 3)
#define LPS28DFW_CTRL2_FS_MODE    (1u << 6)
#define LPS28DFW_CTRL_REG2_AWA    (LPS28DFW_CTRL2_BDU) /* 0x08, FS_MODE=0 */
#define LPS28DFW_CTRL_REG2_UW     (LPS28DFW_CTRL2_BDU | LPS28DFW_CTRL2_FS_MODE) /* 0x48 */

#define LPS28DFW_LSB_PER_HPA_AWA  4096
#define LPS28DFW_LSB_PER_HPA_UW   2048
#if SMART_APO_VARIANT == SMART_APO_VARIANT_UW
#define LPS28DFW_LSB_PER_HPA      LPS28DFW_LSB_PER_HPA_UW
#else
#define LPS28DFW_LSB_PER_HPA      LPS28DFW_LSB_PER_HPA_AWA
#endif

#if LPS28DFW_CTRL_REG1_AWA != 0x2Cu || LPS28DFW_CTRL_REG1_UW != 0x3Cu
#error "LPS28DFW CTRL_REG1 packing does not match DS13317 Table 19/20"
#endif
#if LPS28DFW_CTRL_REG2_AWA != 0x08u || LPS28DFW_CTRL_REG2_UW != 0x48u
#error "LPS28DFW CTRL_REG2 packing does not match DS13317 §9.7"
#endif
#if LSM6DSO_INT1_CTRL_DRDY != 0x03u
#error "LSM6DSO INT1_CTRL DRDY packing does not match DS12140 INT1_CTRL"
#endif

#define LSM6DSO_CTRL1_XL_AWA  0x48u /* ODR 104 Hz, FS ±4 g */
#define LSM6DSO_CTRL1_XL_UW   0x58u /* ODR 208 Hz, FS ±4 g */
#define LSM6DSO_CTRL2_G_AWA   0x44u /* ODR 104 Hz, FS ±500 dps */
#define LSM6DSO_CTRL2_G_UW    0x54u /* ODR 208 Hz, FS ±500 dps */

/* NAU7802 V1.7: PU_CTRL bit7 AVDDS, bit4 CS, bit2 PUA, bit1 PUD, bit0 RR.
 * §9.1: RR=1, then RR=0 PUD=1, wait ~200 µs for PUR, then analog/LDO, then CS.
 * CTRL1 VLDO 101=3.0 V, GAINS 111=128x. CTRL2 CRS 111=320 SPS. UW only.
 */
#define NAU7802_PU_PUR          (1u << 3)
#define NAU7802_PU_CR           (1u << 5)
#define NAU7802_CTRL2_CALS      (1u << 2)
#define NAU7802_CTRL2_CAL_ERR   (1u << 3)
#define NAU7802_READY_POLLS     256u
#define NAU7802_CAL_POLLS       8192u /* bounded skeleton; replace with real timer */
#define NAU7802_PU_RR           0x01u /* RR=1 */
#define NAU7802_PU_PUD          0x02u /* PUD=1, leave reset */
#define NAU7802_PU_ANALOG_LDO   0x86u /* AVDDS|PUA|PUD, internal LDO */
#define NAU7802_PU_RUN          0x96u /* AVDDS|CS|PUA|PUD, start conversions */
#define NAU7802_CTRL1_3V0_G128  0x2Fu /* VLDO=3.0 V, PGA 128x; DRDY=conversion */
#define NAU7802_CTRL2_320SPS    0x70u /* CRS[6:4]=111 = 320 SPS, CH1 */

#if NAU7802_PU_ANALOG_LDO != 0x86u || NAU7802_PU_RUN != 0x96u
#error "NAU7802 PU_CTRL packing does not match V1.7 §11.1"
#endif
#if NAU7802_CTRL1_3V0_G128 != 0x2Fu || NAU7802_CTRL2_320SPS != 0x70u
#error "NAU7802 CTRL1/CTRL2 packing does not match V1.7 §11.2/§11.3"
#endif

typedef struct {
    int imu_ok;
    int press_ok;
    int strain_ok;
    int lse_ok;
} sensors_status_t;

/* Counters are runtime diagnostics, not persisted in the v1 wire record.
 * Order: IMU, pressure, strain, battery. Saturate rather than wrap.
 * Skipped slots count scheduler overruns, not bus failures or physical DRDY loss.
 */
typedef struct { uint32_t skipped_slots[4]; } sensors_timing_stats_t;
void sensors_timing_stats(sensors_timing_stats_t *out);
void sensors_init(sensors_status_t *st);
int sensors_probe(sensors_status_t *st);
int sensors_configure(sensors_status_t *st);
/* First call anchors phase. Clock must advance modulo 2^32 microseconds;
 * poll gaps must be <= INT32_MAX us. Returns 1 due, 0 idle, -1 invalid clock.
 * Invalid clock is latched until sensors_init; no samples are produced.
 */
int sensors_poll(uint32_t now_us, smart_apo_sample_t *out, const sensors_status_t *st);

#endif
