#!/usr/bin/env python3
"""Generate Rev.A1 mechanical meshes, drawings and checks.

The script is deterministic.  It deliberately does not generate Gerbers: the PCB
must first be opened in KiCad and pass the official ERC/DRC release gate.
"""

from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon


ROOT = Path(__file__).resolve().parents[1]
MECH = ROOT / "mechanical"
HW = ROOT / "hardware"
CHECKS = ROOT / "validation"


def box(extents, center=(0, 0, 0)):
    m = trimesh.creation.box(extents=extents)
    m.apply_translation(center)
    return m


def cyl(radius, height, center=(0, 0, 0), axis="z", sections=64):
    m = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    if axis == "x":
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    elif axis == "y":
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    m.apply_translation(center)
    return m


def union(meshes):
    return trimesh.boolean.union(meshes, engine="manifold")


def difference(a, subtractors):
    return trimesh.boolean.difference([a, *subtractors], engine="manifold")


def intersection(meshes):
    return trimesh.boolean.intersection(meshes, engine="manifold")


def ellipsoid(rx, ry, rz, center=(0, 0, 0), subdivisions=4):
    m = trimesh.creation.icosphere(subdivisions=subdivisions, radius=1.0)
    m.apply_scale([rx, ry, rz])
    m.apply_translation(center)
    return m


def export_mesh(mesh, name):
    mesh.remove_unreferenced_vertices()
    mesh.process(validate=True)
    mesh.export(MECH / name)
    return {
        "file": name,
        "watertight": bool(mesh.is_watertight),
        "volume_mm3": round(abs(float(mesh.volume)), 2),
        "bounds_mm": np.round(mesh.bounds, 3).tolist(),
        "faces": int(len(mesh.faces)),
    }


def make_awa():
    # Datum: float centre at z=0; total envelope 32 x 49 mm.
    outer = ellipsoid(16.0, 16.0, 24.5)
    lower_clip = box((50, 50, 50), (0, 0, -10.0))  # top at z=15
    lower = intersection([outer, lower_clip])

    # Electronics cavity; leaves at least 1.2 mm wall and a 1.7 mm bottom floor.
    cavity = ellipsoid(14.6, 14.6, 22.8, center=(0, 0, 0.2))
    cavity = intersection([cavity, box((40, 40, 45), (0, 0, -2.5))])
    lower = difference(lower, [cavity])

    # 316L axial wire feedthrough and side pressure port. Both are epoxy-sealed.
    lower = difference(lower, [
        cyl(0.75, 60, axis="z"),
        cyl(1.65, 12, center=(12.0, 0, -7.5), axis="x"),
    ])

    # Upper ellipsoidal cap plus an annular bonding/O-ring spigot.
    cap_clip = box((50, 50, 20), (0, 0, 20.0))  # bottom at z=10
    cap_outer = intersection([outer, cap_clip])
    cap_inner = ellipsoid(14.6, 14.6, 22.8, center=(0, 0, 0.2))
    cap_inner = intersection([cap_inner, box((40, 40, 16), (0, 0, 15.5))])
    cap = difference(cap_outer, [cap_inner])
    spigot = difference(cyl(11.55, 4.0, center=(0, 0, 14.0)), [cyl(9.55, 6.0, center=(0, 0, 14.0))])
    cap = union([cap, spigot])
    cap = difference(cap, [
        cyl(0.75, 35, axis="z"),
        cyl(1.55, 20, center=(5.8, 0, 19), axis="z"),
        cyl(0.65, 20, center=(-5.0, -2.1, 19), axis="z"),
        cyl(0.65, 20, center=(-2.8, -2.1, 19), axis="z"),
        cyl(0.65, 20, center=(-0.6, -2.1, 19), axis="z"),
        cyl(0.65, 20, center=(1.6, -2.1, 19), axis="z"),
    ])

    # Removable electronics sled; board on one side, pouch cell on the other.
    sled = union([
        box((12.6, 1.0, 35.6), (-4.2, 0, -1.5)),
        box((1.0, 2.4, 35.6), (-10.0, 0.7, -1.5)),
        box((1.0, 2.4, 35.6), (1.6, 0.7, -1.5)),
        box((9.5, 1.0, 30.0), (5.8, 0, -3.5)),
    ])

    return [
        export_mesh(lower, "awa_body_32x49_revA.stl"),
        export_mesh(cap, "awa_cap_revA.stl"),
        export_mesh(sled, "awa_electronics_sled_revA.stl"),
    ]


def capsule(radius=10.0, straight=50.0):
    body = cyl(radius, straight, axis="z")
    top = trimesh.creation.icosphere(subdivisions=3, radius=radius)
    bottom = top.copy()
    top.apply_translation((0, 0, straight / 2))
    bottom.apply_translation((0, 0, -straight / 2))
    return union([body, top, bottom])


def make_underwater():
    # Ø20 x 70 mm wet-envelope. Four transverse bosses bring local width to 24 mm.
    shell = capsule(10.0, 50.0)
    bosses = []
    for x in (-7.2, 7.2):
        for z in (-17.0, 17.0):
            bosses.append(cyl(2.6, 24.0, center=(x, 0, z), axis="y"))
    shell = union([shell, *bosses])

    cavity = box((13.2, 8.0, 43.0), (0, 0, 0))
    beam_slot = box((7.0, 1.0, 76.0), (0, 0, 0))
    port = cyl(1.65, 10.0, center=(8.0, 0, -7.0), axis="x")
    screw_holes = [cyl(1.1, 28, center=(x, 0, z), axis="y")
                   for x in (-7.2, 7.2) for z in (-17.0, 17.0)]
    shell = difference(shell, [cavity, beam_slot, port, *screw_holes])

    half_a = intersection([shell, box((50, 50, 90), (0, -25.01, 0))])
    half_b = intersection([shell, box((50, 50, 90), (0, 25.01, 0))])

    # Small ballast cassette for measured trim mass, mounted near lower end.
    cassette = difference(box((9.0, 5.5, 12.0)), [box((7.2, 4.0, 10.5), (0, 0, 0.8))])
    cassette.apply_translation((0, 0, -14.0))

    return [
        export_mesh(half_a, "underwater_fairing_half_A_revA.stl"),
        export_mesh(half_b, "underwater_fairing_half_B_revA.stl"),
        export_mesh(cassette, "underwater_ballast_cassette_revA.stl"),
    ]


def make_flexure():
    # Laser-cut 316L, 0.30 mm sheet. Axial dog-bone for Rev.A characterization.
    pts = [
        (-4, -39), (4, -39), (4, -29), (2.5, -24), (1.2, -18),
        (0.75, -11), (0.75, 11), (1.2, 18), (2.5, 24), (4, 29),
        (4, 39), (-4, 39), (-4, 29), (-2.5, 24), (-1.2, 18),
        (-0.75, 11), (-0.75, -11), (-1.2, -18), (-2.5, -24), (-4, -29),
    ]
    beam = trimesh.creation.extrude_polygon(Polygon(pts), height=0.30, engine="earcut")
    holes = [cyl(1.6, 1.0, center=(0, y, 0.15), axis="z") for y in (-33.5, 33.5)]
    beam = difference(beam, holes)
    report = export_mesh(beam, "316L_flexure_preview_NOT_FOR_PRINTING.stl")

    # Minimal R12 ASCII DXF profile; units are millimetres.
    dxf = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC",
           "0", "SECTION", "2", "ENTITIES"]
    closed = pts + [pts[0]]
    for a, b in zip(closed, closed[1:]):
        dxf += ["0", "LINE", "8", "CUT", "10", str(a[0]), "20", str(a[1]), "30", "0",
                "11", str(b[0]), "21", str(b[1]), "31", "0"]
    for y in (-33.5, 33.5):
        dxf += ["0", "CIRCLE", "8", "CUT", "10", "0", "20", str(y), "30", "0", "40", "1.6"]
    dxf += ["0", "ENDSEC", "0", "EOF"]
    (MECH / "316L_flexure_0p30mm_revA.dxf").write_text("\n".join(dxf) + "\n")
    return [report]


PARTS = [
    # ref, value/mpn, footprint, x, y, rotation, population
    ("U1", "STM32U031F8P6", "TSSOP-20_4.4x6.5mm_P0.65", 6.0, 15.0, 0, "BOTH"),
    ("U2", "LSM6DSOTR", "LGA-14_2.5x3.0mm_P0.5", 3.0, 7.0, 0, "BOTH"),
    ("U3", "LPS28DFWTR", "CCLGA-7_2.8x2.8mm", 8.4, 3.2, 0, "BOTH"),
    ("U4", "NAU7802SGI", "SOP-16_3.9x9.9mm_P1.27", 6.0, 22.5, 90, "UNDERWATER"),
    ("U5", "W25Q256JVEIQ", "WSON-8_6x5mm_P1.27", 7.6, 8.8, 0, "BOTH"),
    ("U6", "MCP73831T-2ACI/OT", "SOT-23-5", 2.5, 28.1, 0, "BOTH"),
    ("U7", "TPS7A0233PDBVR", "SOT-23-5", 8.5, 28.1, 180, "BOTH"),
    ("Q1", "DMN1019USN-7", "SOT-23", 2.2, 31.0, 0, "AWA"),
    ("D1", "LTST-C170KRKT_RED", "LED_0805", 4.8, 31.0, 0, "AWA"),
    ("J1", "BATTERY_WIRE_PADS", "PAD_2x1.5mm", 8.6, 31.0, 0, "BOTH"),
    ("J2", "SWD_UART_CHARGE_POGO", "POGO_7x1.27mm", 6.0, 33.4, 0, "BOTH"),
    ("J3", "FULL_BRIDGE_6WIRE", "PAD_6x1.0mm", 6.0, 1.0, 0, "UNDERWATER"),
    ("SW1", "SMT_REED_MK24", "Reed_SMD_5.0x1.8mm", 10.5, 16.5, 90, "BOTH"),
]


def write_bom_and_cpl():
    bom = HW / "BOM_revA.csv"
    with bom.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Reference", "Qty", "Manufacturer part number", "Footprint", "Populate on", "Notes"])
        for ref, val, fp, *_xy, pop in PARTS:
            notes = "Critical wet-side part; do not substitute" if ref == "U3" else "Verify supplier stock before assembly"
            w.writerow([ref, 1, val, fp, pop, notes])
        w.writerows([
            ["R1-R2", 2, "4.7k 0402 1%", "0402", "BOTH", "I2C pullups"],
            ["R3", 1, "20k 0402 1%", "0402", "BOTH", "50mA charge current"],
            ["R4-R5", 2, "1M/330k 0402 1%", "0402", "BOTH", "Battery divider; switched by GPIO"],
            ["R6", 1, "1k 0402 1%", "0402", "AWA", "LED gate series"],
            ["R7", 1, "100k 0402 1%", "0402", "AWA", "LED gate pulldown"],
            ["C1-C8", 8, "100nF 0402 X7R 10V", "0402", "BOTH", "Local decoupling"],
            ["C9-C12", 4, "4.7uF 0603 X5R 10V", "0603", "BOTH", "Rail bulk capacitors"],
            ["R8-R11", 4, "100R 0402 0.1%", "0402", "UNDERWATER", "Bridge input EMI/filter network"],
            ["C13-C14", 2, "10nF 0402 C0G", "0402", "UNDERWATER", "Bridge differential/common filters"],
        ])

    with (HW / "CPL_revA.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X(mm)", "Mid Y(mm)", "Layer", "Rotation", "Populate on"])
        for ref, _val, _fp, x, y, rot, pop in PARTS:
            w.writerow([ref, x, y, "Top", rot, pop])


NETS = [
    ("3V3", "U1.VDD U2.VDD U2.VDDIO U3.VDD U4.DVDD U4.AVDD U5.VCC"),
    ("GND", "U1.VSS U2.GND U3.GND U4.AGND U4.DGND U5.GND U6.VSS U7.GND"),
    ("I2C_SCL", "U1.PB6 U2.SCL U3.SCL U4.SCLK"),
    ("I2C_SDA", "U1.PB7 U2.SDA U3.SDA U4.SDAT"),
    ("IMU_INT", "U1.PA0 U2.INT1"),
    ("PRESS_INT", "U1.PC15 U3.INT_DRDY"),
    ("STRAIN_DRDY", "U1.PC14 U4.DRDY"),
    ("FLASH_CS", "U1.PA4 U5.CS"),
    ("SPI_SCK", "U1.PA5 U5.CLK"),
    ("SPI_MISO", "U1.PA6 U5.DO"),
    ("SPI_MOSI", "U1.PA7 U5.DI"),
    ("LED_GATE", "U1.PB0 R6.1 Q1.G"),
    ("VBAT_SENSE", "U1.PA1 R4.2 R5.1"),
    ("UART_TX", "U1.PA2 J2.5"),
    ("UART_RX", "U1.PA3 J2.6"),
    ("SWDIO", "U1.PA13 J2.3"),
    ("SWCLK", "U1.PA14 J2.4"),
    ("NRST", "U1.NRST J2.7"),
    ("VBAT", "J1.1 SW1.1 U6.VBAT"),
    ("VBAT_SW", "SW1.2 U7.IN"),
    ("CHARGE_IN", "J2.2 U6.VDD"),
    ("BRIDGE_E+", "J3.1 U4.REFP"),
    ("BRIDGE_E-", "J3.2 U4.REFN"),
    ("BRIDGE_A+", "J3.3 U4.VIN1P"),
    ("BRIDGE_A-", "J3.4 U4.VIN1N"),
]


def write_connectivity():
    with (HW / "connectivity_revA.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Net", "Connected pins"])
        w.writerows(NETS)


def kicad_fp(ref, value, x, y, rot, width, height):
    return f'''  (footprint "SmartApo:{ref}" (layer "F.Cu") (at {x:.3f} {y:.3f} {rot})
    (property "Reference" "{ref}" (at 0 {-height/2-0.8:.3f} {rot}) (layer "F.SilkS"))
    (property "Value" "{value}" (at 0 {height/2+0.8:.3f} {rot}) (layer "F.Fab"))
    (fp_rect (start {-width/2:.3f} {-height/2:.3f}) (end {width/2:.3f} {height/2:.3f})
      (stroke (width 0.15) (type default)) (fill none) (layer "F.SilkS"))
    (fp_circle (center {-width/2+0.35:.3f} {-height/2+0.35:.3f}) (end {-width/2+0.55:.3f} {-height/2+0.35:.3f})
      (stroke (width 0.12) (type default)) (fill none) (layer "F.SilkS"))
  )\n'''


def write_kicad_placement():
    # This opens as a four-layer placement/mechanical review board. Pads/tracks are
    # intentionally not emitted: release is blocked until symbol-footprint mapping
    # is verified in KiCad against the chosen assembly vendor libraries.
    dims = {
        "U1": (6.4, 6.5), "U2": (3.0, 2.5), "U3": (2.8, 2.8), "U4": (6.2, 10.0),
        "U5": (6.0, 5.0), "U6": (3.0, 2.9), "U7": (3.0, 2.9), "Q1": (3.0, 2.9),
        "D1": (2.0, 1.25), "J1": (4.0, 2.0), "J2": (9.0, 2.0), "J3": (8.0, 2.0), "SW1": (5.0, 1.8)
    }
    s = ['(kicad_pcb (version 20240108) (generator "smart_apo_revA_generator")',
         '  (general (thickness 1.0))', '  (paper "A4")', '  (layers',
         '    (0 "F.Cu" signal)', '    (2 "In1.Cu" power)', '    (4 "In2.Cu" power)',
         '    (31 "B.Cu" signal)', '    (36 "B.SilkS" user "b.silkscreen")',
         '    (37 "F.SilkS" user "f.silkscreen")', '    (44 "Edge.Cuts" user)',
         '  )', '  (setup (pad_to_mask_clearance 0))']
    # 12 x 35 mm outline with 2 mm corner chamfers.
    outline = [(2,0),(10,0),(12,2),(12,33),(10,35),(2,35),(0,33),(0,2),(2,0)]
    for a,b in zip(outline, outline[1:]):
        s.append(f'  (gr_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width 0.1) (type default)) (layer "Edge.Cuts"))')
    s.append('  (gr_text "SMART APO Rev.A / PLACEMENT REVIEW / NOT FAB RELEASED" (at 6 17.5 90) (layer "B.SilkS") (effects (font (size 0.65 0.65) (thickness 0.1)) (justify mirror)))')
    for ref, val, _fp, x, y, rot, _pop in PARTS:
        w,h = dims[ref]
        s.append(kicad_fp(ref, val, x, y, rot, w, h).rstrip())
    s.append(')')
    (HW / "smart_apo_common_revA_PLACEMENT_ONLY.kicad_pcb").write_text("\n".join(s) + "\n")


def write_pcb_svg():
    colors = {"BOTH":"#5aa9e6", "AWA":"#7fc97f", "UNDERWATER":"#fdc086"}
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="480" height="920" viewBox="0 0 120 230">',
           '<rect width="120" height="230" fill="#fafafa"/>',
           '<g transform="translate(20 10) scale(6)">',
           '<path d="M2,0 H10 L12,2 V33 L10,35 H2 L0,33 V2 Z" fill="#1e5b42" stroke="#111" stroke-width="0.18"/>']
    dims = {"U1":(6.4,6.5),"U2":(3,2.5),"U3":(2.8,2.8),"U4":(6.2,10),"U5":(6,5),
            "U6":(3,2.9),"U7":(3,2.9),"Q1":(3,2.9),"D1":(2,1.25),"J1":(4,2),"J2":(9,2),"J3":(8,2),"SW1":(5,1.8)}
    for ref,val,_fp,x,y,rot,pop in PARTS:
        w,h=dims[ref]
        svg.append(f'<g transform="translate({x} {y}) rotate({rot})"><rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" fill="{colors[pop]}" stroke="#fff" stroke-width="0.15"/><text x="0" y="0.35" font-size="0.9" text-anchor="middle" fill="#111">{ref}</text></g>')
    svg += ['</g>', '<text x="20" y="224" font-family="sans-serif" font-size="5">12 × 35 × 1.0 mm · placement review</text>', '</svg>']
    (HW / "pcb_placement_revA.svg").write_text("\n".join(svg))


def write_summary(mesh_reports):
    # The submerged target is based on the external capsule envelope, not shell material volume.
    r, straight = 10.0, 50.0
    displaced_mm3 = math.pi * r*r*straight + 4/3*math.pi*r**3
    seawater_g = displaced_mm3 / 1000 * 1.025
    target_g = seawater_g + 2.9
    data = {
        "revision": "A1-pre-release",
        "awa_envelope_mm": [32, 32, 49],
        "pcb_envelope_mm": [12, 35, 1.0],
        "underwater_envelope_nominal_mm": [20, 20, 70],
        "underwater_external_displacement_ml": round(displaced_mm3/1000, 3),
        "seawater_displaced_mass_g_at_1p025": round(seawater_g, 3),
        "underwater_target_total_mass_g_for_minus_2p9g": round(target_g, 3),
        "mesh_reports": mesh_reports,
        "pcb_release_status": "BLOCKED: net-assigned and placed; zero routed tracks; requires official footprint review, routing, ERC and DRC",
    }
    (CHECKS / "generated_checks.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main():
    for d in (MECH, HW, CHECKS):
        d.mkdir(parents=True, exist_ok=True)
    reports = make_awa() + make_underwater() + make_flexure()
    # Rev.A1 electrical outputs have separate generators. This script rebuilds
    # only mechanical files so it cannot overwrite reviewed electrical data.
    write_summary(reports)
    bad = [x["file"] for x in reports if not x["watertight"]]
    if bad:
        raise SystemExit("Non-watertight meshes: " + ", ".join(bad))
    print(json.dumps({"generated": len(reports), "all_watertight": True}, indent=2))


if __name__ == "__main__":
    main()
