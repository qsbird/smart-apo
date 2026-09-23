"""Check the real LPS geometry guard without writing project reports."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'validate_revA2.py'
spec = importlib.util.spec_from_file_location('validate_revA2', SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
FOOTPRINT = validator.REV / 'SmartApoRevA2.pretty/LPS28DFW_CCLGA-7L.kicad_mod'
REPORT = validator.REV / 'validation_report_revA2.json'


class LpsGeometryTests(unittest.TestCase):
    def check_geometry(self, footprint):
        original_read = Path.read_text
        captured = {}

        def read(path, *args, **kwargs):
            return footprint if path == FOOTPRINT else original_read(path, *args, **kwargs)

        def write(path, value, *args, **kwargs):
            self.assertEqual(path, REPORT)
            captured.update(json.loads(value))
            return len(value)

        with patch.object(Path, 'read_text', read), patch.object(Path, 'write_text', write):
            with contextlib.redirect_stdout(io.StringIO()):
                try:
                    validator.main()
                except SystemExit as exc:
                    self.assertEqual(exc.code, 1)
        return captured['lps28dfw_official_geometry_locked']

    def test_kicad_multiline_geometry_accepted(self):
        self.assertTrue(self.check_geometry(FOOTPRINT.read_text()))

    def test_compact_geometry_accepted(self):
        self.assertTrue(self.check_geometry(' '.join(FOOTPRINT.read_text().split())))

    def test_changed_pad_dimensions_rejected(self):
        source = FOOTPRINT.read_text()
        changed = source.replace('(size 0.35 1.4)', '(size 0.35 1.5)')
        self.assertNotEqual(source, changed)
        self.assertFalse(self.check_geometry(changed))

    def test_relaxed_track_keepout_rejected(self):
        source = FOOTPRINT.read_text()
        changed = source.replace('(tracks not_allowed)', '(tracks allowed)')
        self.assertNotEqual(source, changed)
        self.assertFalse(self.check_geometry(changed))


if __name__ == '__main__':
    unittest.main()
