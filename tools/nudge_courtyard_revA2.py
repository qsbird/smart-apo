#!/usr/bin/env python3
"""PARKED. Moving footprints on an already-routed board dropped courtyard
10 -> 6 but raised official DRC 108 -> 175 (pads landed on existing tracks).
The live PCB was restored. Do not run this against a routed candidate.
"""

from __future__ import annotations

from pathlib import Path

try:
    import wx

    _wx_app = wx.App(False)
    import pcbnew
except ImportError as exc:
    raise SystemExit("run with KiCad 10 Python") from exc

BOARD = Path(__file__).resolve().parents[1] / "hardware" / "revA2" / "smart_apo_common_revA2.kicad_pcb"

# millimetres, existing occupancy-routed board, CP05 courtyard-only nudges
MOVES = {
    "U6": (4.50, 30.60),
    "C3": (3.20, 7.70),
    "C10": (10.55, 29.80),
    "R3": (8.40, 32.20),
    "C11": (0.95, 27.40),
    "C12": (0.95, 28.80),
    "R7": (3.40, 26.80),
}


def main() -> int:
    board = pcbnew.LoadBoard(str(BOARD))
    found = {fp.GetReference(): fp for fp in board.GetFootprints()}
    for ref, (x, y) in MOVES.items():
        if ref not in found:
            raise SystemExit(f"missing {ref}")
        found[ref].SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        print(f"moved {ref} to {x:.2f},{y:.2f}")
    pcbnew.SaveBoard(str(BOARD), board)
    print(f"saved {BOARD} (tracks unchanged)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
