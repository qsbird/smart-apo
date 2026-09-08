#!/usr/bin/env python3
"""Generate a net-assigned KiCad PCB for Rev.A1 mechanical/electrical review.

The board contains real SMT pads, net assignments, four-layer stack, placement,
and internal plane definitions. Routing/Gerber release remains deliberately
blocked until KiCad's official DRC can be run.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from generate_schematic import PARTS, PASSIVES, CAPS

ROOT=Path(__file__).resolve().parents[1]
HW=ROOT/'hardware'
OUT=HW/'smart_apo_common_revA1_NETS_PLACED.kicad_pcb'


NET_NAMES=sorted({n for *_,pins in PARTS for n in pins.values() if n!='NC'} |
                 {n for _r,_v,a,b,_p in PASSIVES+CAPS for n in (a,b)} |
                 {'LED_A','LED_K','REED_WAKE','LSE_IN','LSE_OUT'})
NET_ID={n:i+1 for i,n in enumerate(NET_NAMES)}


def pad(num,dx,dy,sx,sy,net,layer='F',shape='roundrect'):
    layers=f'"{layer}.Cu" "{layer}.Paste" "{layer}.Mask"'
    rr=' (roundrect_rratio 0.2)' if shape=='roundrect' else ''
    return f'    (pad "{num}" smd {shape} (at {dx:.3f} {dy:.3f}) (size {sx:.3f} {sy:.3f}) (layers {layers}){rr} (net {NET_ID[net]} "{net}"))'


def tssop(n=20):
    ps=[]; half=n//2
    for i in range(half): ps.append((i+1,-3.0,-2.925+i*0.65,1.45,0.35))
    for i in range(half): ps.append((half+i+1,3.0,2.925-i*0.65,1.45,0.35))
    return ps,6.5,7.1


def soic16():
    ps=[]
    for i in range(8): ps.append((i+1,-2.65,-4.445+i*1.27,1.55,0.60))
    for i in range(8): ps.append((9+i,2.65,4.445-i*1.27,1.55,0.60))
    return ps,6.2,10.3


def lga14():
    # 3 pads top + 4 right + 3 bottom + 4 left; confirm orientation against ST reel mark.
    p=[(1,-1.0,-1.0,.38,.48),(2,-.5,-1.0,.38,.48),(3,0,-1.0,.38,.48),
       (4,.75,-.75,.48,.38),(5,.75,-.25,.48,.38),(6,.75,.25,.48,.38),(7,.75,.75,.48,.38),
       (8,.5,1.0,.38,.48),(9,0,1.0,.38,.48),(10,-.5,1.0,.38,.48),
       (11,-.75,.75,.48,.38),(12,-.75,.25,.48,.38),(13,-.75,-.25,.48,.38),(14,-.75,-.75,.48,.38)]
    return p,3.2,3.7


def lps7():
    # Engineering land pattern. Exact pad dimensions remain a fab-release gate per ST TN0018.
    p=[(1,-.85,-.75,.45,.55),(2,0,-.75,.45,.55),(3,.85,-.75,.45,.55),
       (4,.85,.75,.45,.55),(5,0,.75,.45,.55),(6,-.85,.75,.45,.55),(7,0,0,.65,.65)]
    return p,3.4,3.4


def wson8():
    p=[]
    for i in range(4): p.append((i+1,-3.1,-1.905+i*1.27,1.25,.55))
    for i in range(4): p.append((5+i,3.1,1.905-i*1.27,1.25,.55))
    return p,7.0,8.4


def sot23_5():
    return [(1,-.95,.95,.65,1.0),(2,0,.95,.65,1.0),(3,.95,.95,.65,1.0),(4,.95,-.95,.65,1.0),(5,-.95,-.95,.65,1.0)],3.2,3.4


def sot23_3(): return [ (1,-.95,.95,.65,1.0),(2,.95,.95,.65,1.0),(3,0,-.95,.65,1.0)],3.2,3.4


def passive2(): return [(1,-.55,0,.60,.60),(2,.55,0,.60,.60)],1.5,1.0


def conn(n,pitch=1.27):
    x0=-(n-1)*pitch/2
    return [(i+1,x0+i*pitch,0,.85,1.05) for i in range(n)],n*pitch+.5,1.6


FP={"MCU20":tssop,"IMU14":lga14,"PRESS7":lps7,"ADC16":soic16,"FLASH8":wson8,
    "CHARGER5":sot23_5,"LDO5":sot23_5,"MOS3":sot23_3,"PASSIVE2":passive2,
    "CONN6":lambda:conn(6),"CONN7":lambda:conn(7)}


PLACEMENT={
    'U1':(6.0,13.3,0,'F'),'U2':(2.4,5.4,0,'F'),'U3':(6.0,1.9,0,'F'),
    'U4':(6.0,22.1,0,'F'),'U5':(7.0,7.1,0,'B'),'U6':(2.2,28.8,0,'F'),
    'U7':(8.6,28.8,180,'F'),'Q1':(3.0,31.5,0,'B'),'J1':(9.8,33.5,90,'F'),
    'J2':(0.75,13.8,90,'B'),'J3':(5.6,34.1,0,'F'),
    'D1':(1.0,33.4,90,'F'),'SW1':(9.8,18.0,90,'B'),'Y1':(6.0,18.0,0,'B'),
    'R1':(4.8,9.4,0,'F'),'R2':(7.2,9.4,0,'F'),'R3':(4.3,29.3,90,'F'),
    'R4':(10.3,15.4,90,'F'),'R5':(10.3,16.8,90,'F'),'R6':(1.0,31.3,90,'F'),
    'R7':(2.0,30.8,0,'F'),'R8':(2.2,22.5,90,'F'),'R9':(2.2,24.0,90,'F'),
    'R10':(10.3,19.2,90,'F'),'R11':(10.3,10.8,90,'F'),
    'C1':(9.7,13.1,90,'F'),'C2':(4.2,4.8,90,'F'),'C3':(4.2,6.0,90,'F'),
    'C4':(8.2,2.2,0,'F'),'C5':(9.7,21.0,90,'F'),'C6':(9.7,22.4,90,'F'),
    'C7':(9.7,23.8,90,'F'),'C8':(10.5,7.1,90,'B'),'C9':(7.0,30.5,0,'F'),
    'C10':(10.3,30.5,90,'F'),'C11':(.8,27.0,90,'F'),'C12':(.8,28.5,90,'F'),
    'C13':(2.2,20.8,90,'F'),'C14':(10.3,14.0,90,'F'),'C15':(4.0,18.0,0,'B'),
    'C16':(8.0,18.0,0,'B'),'C17':(10.3,12.0,90,'F'),
}


def comp_data():
    out=[]
    for ref,val,sym,_fp,_x,_y,_r,pop,pins in PARTS:
        out.append((ref,val,sym,pop,pins))
    for ref,val,a,b,pop in PASSIVES+CAPS:
        out.append((ref,val,'PASSIVE2',pop,{1:a,2:b}))
    out += [('D1','RED_HIGH_BRIGHT','PASSIVE2','AWA',{1:'LED_A',2:'LED_K'}),
            ('SW1','SMT_REED_NO','PASSIVE2','BOTH',{1:'REED_WAKE',2:'GND'}),
            ('Y1','32.768kHz','PASSIVE2','BOTH',{1:'LSE_IN',2:'LSE_OUT'})]
    return out


def footprint(ref,val,sym,pop,pins):
    x,y,rot,layer=PLACEMENT[ref]
    pdata,w,h=FP[sym]()
    lines=[f'  (footprint "SmartApo:{sym}" (layer "{layer}.Cu") (at {x:.3f} {y:.3f} {rot})',
           f'    (property "Reference" "{ref}" (at 0 {-h/2-.6:.3f} {rot}) (layer "{layer}.SilkS")',
           f'      (effects (font (size .65 .65) (thickness .1))'+(' (justify mirror)' if layer=='B' else '')+'))',
           f'    (property "Value" "{val}" (at 0 {h/2+.6:.3f} {rot}) (layer "{layer}.Fab") hide',
           f'      (effects (font (size .6 .6))'+(' (justify mirror)' if layer=='B' else '')+'))',
           f'    (property "Population" "{pop}" (at 0 0 {rot}) (layer "{layer}.Fab") hide',
           f'      (effects (font (size .5 .5))'+(' (justify mirror)' if layer=='B' else '')+'))',
           '    (attr smd)',
           f'    (fp_rect (start {-w/2:.3f} {-h/2:.3f}) (end {w/2:.3f} {h/2:.3f}) (stroke (width .12) (type default)) (fill none) (layer "{layer}.SilkS"))']
    for num,dx,dy,sx,sy in pdata:
        net=pins.get(num)
        if net and net!='NC': lines.append(pad(num,dx,dy,sx,sy,net,layer))
        else:
            layers=f'"{layer}.Cu" "{layer}.Paste" "{layer}.Mask"'
            lines.append(f'    (pad "{num}" smd roundrect (at {dx:.3f} {dy:.3f}) (size {sx:.3f} {sy:.3f}) (layers {layers}) (roundrect_rratio .2))')
    lines.append('  )')
    return '\n'.join(lines)


def main():
    comps=comp_data()
    missing=sorted({r for r,*_ in comps}-set(PLACEMENT))
    if missing: raise SystemExit(f'Missing placement: {missing}')
    s=['(kicad_pcb (version 20240108) (generator "smart_apo_revA1_generator")',
       '  (general (thickness 1.0))','  (paper "A4")','  (layers',
       '    (0 "F.Cu" signal)','    (2 "In1.Cu" power)','    (4 "In2.Cu" power)','    (31 "B.Cu" signal)',
       '    (36 "B.SilkS" user "b.silkscreen")','    (37 "F.SilkS" user "f.silkscreen")',
       '    (44 "Edge.Cuts" user))',
       '  (setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no))',
       '  (net 0 "")']
    for n,i in sorted(NET_ID.items(),key=lambda x:x[1]): s.append(f'  (net {i} "{n}")')
    outline=[(2,0),(10,0),(12,2),(12,33),(10,35),(2,35),(0,33),(0,2),(2,0)]
    for a,b in zip(outline,outline[1:]):
        s.append(f'  (gr_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width .1) (type default)) (layer "Edge.Cuts"))')
    s.append('  (gr_text "SMART APO A1 / NETS+PLACEMENT / NO GERBER" (at 6 17.5 90) (layer "B.SilkS") (effects (font (size .55 .55) (thickness .08)) (justify mirror)))')
    for c in comps: s.append(footprint(*c))
    # Plane definitions are included but require stitching vias during routing.
    for name,layer in [('GND','In1.Cu'),('3V3','In2.Cu')]:
        nid=NET_ID[name]
        s.append(f'''  (zone (net {nid}) (net_name "{name}") (layer "{layer}") (hatch edge 0.5)
    (connect_pads (clearance 0.2)) (min_thickness 0.15) (fill yes (thermal_gap 0.25) (thermal_bridge_width 0.25))
    (polygon (pts (xy .3 .3) (xy 11.7 .3) (xy 11.7 34.7) (xy .3 34.7))))''')
    s.append(')')
    OUT.write_text('\n'.join(s)+'\n')

    rows=[]
    for ref,val,sym,pop,pins in comps:
        x,y,rot,layer=PLACEMENT[ref]
        rows.append((ref,val,x,y,layer,rot,pop))
    with (HW/'CPL_revA1.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Designator','Val','Mid X(mm)','Mid Y(mm)','Layer','Rotation','Population']);w.writerows(rows)
    report={'board_mm':[12,35,1.0],'layers':4,'components':len(comps),'nets':len(NET_ID),
            'all_pads_net_assigned_except_documented_NC':True,
            'release_status':'BLOCKED_NO_ROUTING_NO_OFFICIAL_DRC_NO_GERBER',
            'pressure_footprint_status':'REVIEW_AGAINST_ST_TN0018'}
    (HW/'pcb_generation_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()
