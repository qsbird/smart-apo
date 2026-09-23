"""Mutation checks for working BOM/variant/netlist mismatches."""
import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'check_bom_revA2.py'
spec = importlib.util.spec_from_file_location('check_bom_revA2', SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class BomConsistencyTests(unittest.TestCase):
    def run_case(self, mutation=None, variants_mutation=None, netlist_mutation=None):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            names = ['BOM_revA2_WORKING.csv', 'ASSEMBLY_VARIANTS_revA2.csv', 'netlist_revA2_kicad10.xml']
            for name in names:
                (dest / name).write_bytes((checker.REV / name).read_bytes())
            for name, edit in [(names[0], mutation), (names[1], variants_mutation)]:
                if edit:
                    with (dest / name).open(newline='') as f:
                        reader = csv.DictReader(f)
                        fields, rows = reader.fieldnames, list(reader)
                    edit(rows)
                    with (dest / name).open('w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=fields)
                        writer.writeheader()
                        writer.writerows(rows)
            if netlist_mutation:
                path = dest / names[2]
                path.write_text(netlist_mutation(path.read_text()))
            return checker.check(*(dest / n for n in names))

    def test_current_design_consistent(self):
        result = self.run_case()
        self.assertEqual(result['issues'], [])
        self.assertEqual(result['component_count'], 43)

    def test_historical_c7_value_rejected(self):
        def change(rows):
            next(r for r in rows if r['Designator'] == 'C7')['Comment'] = '1uF X5R'
        self.assertIn('passive value mismatch: C7', self.run_case(change)['issues'])

    def test_wrong_package_rejected(self):
        def change(rows):
            next(r for r in rows if r['Designator'] == 'C11 C12')['Footprint'] = 'Capacitor_SMD:C_0603_1608Metric'
        issues = self.run_case(change)['issues']
        self.assertIn('footprint mismatch: C11', issues)
        self.assertIn('footprint mismatch: C12', issues)

    def test_variant_quantity_rejected(self):
        def change(rows):
            next(r for r in rows if r['Designator'] == 'C7')['AWA Qty'] = '1'
        self.assertTrue(any('quantity mismatch: C7/AWA' in s for s in self.run_case(change)['issues']))

    def test_duplicate_and_missing_refs_rejected(self):
        def change(rows):
            rows[0]['Designator'] = rows[1]['Designator']
        issues = self.run_case(change)['issues']
        self.assertTrue(any('duplicate BOM' in s for s in issues))
        self.assertTrue(any('BOM coverage mismatch' in s for s in issues))

    def test_population_disagreement_rejected(self):
        def change(rows):
            next(r for r in rows if r['Reference'] == 'U4')['AWA'] = 'POPULATE'
        self.assertIn('population mismatch: U4/AWA', self.run_case(variants_mutation=change)['issues'])

    def test_led_anode_cathode_swap_rejected(self):
        def change(text):
            return text.replace('ref="D1" pin="1"', 'ref="D1" pin="TEMP"').replace('ref="D1" pin="2"', 'ref="D1" pin="1"').replace('ref="D1" pin="TEMP"', 'ref="D1" pin="2"')
        self.assertTrue(any('D1 polarity mismatch' in issue for issue in self.run_case(netlist_mutation=change)['issues']))

    def test_generic_passive_led_semantics_rejected(self):
        def change(text):
            return text.replace('pinfunction="K_1"', 'pinfunction="1_1"').replace('pinfunction="A_2"', 'pinfunction="2_2"')
        self.assertTrue(any('D1 polarity mismatch' in issue for issue in self.run_case(netlist_mutation=change)['issues']))


if __name__ == '__main__':
    unittest.main()
