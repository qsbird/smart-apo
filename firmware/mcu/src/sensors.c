#include "sensors.h"
#include "datalog.h"

#include <string.h>

/* Fractional phases preserve exact nominal ODR without truncating periods.
 * One poll may read only the current conversion, never fabricate past samples.
 */
static uint32_t g_phase[4], g_last_poll_us;
static int g_started, g_clock_fault;
static sensors_timing_stats_t g_timing;

void sensors_timing_stats(sensors_timing_stats_t *out)
{
    if (out) *out = g_timing;
}

static int channel_due(unsigned channel, unsigned hz, uint32_t elapsed, int first)
{
    uint64_t phase = g_phase[channel] + (uint64_t)elapsed * hz;
    uint32_t slots = (uint32_t)(phase / 1000000u);
    g_phase[channel] = (uint32_t)(phase % 1000000u);
    if (slots > 1u) {
        uint32_t missed = slots - 1u;
        uint32_t *count = &g_timing.skipped_slots[channel];
        *count = UINT32_MAX - *count < missed ? UINT32_MAX : *count + missed;
    }
    return first || slots != 0u;
}

static int i2c_write_u8(uint8_t addr7, uint8_t reg, uint8_t value)
{
    return board_i2c1_write_u8(addr7, reg, value);
}

static int i2c_read_n(uint8_t addr7, uint8_t reg, uint8_t *buf, unsigned n)
{
    return board_i2c1_read_n(addr7, reg, buf, n);
}

static int i2c_read_u8(uint8_t addr7, uint8_t reg, uint8_t *value)
{
    return i2c_read_n(addr7, reg, value, 1);
}

static int16_t le16(const uint8_t *p)
{
    return (int16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static int32_t le24_sign(const uint8_t *p)
{
    uint32_t u = (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16);
    if (u & 0x800000u) {
        u |= 0xFF000000u;
    }
    return (int32_t)u;
}

static int32_t be24_sign(const uint8_t *p)
{
    uint32_t u = ((uint32_t)p[0] << 16) | ((uint32_t)p[1] << 8) | (uint32_t)p[2];
    if (u & 0x800000u) {
        u |= 0xFF000000u;
    }
    return (int32_t)u;
}

static int lsm6dso_read_sample(smart_apo_sample_t *out)
{
    uint8_t buf[14];
    int16_t t_raw;

    /* DS12754: OUT_TEMP_L..OUTZ_H_A with IF_INC. Gyro then accel. */
    if (i2c_read_n(I2C_ADDR_LSM6DSO_SA0_GND, LSM6DSO_OUT_TEMP_L, buf, 14) != 0) {
        return -1;
    }
    t_raw = le16(buf);
    out->temperature = (int16_t)(2500 + ((int32_t)t_raw * 100) / 256);
    out->gx = le16(buf + 2);
    out->gy = le16(buf + 4);
    out->gz = le16(buf + 6);
    out->ax = le16(buf + 8);
    out->ay = le16(buf + 10);
    out->az = le16(buf + 12);
    return 0;
}

static int lps28_read_sample(smart_apo_sample_t *out)
{
    uint8_t buf[5];

    /* DS13317: PRESS_OUT_XL..TEMP_OUT_H with IF_ADD_INC. Temp is 100 LSB/°C. */
    if (i2c_read_n(I2C_ADDR_LPS28DFW, LPS28DFW_PRESS_OUT_XL, buf, 5) != 0) {
        return -1;
    }
    out->pressure_raw = le24_sign(buf);
    out->temperature = le16(buf + 3);
    return 0;
}

static int nau7802_read_sample(smart_apo_sample_t *out)
{
    uint8_t buf[3], status;

    if (i2c_read_u8(I2C_ADDR_NAU7802, NAU7802_PU_CTRL, &status) != 0 ||
        (status & NAU7802_PU_CR) == 0u) {
        return -1; /* never mark a stale or incomplete conversion valid */
    }
    if (i2c_read_n(I2C_ADDR_NAU7802, NAU7802_ADCO_B2, buf, 3) != 0) {
        return -1;
    }
    out->tension_raw = be24_sign(buf);
    return 0;
}

static int nau7802_configure(void)
{
    uint8_t pur;

    /* V1.7 §9.1. Do not init on AWA — U4 is DNP. */
    if (i2c_write_u8(I2C_ADDR_NAU7802, NAU7802_PU_CTRL, NAU7802_PU_RR) != 0) {
        return -1;
    }
    if (i2c_write_u8(I2C_ADDR_NAU7802, NAU7802_PU_CTRL, NAU7802_PU_PUD) != 0) {
        return -1;
    }
    /* Bounded polling is fail-closed; HAL must replace counts with a timed deadline. */
    pur = 0;
    for (unsigned i = 0; i < NAU7802_READY_POLLS; ++i) {
        if (i2c_read_u8(I2C_ADDR_NAU7802, NAU7802_PU_CTRL, &pur) != 0) return -1;
        if (pur & NAU7802_PU_PUR) break;
    }
    if ((pur & NAU7802_PU_PUR) == 0u) return -1;
    if (i2c_write_u8(I2C_ADDR_NAU7802, NAU7802_PU_CTRL, NAU7802_PU_ANALOG_LDO) != 0) {
        return -1;
    }
    if (i2c_write_u8(I2C_ADDR_NAU7802, NAU7802_CTRL1, NAU7802_CTRL1_3V0_G128) != 0) {
        return -1;
    }
    if (i2c_write_u8(I2C_ADDR_NAU7802, NAU7802_CTRL2, NAU7802_CTRL2_320SPS) != 0) {
        return -1;
    }
    if (i2c_write_u8(I2C_ADDR_NAU7802, NAU7802_PU_CTRL, NAU7802_PU_RUN) != 0) {
        return -1;
    }
    /* Internal offset calibration is not beam zero/gain calibration. */
    if (i2c_write_u8(I2C_ADDR_NAU7802, NAU7802_CTRL2,
                     NAU7802_CTRL2_320SPS | NAU7802_CTRL2_CALS) != 0) return -1;
    for (unsigned i = 0; i < NAU7802_CAL_POLLS; ++i) {
        if (i2c_read_u8(I2C_ADDR_NAU7802, NAU7802_CTRL2, &pur) != 0) return -1;
        if ((pur & NAU7802_CTRL2_CALS) == 0u) {
            return (pur & NAU7802_CTRL2_CAL_ERR) ? -1 : 0;
        }
    }
    return -1;
}

static int whoami_match(uint8_t addr7, uint8_t reg, uint8_t expect)
{
    uint8_t id;

    if (i2c_read_u8(addr7, reg, &id) != 0) {
        return 0;
    }
    return id == expect;
}

int sensors_probe(sensors_status_t *st)
{
    if (st == 0) {
        return -1;
    }
    st->imu_ok = whoami_match(I2C_ADDR_LSM6DSO_SA0_GND, LSM6DSO_WHO_AM_I_REG, LSM6DSO_WHO_AM_I_VAL);
    st->press_ok = whoami_match(I2C_ADDR_LPS28DFW, LPS28DFW_WHOAMI_REG, LPS28DFW_WHOAMI_VAL);
    st->strain_ok = 0;
    /* NAU7802 has no WHO_AM_I; strain_ok is set only after configure. */
    if (!st->imu_ok && !st->press_ok) {
        return -1;
    }
    return 0;
}

int sensors_configure(sensors_status_t *st)
{
    int rc = 0;
    uint8_t xl;
    uint8_t g;
    uint8_t p1;
    uint8_t p2;

    if (st == 0) {
        return -1;
    }
    if (st->imu_ok) {
        xl = (SMART_APO_VARIANT == SMART_APO_VARIANT_UW) ? LSM6DSO_CTRL1_XL_UW : LSM6DSO_CTRL1_XL_AWA;
        g = (SMART_APO_VARIANT == SMART_APO_VARIANT_UW) ? LSM6DSO_CTRL2_G_UW : LSM6DSO_CTRL2_G_AWA;
        if (i2c_write_u8(I2C_ADDR_LSM6DSO_SA0_GND, LSM6DSO_CTRL1_XL, xl) != 0 ||
            i2c_write_u8(I2C_ADDR_LSM6DSO_SA0_GND, LSM6DSO_CTRL2_G, g) != 0 ||
            i2c_write_u8(I2C_ADDR_LSM6DSO_SA0_GND, LSM6DSO_CTRL3_C, LSM6DSO_CTRL3_C_CONFIG) != 0 ||
            i2c_write_u8(I2C_ADDR_LSM6DSO_SA0_GND, LSM6DSO_INT1_CTRL, LSM6DSO_INT1_CTRL_DRDY) != 0) {
            st->imu_ok = 0;
            rc = -1;
        }
    }
    if (st->press_ok) {
        p1 = (SMART_APO_VARIANT == SMART_APO_VARIANT_UW) ? LPS28DFW_CTRL_REG1_UW : LPS28DFW_CTRL_REG1_AWA;
        p2 = (SMART_APO_VARIANT == SMART_APO_VARIANT_UW) ? LPS28DFW_CTRL_REG2_UW : LPS28DFW_CTRL_REG2_AWA;
        if (i2c_write_u8(I2C_ADDR_LPS28DFW, LPS28DFW_CTRL_REG2, p2) != 0 ||
            i2c_write_u8(I2C_ADDR_LPS28DFW, LPS28DFW_CTRL_REG1, p1) != 0) {
            st->press_ok = 0;
            rc = -1;
        }
    }
    if (SMART_APO_VARIANT == SMART_APO_VARIANT_UW) {
        if (nau7802_configure() != 0) {
            st->strain_ok = 0;
            rc = -1;
        } else {
            st->strain_ok = 1;
        }
    }
    return rc;
}

void sensors_init(sensors_status_t *st)
{
    memset(st, 0, sizeof(*st));
    /* WHO_AM_I first. Do not write CTRL if the chip ID does not match. */
    (void)sensors_probe(st);
    (void)sensors_configure(st);
    memset(g_phase, 0, sizeof(g_phase));
    memset(&g_timing, 0, sizeof(g_timing));
    g_started = g_clock_fault = 0;
    g_last_poll_us = 0;
}

int sensors_poll(uint32_t now_us, smart_apo_sample_t *out, const sensors_status_t *st)
{
    int due = 0;
    int first = !g_started;
    uint32_t elapsed = first ? 0u : now_us - g_last_poll_us;
    if (!out || !st) return -1;
    memset(out, 0, sizeof(*out));
    if (g_clock_fault || elapsed > INT32_MAX) {
        g_clock_fault = 1;
        return -1;
    }
    g_started = 1;
    g_last_poll_us = now_us;
    out->timestamp_us = now_us;
    if (channel_due(0, SMART_APO_VARIANT == SMART_APO_VARIANT_UW ?
                    ODR_IMU_UW_HZ : ODR_IMU_AWA_HZ, elapsed, first)) {
        due = 1;
        if (st->imu_ok && lsm6dso_read_sample(out) == 0) {
            out->flags |= SAMPLE_FLAG_IMU_OK;
        }
    }
    if (channel_due(1, SMART_APO_VARIANT == SMART_APO_VARIANT_UW ?
                    ODR_PRESS_UW_HZ : ODR_PRESS_AWA_HZ, elapsed, first)) {
        due = 1;
        if (st->press_ok && lps28_read_sample(out) == 0) {
            out->flags |= SAMPLE_FLAG_PRESS_OK;
            /* LPS28 temp is already 0.01 °C; replaces IMU temp when both due. */
        }
    }
    if (SMART_APO_VARIANT == SMART_APO_VARIANT_UW &&
        channel_due(2, ODR_STRAIN_UW_SPS, elapsed, first)) {
        due = 1;
        if (st->strain_ok && nau7802_read_sample(out) == 0) {
            out->flags |= SAMPLE_FLAG_STRAIN_OK;
        }
    }
    if (channel_due(3, ODR_BATT_HZ, elapsed, first)) {
        uint16_t adc;
        due = 1;
        if (board_adc_read_vbat(&adc) == 0) {
            out->battery_mv = board_vbat_mv_from_adc(adc);
        }
    }
    return due;
}
