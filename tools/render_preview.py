#!/usr/bin/env python3
"""Render a compact engineering preview from generated STL files."""

from pathlib import Path
import matplotlib.pyplot as plt
import trimesh

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "mechanical"

items = [
    ("Smart Awa body", "awa_body_32x49_revA.stl", "#4c9f70"),
    ("Smart Awa cap", "awa_cap_revA.stl", "#7fc8a9"),
    ("Underwater half A", "underwater_fairing_half_A_revA.stl", "#3977b7"),
    ("316L flexure", "316L_flexure_preview_NOT_FOR_PRINTING.stl", "#aaaeb5"),
]

fig = plt.figure(figsize=(11, 8), facecolor="white")
for i, (title, filename, color) in enumerate(items, 1):
    ax = fig.add_subplot(2, 2, i, projection="3d")
    mesh = trimesh.load_mesh(M / filename)
    # Decimate only visually by plotting every Nth face; source STL is untouched.
    step = max(1, len(mesh.faces) // 3500)
    f = mesh.faces[::step]
    v = mesh.vertices
    ax.plot_trisurf(v[:,0], v[:,1], v[:,2], triangles=f, color=color,
                    linewidth=0.05, edgecolor=(0,0,0,0.08), shade=True)
    bounds = mesh.bounds
    spans = bounds[1] - bounds[0]
    centres = bounds.mean(axis=0)
    half = max(spans) / 2
    ax.set_xlim(centres[0]-half, centres[0]+half)
    ax.set_ylim(centres[1]-half, centres[1]+half)
    ax.set_zlim(centres[2]-half, centres[2]+half)
    ax.set_box_aspect((1,1,1))
    ax.view_init(elev=22, azim=35)
    ax.set_title(title, fontsize=11)
    ax.set_axis_off()

fig.suptitle("Smart Awa + Smart Underwater Rev.A1 mechanical preview", fontsize=15)
fig.text(0.5, 0.025, "Awa 32 × 49 mm · underwater capsule Ø20 × 70 mm · dimensions in mm",
         ha="center", fontsize=10, color="#444")
fig.tight_layout(rect=(0,0.05,1,0.95))
fig.savefig(ROOT / "mechanical_preview_revA.png", dpi=180)
