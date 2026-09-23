#!/usr/bin/env python3
"""Working BOM consistency only: not supplier, polarity or manufacturing release."""
import argparse
import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / 'hardware/revA2'


def value_number(value):
    match = re.match(r'^(\d+(?:\.\d+)?)([pnumkR]?)', value)
    if not match:
        raise ValueError('unrecognized passive value: ' + value)
    return Decimal(match[1]) * {'p': Decimal('1e-12'), 'n': Decimal('1e-9'),
        'u': Decimal('1e-6'), 'm': Decimal('1e-3'), 'k': Decimal('1e3'),
        'R': Decimal(1), '': Decimal(1)}[match[2]]


def check(bom_path, variants_path, netlist_path):
    with bom_path.open(newline='') as f:
        rows = list(csv.DictReader(f))
    with variants_path.open(newline='') as f:
        variants = list(csv.DictReader(f))
    components = {c.get('ref'): c for c in ET.parse(netlist_path).getroot().findall('./components/comp')}
    issues = []
    population = {}
    for row in variants:
        for ref in row['Reference'].split():
            if ref in population:
                issues.append(f'duplicate variant reference: {ref}')
            population[ref] = row
    covered = set()
    for row in rows:
        refs = row['Designator'].split()
        expected_qty = {'AWA': 0, 'UNDERWATER': 0}
        for ref in refs:
            if ref in covered:
                issues.append(f'duplicate BOM reference: {ref}')
            covered.add(ref)
            if ref not in components or ref not in population:
                issues.append(f'unknown or absent reference: {ref}')
                continue
            comp = components[ref]
            if row['Footprint'] != comp.findtext('footprint'):
                issues.append(f'footprint mismatch: {ref}')
            if ref.startswith(('C', 'R')):
                try:
                    if value_number(row['Comment']) != value_number(comp.findtext('value')):
                        issues.append(f'passive value mismatch: {ref}')
                except ValueError as exc:
                    issues.append(str(exc))
            tag = next((p.get('value') for p in comp.findall('property') if p.get('name') == 'Population'), None)
            for variant in expected_qty:
                state = population[ref][variant]
                if state not in ('POPULATE', 'DNP', 'MANUAL', 'PCB_ONLY'):
                    issues.append(f'unknown assembly state: {ref}/{variant}')
                enabled = state != 'DNP'
                expected_qty[variant] += int(enabled)
                if tag not in ('BOTH', 'AWA', 'UNDERWATER') or enabled != (tag in ('BOTH', variant)):
                    issues.append(f'population mismatch: {ref}/{variant}')
        for variant, qty in expected_qty.items():
            try:
                actual = int(row[variant + ' Qty'])
            except ValueError:
                actual = -1
            if actual != qty:
                issues.append(f'quantity mismatch: {row["Designator"]}/{variant}: {actual} != {qty}')
    if covered != set(components):
        issues.append('BOM coverage mismatch: ' + str(sorted(covered ^ set(components))))
    if set(population) != set(components):
        issues.append('variant coverage mismatch: ' + str(sorted(set(population) ^ set(components))))
    led_nodes = {
        node.get('pin'): (net.get('name'), node.get('pinfunction'))
        for net in ET.parse(netlist_path).getroot().findall('./nets/net')
        for node in net.findall('node') if node.get('ref') == 'D1'
    }
    if led_nodes != {'1': ('/LED_K', 'K_1'), '2': ('/LED_A', 'A_2')}:
        issues.append('D1 polarity mismatch: require explicit K_1 on LED_K and A_2 on LED_A')
    return {'status': 'PASS_DESIGN_CONSISTENCY_ONLY' if not issues else 'FAIL',
        'component_count': len(components), 'BOM_reference_count': len(covered), 'issues': issues,
        'scope': 'Exact footprint IDs, passive nominal values, unique reference coverage, variant presence and grouped quantities. PCB_ONLY/MANUAL counts are presence, not SMT purchase quantities. Supplier SKU, exact MPN suitability, tolerance, polarity and effective capacitance are not validated.',
        'inputs_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (bom_path, variants_path, netlist_path)}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = check(REV / 'BOM_revA2_WORKING.csv', REV / 'ASSEMBLY_VARIANTS_revA2.csv', REV / 'netlist_revA2_kicad10.xml')
    text = json.dumps(report, indent=2) + '\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')
    raise SystemExit(0 if not report['issues'] else 1)
