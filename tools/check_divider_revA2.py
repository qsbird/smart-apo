#!/usr/bin/env python3
"""Cross-check authoritative values, conversion and unchanged PCB geometry."""
from pathlib import Path
from fractions import Fraction
import argparse,csv,hashlib,json,math,re,runpy,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1];hw=root/'hardware/revA2';out=root/'validation/revA2_divider'
parser=argparse.ArgumentParser()
parser.add_argument('--check-value-only',action='store_true',help='Historical divider migration only; later routing may legitimately differ')
parser.add_argument('--output',type=Path,default=out/'current_consistency.json')
args=parser.parse_args()
expected={'R4':'180k','R5':'60.4k'};old={'R4':'1M','R5':'330k'}
def values(text):
    r={}
    for ref in expected:
        m=re.search(r'\(property "Reference" "'+ref+r'"(?:(?!\(property "Reference").)*?\(property "Value" "([^"]+)"',text,re.S)
        assert m,ref
        r[ref]=m[1]
    return r
for ext in ['kicad_sch','kicad_pcb']:
    name='smart_apo_common_revA2.'+ext;p=hw/name;s=p.read_text();assert values(s)==expected
    restored=s
    for ref,value in expected.items():restored=restored.replace('(property "Value" "'+value+'"','(property "Value" "'+old[ref]+'"')
    if args.check_value_only:
        assert restored==(out/'baseline/hardware/revA2'/name).read_text(),name+': changes exceed value fields'
net=ET.parse(hw/'netlist_revA2_kicad10.xml').getroot()
assert {c.attrib['ref']:c.findtext('value') for c in net.find('components') if c.attrib['ref'] in expected}==expected
prior=ET.parse(out/'baseline/netlist_before.xml').getroot()
def nodes(tree):return sorted((n.attrib['name'],tuple(sorted((v.attrib['ref'],v.attrib['pin']) for v in n.findall('node')))) for n in tree.find('nets'))
assert nodes(net)==nodes(prior)
with (hw/'BOM_revA2_WORKING.csv').open(newline='') as f:
    rows={r['Designator']:r for r in csv.DictReader(f)}
for ref,value in expected.items():assert rows[ref]['Comment']==value+' 1%'
h=(root/'firmware/mcu/include/board_revA2.h').read_text()
def constant(n):return int(re.search(r'^#define\s+'+n+r'\s+(\d+)u',h,re.M)[1])
top,bottom=constant('VBAT_R_TOP_OHM'),constant('VBAT_R_BOT_OHM')
assert (top,bottom)==(180000,60400)
ratio=Fraction(3300*(top+bottom),bottom*4095)
assert ratio==Fraction(constant('VBAT_MV_NUM'),constant('VBAT_MV_DEN'))
assert 4095*constant('VBAT_MV_NUM')<2**32
rth=top*bottom/(top+bottom);assert rth*1.01<50000
cap_row=next(row for row in rows.values() if 'C14' in row['Designator'].split())
assert cap_row['Comment']=='100nF X7R' and 'C14 tolerance <=20%' in cap_row['Notes']
settle_seconds=math.log(8192)*rth*1.01*100e-9*1.20*1.15
settle_guard_us=constant('VBAT_STARTUP_SETTLE_US')
minimum_guard_seconds=settle_guard_us/1e6/1.05
assert minimum_guard_seconds>settle_seconds

module=runpy.run_path(str(root/'tools/generate_revA2.py'))
assert module['DIVIDER_VALUES']==expected
assert values(module['update_divider_values']((root/'hardware/smart_apo_common_revA1.kicad_sch').read_text()))==expected
report={'status':'PASS_DESIGN_CONSISTENCY_ONLY','values':expected,'tolerance_percent':1,'rth_nominal_ohm':rth,'rth_max_ohm':rth*1.01,'divider_uA_at_4p2V':4.2/(top+bottom)*1e6,'divider_30day_mAh_at_4p2V':4.2/(top+bottom)*1000*720,'C14_100nF_nominal_tau_ms':rth*.0001,'conversion_reduced':[ratio.numerator,ratio.denominator],'schematic_and_pcb_changes_only_value_fields':True if args.check_value_only else None,'netlist_nodes_unchanged':True,'generator_build_run':False,'board_sha256':hashlib.sha256((hw/'smart_apo_common_revA2.kicad_pcb').read_bytes()).hexdigest(),'limits':'Nominal VDDA=3.3V; not measured accuracy, standby budget, RC settling, leakage or temperature qualification'}
report['startup_RC']={'capacitance_max_F_assumed':138e-9,'r_tolerance':0.01,'c_tolerance':0.20,'c_temperature_positive_fraction':0.15,'clock_fast_fraction_assumed':0.05,'settle_to_half_12bit_LSB_ms':settle_seconds*1000,'guard_nominal_us':settle_guard_us,'guard_minimum_ms_under_clock_assumption':minimum_guard_seconds*1000,'scope':'Cold power-on only; exact capacitor, clock and hot-plug behavior unverified'}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
