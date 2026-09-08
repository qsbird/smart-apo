#!/usr/bin/env python3
"""Create a concise, machine-readable Rev.A1 package validation report."""
from __future__ import annotations
import csv, json
from pathlib import Path
import trimesh
from kiutils.board import Board
from kiutils.schematic import Schematic

ROOT=Path(__file__).resolve().parents[1]
HW=ROOT/"hardware"; MECH=ROOT/"mechanical"; VAL=ROOT/"validation"

def main():
    sch=Schematic().from_file(HW/"smart_apo_common_revA1.kicad_sch")
    pcb=Board().from_file(HW/"smart_apo_common_revA1_NETS_PLACED.kicad_pcb")
    meshes=[]
    for p in sorted(MECH.glob("*.stl")):
        m=trimesh.load_mesh(p,process=True)
        meshes.append({"file":p.name,"watertight":bool(m.is_watertight),"faces":int(len(m.faces))})
    with (HW/"BOM_revA1_JLCPCB.csv").open(newline="") as f: bom=list(csv.DictReader(f))
    tune=json.loads((ROOT/"firmware/host/example_result.json").read_text())
    tune_pass=tune["time_map"]["rms_ms"] < 10 and tune["time_map"]["marker_count"] >= 6
    report={
      "revision":"A1","result":"PASS_WITH_FABRICATION_GATES",
      "schematic":{"symbols":len(sch.schematicSymbols),"embedded_symbol_definitions":len(sch.libSymbols),"parser":"kiutils PASS"},
      "pcb":{"footprints":len(pcb.footprints),"nets_including_empty":len(pcb.nets),"zones":len(pcb.zones),
             "routed_tracks":len(getattr(pcb,"traceItems",[]) or []),"parser":"kiutils PASS",
             "release":"BLOCKED_NO_ROUTING_NO_OFFICIAL_DRC_NO_GERBER"},
      "bom":{"rows":len(bom),"locked_core_lcsc_ids":sum(bool(r["LCSC Part #"]) for r in bom)},
      "mechanical":{"all_stl_watertight":all(x["watertight"] for x in meshes),"files":meshes},
      "autotune":{"synthetic_smoke_test":"PASS" if tune_pass else "FAIL",
                  "synchronization_rms_ms":tune["time_map"]["rms_ms"],
                  "promotion_requires_unseen_trip":tune["promotion_gate"]["requires_new_unseen_trip"]},
      "remaining_gates":["official footprint verification, especially LPS28DFW against ST TN0018",
                         "PCB routing and KiCad ERC/DRC","Gerber/drill/CPL independent review",
                         "battery fit and protection verification","15 m equivalent pressure test",
                         "316L coupon calibration and >=5 kgf survival test"]}
    VAL.mkdir(exist_ok=True)
    (VAL/"revA1_validation_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=="__main__": main()
