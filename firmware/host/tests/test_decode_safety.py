import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'dump_decode.py'
spec = importlib.util.spec_from_file_location('decode_safety_target', SCRIPT)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def row(flags=6, timestamp=1000, tension=120, sequence=1):
    values = [timestamp, sequence, 0, 0, 1000, 1000, 0, 0, 4096000, tension, 0, 0, flags, 0]
    values[-1] = d.crc16_ccitt(d.SAMPLE.pack(*values)[:-2])
    return tuple(values)


def frame(values):
    payload = bytes([1, d.SAMPLE.size]) + d.SAMPLE.pack(*values)
    return d.SYNC + payload + d.crc16_ccitt(payload).to_bytes(2, 'big')


class DecodeSafety(unittest.TestCase):
    def unwrap(self, rows, limit=1000):
        return d.format_autotune_rows(rows, False, 0, unwrap_timestamps=True,
                                      max_sample_gap_us=limit)

    def test_explicit_timestamp_unwrap_preserves_payload_and_sequence_wrap(self):
        rows = [row(timestamp=0xfffffff0, sequence=65535), row(timestamp=16, sequence=0),
                row(timestamp=48, sequence=1)]
        original = list(rows)
        self.assertEqual([line.split(',')[0] for line in self.unwrap(rows, 32)],
                         ['4294967280.0', '4294967312.0', '4294967344.0'])
        self.assertEqual(rows, original)
        self.assertEqual(d.decode_bytes(b''.join(frame(r) for r in rows)), original)

    def test_unwrap_rejects_duplicate_backward_and_half_period_ambiguity(self):
        for start, end, limit in ((100, 100, 1000), (100, 99, 1000),
                                  (0, 1 << 31, (1 << 31) - 1),
                                  (0, (1 << 31) + 1, (1 << 31) - 1),
                                  (100, 1101, 1000)):
            with self.subTest(start=start, end=end), self.assertRaisesRegex(ValueError, 'ambiguous'):
                self.unwrap([row(timestamp=start), row(timestamp=end, sequence=2)], limit)

    def test_unwrap_requires_explicit_bounded_contract(self):
        for limit in (None, 0, -1, 1 << 31, 1.5, True):
            with self.subTest(limit=limit), self.assertRaisesRegex(ValueError, 'explicit max'):
                self.unwrap([row()], limit)
        with self.assertRaisesRegex(ValueError, 'requires explicit timestamp'):
            d.format_autotune_rows([row()], False, 0, max_sample_gap_us=1000)

    def test_unwrap_keeps_crc_flags_variant_and_sequence_gates(self):
        first = row(timestamp=0xfffffff0, sequence=65535)
        bad_inner = list(row(timestamp=16, sequence=0)); bad_inner[2] ^= 1
        for second, reason in ((tuple(bad_inner), 'CRC'),
                               (row(timestamp=16, sequence=0, flags=2), 'missing valid'),
                               (row(timestamp=16, sequence=0, flags=14), 'conflicts'),
                               (row(timestamp=16, sequence=1), 'sequence gap')):
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                self.unwrap([first, second])
        bad_outer = bytearray(frame(row(timestamp=16, sequence=0))); bad_outer[-1] ^= 1
        rows = d.decode_bytes(frame(first) + bad_outer + frame(row(timestamp=48, sequence=1)))
        with self.assertRaisesRegex(ValueError, 'sequence gap'):
            self.unwrap(rows)

    def test_unwrap_multiple_time_wraps(self):
        # Small known intervals accumulate beyond several uint32 periods.
        step = 1000000000
        rows = [row(timestamp=(i * step) & 0xffffffff, sequence=i) for i in range(14)]
        self.assertEqual(self.unwrap(rows, step)[-1].split(',')[0], '13000000000.0')

    def test_cli_unwrap_opt_in_and_refusal_preserve_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / 'log.bin'; output = Path(tmp) / 'out.csv'
            binary.write_bytes(frame(row(timestamp=0xfffffff0, sequence=65535)) +
                               frame(row(timestamp=16, sequence=0)))
            base = [sys.executable, str(SCRIPT), str(binary), '--autotune', 'awa', '--allow-headerless', '-o', str(output)]
            for options in ([], ['--unwrap-timestamps'],
                            ['--unwrap-timestamps', '--max-sample-gap-us', '31']):
                output.write_text('existing review artifact')
                result = subprocess.run(base + options, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(output.read_text(), 'existing review artifact')
            result = subprocess.run(base + ['--unwrap-timestamps', '--max-sample-gap-us', '32'],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('4294967312.0,', output.read_text())

    def test_missing_flags_and_variant_are_rejected(self):
        for flags in (0, 2, 4, 8, 10, 12):
            with self.assertRaisesRegex(ValueError, 'missing valid'):
                d.format_autotune(row(flags), True, 2, 100)
        with self.assertRaisesRegex(ValueError, 'conflicts'):
            d.format_autotune(row(14), False, 0)
        # Valid physical zero acceleration must remain a real zero, not a missing-value rule.
        self.assertEqual(d.format_autotune(row(), False, 0).split(',')[1], '0')

    def test_calibration_requires_finite_slope_and_explicit_zero(self):
        for slope, zero in ((0, 0), (float('nan'), 0), (float('inf'), 0), (2, None), (2, float('nan'))):
            with self.assertRaisesRegex(ValueError, 'UW needs'):
                d.format_autotune(row(14), True, slope, zero)
        self.assertEqual(d.format_autotune(row(14), True, 2, 100).split(',')[-1], '10')
        self.assertEqual(d.format_autotune(row(14), True, -2, 100).split(',')[-1], '-10')

    def test_manufacturer_sensitivities(self):
        fields = d.format_autotune(row(), False, 0).split(',')
        self.assertEqual(float(fields[3]), 0.122)
        self.assertEqual(float(fields[4]), 17.5)

    def test_inner_crc_and_timestamp_rejection(self):
        corrupted = list(row()); corrupted[2] ^= 1
        with self.assertRaisesRegex(ValueError, 'CRC'):
            d.format_autotune(tuple(corrupted), False, 0)
        for rows in ([row(), row()], [row(timestamp=0xffffffff), row(timestamp=0)]):
            with self.assertRaisesRegex(ValueError, 'strictly increase'):
                d.format_autotune_rows(rows, False, 0)
        self.assertEqual(len(d.format_autotune_rows([row(), row(timestamp=2000, sequence=2)], False, 0)), 2)

    def test_sequence_gap_after_corrupt_frame_and_normal_wrap(self):
        first = row(sequence=0)
        middle = bytearray(frame(row(timestamp=2000, sequence=1)))
        middle[-1] ^= 1  # outer UART CRC failure hides the middle record
        last = row(timestamp=3000, sequence=2)
        recovered = d.decode_bytes(frame(first) + middle + frame(last))
        self.assertEqual([r[1] for r in recovered], [0, 2])  # raw recovery remains available
        with self.assertRaisesRegex(ValueError, 'sequence gap'):
            d.format_autotune_rows(recovered, False, 0)
        for next_sequence in (1, 0):
            with self.assertRaisesRegex(ValueError, 'sequence gap'):
                d.format_autotune_rows([row(sequence=1), row(timestamp=2000, sequence=next_sequence)], False, 0)
        wrapped = [row(sequence=65535), row(timestamp=2000, sequence=0)]
        self.assertEqual(len(d.format_autotune_rows(wrapped, False, 0)), 2)

    def test_cli_rejects_partial_log_without_overwriting_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / 'log.bin'; output = Path(tmp) / 'out.csv'
            binary.write_bytes(frame(row()) + frame(row(flags=2, timestamp=2000, sequence=2)))
            output.write_text('existing review artifact')
            result = subprocess.run([sys.executable, str(SCRIPT), str(binary), '--autotune', 'awa', '--allow-headerless', '-o', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('missing valid', result.stderr)
            self.assertEqual(output.read_text(), 'existing review artifact')
            result = subprocess.run([sys.executable, str(SCRIPT), str(binary)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)  # raw diagnostic export stays available
            self.assertEqual(len(result.stdout.splitlines()), 3)
