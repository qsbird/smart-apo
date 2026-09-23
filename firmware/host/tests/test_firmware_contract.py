"""Native logic/serialization tests; never runs board.c memory-mapped I/O."""
import importlib.util
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
MCU = ROOT / 'firmware/mcu'
spec = importlib.util.spec_from_file_location('dump_decode', ROOT / 'firmware/host/dump_decode.py')
decoder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decoder)


class FirmwareContract(unittest.TestCase):
    def build_run(self, source, units, variant=0):
        cc = shutil.which('clang') or shutil.which('cc')
        self.assertIsNotNone(cc, 'A native C compiler is required for these tests')
        with tempfile.TemporaryDirectory() as tmp:
            harness = Path(tmp) / 'test.c'
            harness.write_text(source)
            exe = Path(tmp) / 'test'
            subprocess.run([cc, '-std=c11', '-Wall', '-Wextra', '-Werror',
                            f'-DSMART_APO_VARIANT={variant}', '-I' + str(MCU / 'include'),
                            str(harness), *[str(MCU / 'src' / u) for u in units], '-o', str(exe)], check=True)
            return subprocess.check_output([str(exe)])

    def test_all_sources_both_variants_compile(self):
        cc = shutil.which('clang') or shutil.which('cc')
        for variant in (0, 1):
            subprocess.run([cc, '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsyntax-only',
                            f'-DSMART_APO_VARIANT={variant}', '-I' + str(MCU / 'include'),
                            *map(str, sorted((MCU / 'src').glob('*.c')))], check=True)

    def test_st_rcc_register_contract(self):
        self.build_run(r'''
#include "board_revA2.h"
/* ST CMSIS stm32g031xx.h RCC_TypeDef: APBENR2 offset 0x40,
 * whereas 0x4c is APBSMENR1 and cannot enable SYSCFG or SPI1. */
_Static_assert(RCC_APBENR2_G0 == 0x40021040u, "Wrong RCC APBENR2 address");
int main(void) {return 0;}
''', [])

    def test_c_uart_packet_decodes_and_corruption_resynchronizes(self):
        frame = self.build_run(r'''
#include "uart_dump.h"
#include <stdio.h>
#include <assert.h>
int board_usart2_write(const uint8_t *p, unsigned n) {(void)p; (void)n; return -1;}
int main(void) {
    smart_apo_sample_t s = {.timestamp_us=123456, .sequence=7, .ax=-123,
        .gx=456, .pressure_raw=4096000, .tension_raw=-42, .flags=6};
    uint8_t frame[UART_DUMP_MAX_FRAME];
    assert(sizeof(s) == 34);
    assert(uart_dump_pack_sample(&s, frame, sizeof(frame)-1) == 0);
    assert(uart_dump_pack_sample(&s, frame, sizeof(frame)) == 40);
    assert(uart_dump_send_sample(&s) == -1);
    return fwrite(frame, 1, sizeof(frame), stdout) == sizeof(frame) ? 0 : 1;
}
''', ['uart_dump.c'])
        rows = decoder.decode_bytes(frame)
        self.assertEqual(len(rows), 1)
        self.assertEqual(decoder.decode_bytes(frame + frame), rows)
        self.assertEqual(rows[0][0:3], (123456, 7, -123))
        self.assertEqual(rows[0][8:10], (4096000, -42))
        damaged = bytearray(frame)
        damaged[8] ^= 1
        self.assertEqual(decoder.decode_bytes(b'noise' + damaged + frame + frame[:15]), rows)
        valid = list(rows[0])
        valid[-1] = decoder.crc16_ccitt(decoder.SAMPLE.pack(*valid)[:-2])
        self.assertEqual(decoder.format_autotune(tuple(valid), False, 0).split(',')[-1], '1000')
        valid[-2] = 14
        valid[-1] = decoder.crc16_ccitt(decoder.SAMPLE.pack(*valid)[:-2])
        self.assertEqual(decoder.format_autotune(tuple(valid), True, 2, 0).split(',')[-2:], ['2000', '-21'])

    def test_log_lifecycle_and_reboot_protection(self):
        for variant in (0, 1):
            self.build_run((MCU / 'tests/log_lifecycle.c').read_text(), ['datalog.c'], variant)

    def test_flash_nor_readback_and_torn_write(self):
        self.build_run((MCU / 'tests/flash_nor.c').read_text(), ['flash.c'])

    def test_sensor_timing_wrap_rates_overrun_and_clock_fault(self):
        for variant in (0, 1):
            self.build_run((MCU / 'tests/sensors_timing.c').read_text(), ['sensors.c'], variant)

    def test_missing_hardware_clock_does_not_invent_time(self):
        self.build_run(r'''
#include "board_revA2.h"
#include <assert.h>
int main(void) {
    uint32_t now=123456;
    assert(board_time_us(&now)==-1 && now==123456);
    assert(board_time_us(0)==-1);
    return 0;
}
''', ['board.c'])

    def test_sensor_bdu_calibration_and_ready_gates(self):
        for variant in (0, 1):
            self.build_run((MCU / 'tests/sensors_config.c').read_text(), ['sensors.c'], variant)

    def test_log_full_capacity_rejects_after_implicit_flush(self):
        self.build_run((MCU / 'tests/log_capacity.c').read_text(), ['datalog.c'])

    def test_flash_bounds_reject_before_spi(self):
        self.build_run(r'''
#include "flash.h"
#include <assert.h>
static int calls;
int board_time_us(uint32_t *now) {static uint32_t ticks; *now=++ticks; return 0;}
int board_spi1_cs(int low) {(void)low; ++calls; return -1;}
int board_spi1_tx(const uint8_t *p, unsigned n) {(void)p; (void)n; return -1;}
int board_spi1_rx(uint8_t *p, unsigned n) {(void)p; (void)n; return -1;}
int main(void) {
    uint8_t page[256]={0};
    assert(flash_page_program(W25Q_CAPACITY_BYTES, page, 256) == -1);
    assert(flash_page_program(0xffffff00u, page, 256) == -1);
    assert(flash_page_program(1, page, 256) == -1);
    assert(flash_page_program(0, 0, 256) == -1);
    assert(calls == 0);
    assert(flash_page_program(W25Q_CAPACITY_BYTES-256, page, 256) == -1);
    assert(calls == 2);
    return 0;
}
''', ['flash.c'])

    def test_app_log_errors_and_dump_retries(self):
        for variant in (0, 1):
            self.build_run((MCU / 'tests/app_errors.c').read_text(), ['app.c'], variant)


if __name__ == '__main__':
    unittest.main()
