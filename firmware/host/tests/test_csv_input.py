import importlib.util
from pathlib import Path
import tempfile
import unittest

p = Path(__file__).resolve().parents[1] / 'csv_input.py'
spec = importlib.util.spec_from_file_location('apo_csv_input', p)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
REQUIRED = ('timestamp_us', 'ax', 'tension_gf')


class CsvInputTests(unittest.TestCase):
    def read(self, text):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / 'capture.csv'
            p.write_text(text)
            return module.load_numeric_csv(p, REQUIRED)

    def test_valid_signed_channels_and_nonuniform_time(self):
        data = self.read('timestamp_us,ax,tension_gf,notes\n10,-.5,-2,first\n30,1e-3,3,next\n55,0,0,last\n')
        self.assertEqual(data['timestamp_us'], [10.,30.,55.])
        self.assertEqual(data['ax'], [-.5,.001,0.])

    def test_nonfinite_in_each_required_column(self):
        for i in range(3):
            for bad in ['nan', 'inf', '-inf', '1e999']:
                row = ['20','1','2'];row[i] = bad
                with self.subTest(column=i,value=bad), self.assertRaisesRegex(ValueError, 'finite'):
                    self.read('timestamp_us,ax,tension_gf\n10,0,0\n'+','.join(row)+'\n')

    def test_duplicate_and_reverse_timestamps_rejected(self):
        for stamp in ['10','9']:
            with self.assertRaisesRegex(ValueError, 'strictly increasing'):
                self.read(f'timestamp_us,ax,tension_gf\n10,0,0\n{stamp},1,1\n')

    def test_duplicate_headers_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.read('timestamp_us,ax,tension_gf,ax\n1,0,0,3\n2,0,0,4\n')

    def test_missing_columns_and_blank_cells_rejected(self):
        with self.assertRaisesRegex(ValueError, 'missing columns'):
            self.read('timestamp_us,ax\n1,0\n2,0\n')
        with self.assertRaisesRegex(ValueError, 'ax'):
            self.read('timestamp_us,ax,tension_gf\n1,0,0\n2,,0\n')

    def test_empty_and_single_record_rejected(self):
        for text in ['', 'timestamp_us,ax,tension_gf\n', 'timestamp_us,ax,tension_gf\n1,0,0\n']:
            with self.assertRaises(ValueError):self.read(text)


if __name__ == '__main__':unittest.main()
