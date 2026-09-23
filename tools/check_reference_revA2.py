#!/usr/bin/env python3
"""Read-only, fresh-fill geometry audit. Run with KiCad's wx-enabled Python."""
import argparse, hashlib, json, math
from pathlib import Path
import wx
app = wx.App(False)
import pcbnew as k

p = argparse.ArgumentParser()
p.add_argument('board', type=Path)
p.add_argument('--baseline', type=Path)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()

def load_filled(path):
    board = k.LoadBoard(str(path.resolve()))
    filler = k.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.BuildConnectivity()
    planes = [z for z in board.Zones() if z.GetLayer() == k.In1_Cu and z.GetNetname() == '/GND' and not z.GetIsRuleArea()]
    if len(planes) != 1:
        raise RuntimeError('Expected exactly one In1 GND zone')
    return board, planes[0].GetFilledPolysList(k.In1_Cu)

def sample(track, edges=False):
    x, z = track.GetStart(), track.GetEnd()
    length = math.hypot(z.x-x.x, z.y-x.y)
    n = max(1, math.ceil(length/k.FromMM(.05)))
    nx, ny = (-(z.y-x.y)/length, (z.x-x.x)/length) if length else (0, 0)
    for j in range(n+1):
        for offset in [-track.GetWidth()/2, 0, track.GetWidth()/2] if edges else [0]:
            yield k.VECTOR2I(round(x.x+(z.x-x.x)*j/n+nx*offset), round(x.y+(z.y-x.y)*j/n+ny*offset))

b, ground = load_filled(a.board)
tracks = list(b.GetTracks())
report = {'board': str(a.board.resolve()), 'sha256': hashlib.sha256(a.board.read_bytes()).hexdigest(),
          'fresh_zone_fill_before_analysis': True, 'board_file_written': False,
          'in1_ground_outlines': ground.OutlineCount(), 'critical': {}, 'failures': [],
          'scope': 'Digital geometry only. Same-layer outline connectivity and sampled reference coverage do not prove electromagnetic return paths.'}
if ground.OutlineCount() != 1:
    report['failures'].append('In1 GND is split into multiple filled outlines')
for name in ['/LSE_IN', '/LSE_OUT', '/BRIDGE_A+', '/BRIDGE_A-', '/AIN_P_FILT', '/AIN_N_FILT']:
    ts = [t for t in tracks if t.GetNetname() == name]
    via_count = sum(isinstance(t, k.PCB_VIA) for t in ts)
    if not ts or via_count or any(t.GetLayer() != k.F_Cu for t in ts):
        report['failures'].append(name + ': missing route or not zero-via F.Cu')
    gaps = []; count = 0
    for t in ts:
        if isinstance(t, k.PCB_VIA): continue
        for q in sample(t, edges=True):
            count += 1
            if not ground.Contains(q): gaps.append(list(k.ToMM(q)))
    report['critical'][name] = {'samples_with_trace_edges': count, 'vias': via_count, 'missing': gaps}
    if gaps: report['failures'].append(name + ': reference samples outside freshly filled In1 GND')
if a.baseline:
    old, old_ground = load_filled(a.baseline)
    old_tracks = {t.m_Uuid.AsString(): t for t in old.GetTracks()}
    losses = []
    for t in tracks:
        if isinstance(t, k.PCB_VIA) or t.GetLayer() not in [k.F_Cu,k.B_Cu] or t.GetNetname() == '/GND': continue
        previous = old_tracks.get(t.m_Uuid.AsString())
        if previous is None or previous.GetStart() != t.GetStart() or previous.GetEnd() != t.GetEnd(): continue
        gaps = [list(k.ToMM(q)) for q in sample(t, edges=True) if old_ground.Contains(q) and not ground.Contains(q)]
        if gaps: losses.append({'net':t.GetNetname(), 'layer':t.GetLayerName(), 'uuid':t.m_Uuid.AsString(), 'new_missing_samples':gaps})
    report['baseline_sha256'] = hashlib.sha256(a.baseline.read_bytes()).hexdigest()
    report['new_reference_losses_on_unchanged_outer_tracks'] = losses
    if losses: report['failures'].append('New reference gaps on unchanged outer copper require disposition')
report['status'] = 'GEOMETRY_REVIEW_REQUIRED' if report['failures'] else 'PASS_SAMPLED_GEOMETRY_ONLY'
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'status':report['status'], 'in1_ground_outlines':ground.OutlineCount(), 'failures':report['failures'], 'output':str(a.output)}, indent=2))
raise SystemExit(2 if report['failures'] else 0)
