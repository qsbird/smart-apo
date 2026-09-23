"""Report pre-link ARM resource evidence; never claim a full stack bound."""
import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--build', type=Path, required=True)
parser.add_argument('--llvm-bin', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
a = parser.parse_args()
reports = []
for variant in (0, 1):
    objects = sorted((a.build / f'variant{variant}').glob('*/*.o'))
    assert len(objects) == 10, (variant, len(objects))
    frames, graph, sections, artifacts, indirect = {}, {}, [], [], []
    call_count = relocation_count = 0
    for obj in objects:
        raw = obj.read_bytes()
        assert raw[:6] == b'\x7fELF\x01\x01'
        header = struct.unpack_from('<HHIIIIIHHHHHH', raw, 16)
        assert header[0:2] == (1, 40)
        shoff, shsize, shnum, shstr = header[5], header[10], header[11], header[12]
        assert shsize == 40 and shoff + shsize * shnum <= len(raw)
        sh = [struct.unpack_from('<IIIIIIIIII', raw, shoff + i * shsize) for i in range(shnum)]
        names = raw[sh[shstr][4]:sh[shstr][4]+sh[shstr][5]]
        for entry in sh:
            name = names[entry[0]:].split(b'\0', 1)[0].decode()
            if entry[2] & 2 and entry[5]:
                sections.append({'object':str(obj), 'name':name, 'size':entry[5],
                                 'alignment':entry[8], 'writable':bool(entry[2] & 1),
                                 'nobits':entry[1] == 8})
        for line in obj.with_suffix('.su').read_text().splitlines():
            location, count, kind = line.split('\t')
            function = location.rsplit(':', 1)[1]
            key = (str(obj), function)
            assert key not in frames
            frames[key] = {'bytes':int(count), 'kind':kind, 'source':location}
        dis = subprocess.check_output([str(a.llvm_bin/'llvm-objdump'), '-dr', str(obj)], text=True)
        obj.with_suffix('.disassembly.txt').write_text(dis)
        current = None
        for line in dis.splitlines():
            m = re.match(r'Disassembly of section \.text\.([^:]+):', line)
            if m:
                current = (str(obj), m[1]); graph.setdefault(current, set())
            m = re.search(r'R_ARM_THM_(?:CALL|JUMP\d+)\s+(\S+)', line)
            if m and current:
                graph[current].add(m[1]); relocation_count += 1
            if re.search(r'\tbl(?:x)?\s+', line):
                call_count += 1
                if re.search(r'\tblx\s+r\d+', line):
                    indirect.append({'object':str(obj), 'function':current, 'instruction':line.strip()})
        artifacts.append({'object':str(obj), 'sha256':hashlib.sha256(raw).hexdigest(),
                          'stack_usage_sha256':hashlib.sha256(obj.with_suffix('.su').read_bytes()).hexdigest()})
    by_name = {}
    for key in frames:
        by_name.setdefault(key[1], []).append(key)
    unresolved, cycles, cache = set(), [], {}
    def longest(key, active=()):
        if key in active:
            cycles.append([x[1] for x in active + (key,)])
            return 0, []
        if key in cache:
            return cache[key]
        own = frames.get(key)
        if own is None:
            unresolved.add(key[1]); return 0, [key[1] + ' [unknown frame]']
        best = (0, [])
        for target in graph.get(key, set()):
            candidates = [key2 for key2 in by_name.get(target, []) if key2[0] == key[0]] or by_name.get(target, [])
            if len(candidates) == 1:
                child = longest(candidates[0], active + (key,))
            else:
                unresolved.add(target); child = (0, [target + ' [unknown frame]'])
            if child[0] > best[0]:
                best = child
        result = (own['bytes'] + best[0], [key[1]] + best[1]); cache[key] = result
        return result
    roots = {}
    for name in ['Reset_Handler', 'main']:
        key, = by_name[name]
        size, chain = longest(key)
        roots[name] = {'known_frame_sum_bytes':size, 'chain':chain}
    # Scan every emitted function too, so unused/helper references are not hidden.
    for key in frames:
        longest(key)
    writable = [s for s in sections if s['writable']]
    report = {'variant':variant, 'objects':artifacts,
              'static_ram_section_bytes_before_link':sum(s['size'] for s in writable),
              'static_ram_sum_with_per_section_max_alignment_slack':sum(s['size']+max(0,s['alignment']-1) for s in writable),
              'read_only_allocated_section_bytes_before_link':sum(s['size'] for s in sections if not s['writable']),
              'section_inventory':sections, 'function_frame_count':len(frames),
              'largest_frames':sorted([{'function':k[1], **v} for k,v in frames.items()], key=lambda x:x['bytes'], reverse=True)[:12],
              'nonstatic_frames':[{'function':k[1],**v} for k,v in frames.items() if v['kind']!='static'],
              'known_direct_call_paths':roots, 'unknown_callee_frames':sorted(unresolved),
              'recursive_cycles':cycles, 'indirect_call_instructions':indirect,
              'disassembled_call_instructions':call_count, 'call_or_tail_jump_relocations':relocation_count,
              'full_stack_bound_verified':False,
              'limits':'Unlinked emitted-object evidence. Includes no external runtime frame sizes, exception entry/nesting, linker veneers, final section placement, or hardware watermark. Tail jumps conservatively retain caller frames. Known path sum is not an end-to-end upper bound.'}
    reports.append(report)
root = Path(__file__).resolve().parents[1]
source_files = [root/'Makefile'] + sorted((root/'src').glob('*.c')) + sorted((root/'include').glob('*.h')) + sorted((root/'runtime').rglob('*.c')) + sorted((root/'runtime').rglob('*.h')) + sorted((root/'runtime').glob('*.ld'))
result = {'status':'PRELINK_RESOURCE_EVIDENCE_ONLY', 'compiler':subprocess.check_output([str(a.llvm_bin/'clang'),'--version'],text=True).strip(),
          'sources':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}, 'variants':reports}
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps([{k:v for k,v in r.items() if k in ['variant','static_ram_section_bytes_before_link','static_ram_sum_with_per_section_max_alignment_slack','read_only_allocated_section_bytes_before_link','known_direct_call_paths','unknown_callee_frames','recursive_cycles','indirect_call_instructions','disassembled_call_instructions','call_or_tail_jump_relocations']} for r in reports],indent=2))
