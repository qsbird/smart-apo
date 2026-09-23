#!/usr/bin/env python3
"""Build the Rev.A2 placement-only PCB with KiCad 10's pcbnew API.

This is intentionally not a fabrication generator.  It imports the exact
footprints and connectivity declared by the KiCad XML netlist, establishes the
mechanical/layer/rule baseline, and stops before routing.  The resulting board
is marked NO_GERBER until routing and an error-free official DRC are complete.

Run with KiCad's bundled Python, for example::

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/\
      Versions/3.9/bin/python3 tools/generate_pcb_revA2.py
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

try:
    import wx

    _wx_app = wx.App(False)
    import pcbnew
except ImportError as exc:  # pragma: no cover - useful diagnostic outside KiCad Python
    raise SystemExit(
        "pcbnew is unavailable; run this script with KiCad 10's bundled Python"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "hardware" / "revA2"
NETLIST = REV / "netlist_revA2_kicad10.xml"
OUTPUT = REV / "smart_apo_common_revA2.kicad_pcb"
KICAD_FOOTPRINTS = Path(
    "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
)
PROJECT_FOOTPRINTS = REV / "SmartApoRevA2.pretty"


@dataclass(frozen=True)
class Placement:
    x: float
    y: float
    angle: float = 0.0
    back: bool = False


# Coordinates are a fresh Rev.A2 placement based on functional blocks.  They
# deliberately keep the pressure sensor at the top, the analog bridge chain
# together, and charging/battery interfaces at the bottom.  Routing remains a
# later reviewed operation.
PLACEMENT: dict[str, Placement] = {
    "U3": Placement(6.0, 2.4),
    "C4": Placement(10.4, 2.2, 90),
    "U2": Placement(2.3, 6.6),
    "C2": Placement(1.05, 9.5, 90),
    "C3": Placement(4.8, 8.8, 90),
    "U5": Placement(6.2, 6.2, 0, True),
    "C8": Placement(1.15, 10.0, 90, True),
    "R12": Placement(10.55, 5.0, 90),
    "R1": Placement(1.15, 11.3),
    "R2": Placement(8.5, 8.4),
    "U1": Placement(6.0, 13.2),
    "C1": Placement(10.55, 12.4, 90),
    "C14": Placement(10.55, 14.4, 90),
    "C17": Placement(10.55, 10.4, 90),
    "R11": Placement(10.55, 8.4, 90),
    "R4": Placement(10.55, 16.4, 90),
    "R5": Placement(10.55, 18.4, 90),
    "R10": Placement(10.55, 20.4, 90),
    "J2": Placement(1.15, 13.6, 90, True),
    "Y1": Placement(6.0, 17.6, 0, True),
    "C15": Placement(3.8, 17.6, 90, True),
    "C16": Placement(8.2, 17.6, 90, True),
    "SW1": Placement(6.0, 20.4, 0, True),
    "U4": Placement(5.4, 23.6),
    "C5": Placement(10.55, 22.6, 90),
    "C6": Placement(10.55, 24.6, 90),
    "C7": Placement(10.55, 26.6, 90),
    "C13": Placement(1.05, 21.6, 90),
    "R8": Placement(1.05, 23.6, 90),
    "R9": Placement(1.05, 25.6, 90),
    "U6": Placement(3.2, 31.2),
    "U7": Placement(10.0, 33.4, 180),
    "C11": Placement(0.95, 31.0, 90),
    "C12": Placement(0.95, 32.4, 90),
    "R3": Placement(4.8, 31.2, 90),
    "C9": Placement(6.6, 31.8),
    "C10": Placement(10.55, 28.4, 90),
    "J1": Placement(6.2, 33.4, 0, True),
    "Q1": Placement(1.9, 29.6, 0, True),
    "D1": Placement(2.0, 33.4, 90),
    "R6": Placement(4.0, 33.4),
    "R7": Placement(2.2, 28.8, 90, True),
    "J3": Placement(7.4, 32.6),
}


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(x), mm(y))


def parse_netlist() -> tuple[list[dict[str, str]], dict[tuple[str, str], str]]:
    root = ET.parse(NETLIST).getroot()
    components: list[dict[str, str]] = []
    for comp in root.find("components") or ():
        fields = {f.get("name", ""): f.text or "" for f in comp.findall("./fields/field")}
        components.append(
            {
                "ref": comp.attrib["ref"],
                "value": comp.findtext("value") or "",
                "footprint": comp.findtext("footprint") or "",
                "uuid": comp.findtext("tstamps") or "",
                "population": fields.get("Population", ""),
            }
        )

    pin_nets: dict[tuple[str, str], str] = {}
    for net in root.find("nets") or ():
        name = net.attrib["name"]
        for node in net.findall("node"):
            key = (node.attrib["ref"], node.attrib["pin"])
            if key in pin_nets:
                raise ValueError(f"duplicate netlist node {key}")
            pin_nets[key] = name
    return components, pin_nets


def load_footprint(identifier: str) -> pcbnew.FOOTPRINT:
    if ":" not in identifier:
        raise ValueError(f"invalid footprint identifier: {identifier!r}")
    nickname, name = identifier.split(":", 1)
    directory = (
        PROJECT_FOOTPRINTS
        if nickname == "SmartApoRevA2"
        else KICAD_FOOTPRINTS / f"{nickname}.pretty"
    )
    footprint = pcbnew.FootprintLoad(str(directory), name)
    if footprint is None:
        raise FileNotFoundError(f"cannot load {identifier} from {directory}")
    footprint.SetFPID(pcbnew.LIB_ID(nickname, name))
    return footprint


def configure_board(board: pcbnew.BOARD) -> None:
    board.SetCopperLayerCount(4)
    board.SetLayerName(pcbnew.In1_Cu, "In1.Cu")
    board.SetLayerName(pcbnew.In2_Cu, "In2.Cu")
    settings = board.GetDesignSettings()
    settings.SetBoardThickness(mm(1.0))
    settings.m_MinClearance = mm(0.15)
    settings.m_TrackMinWidth = mm(0.15)
    settings.m_ViasMinSize = mm(0.60)
    settings.m_ViasMinDrill = mm(0.30)
    settings.m_MicroViasMinSize = mm(0.60)
    settings.m_MicroViasMinDrill = mm(0.30)
    settings.m_CopperEdgeClearance = mm(0.25)
    default = settings.m_NetSettings.GetDefaultNetclass()
    default.SetClearance(mm(0.15))
    default.SetTrackWidth(mm(0.15))
    default.SetViaDiameter(mm(0.60))
    default.SetViaDrill(mm(0.30))
    properties = pcbnew.MAP_STRING_STRING()
    for key, value in {
        "REVISION": "Rev.A2",
        "RELEASE_STATUS": "NO_GERBER_PLACEMENT_ONLY",
        "BOARD_SIZE": "12x35x1.0mm",
        "STACKUP_INTENT": "F.Cu / In1.GND / In2.POWER / B.Cu",
    }.items():
        properties[key] = value
    board.SetProperties(properties)


def add_outline(board: pcbnew.BOARD) -> None:
    # Overall bounding box is exactly 12 x 35 mm.  The small corner chamfers
    # match the mechanical intent without inheriting the Rev.A1 PCB file.
    outline = [
        (2.0, 0.0), (10.0, 0.0), (12.0, 2.0), (12.0, 33.0),
        (10.0, 35.0), (2.0, 35.0), (0.0, 33.0), (0.0, 2.0), (2.0, 0.0),
    ]
    for start, end in zip(outline, outline[1:]):
        edge = pcbnew.PCB_SHAPE(board)
        edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
        edge.SetStart(point(*start))
        edge.SetEnd(point(*end))
        edge.SetLayer(pcbnew.Edge_Cuts)
        edge.SetWidth(mm(0.10))
        board.Add(edge)


def add_status_text(board: pcbnew.BOARD) -> None:
    text = pcbnew.PCB_TEXT(board)
    text.SetText("SMART APO Rev.A2 | PLACEMENT ONLY | NO GERBER")
    text.SetLayer(pcbnew.B_SilkS)
    text.SetPosition(point(6.0, 17.5))
    text.SetTextSize(point(0.65, 0.65))
    text.SetTextThickness(mm(0.10))
    text.SetTextAngle(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
    board.Add(text)


def add_components(
    board: pcbnew.BOARD,
    components: list[dict[str, str]],
    pin_nets: dict[tuple[str, str], str],
) -> None:
    refs = {component["ref"] for component in components}
    if refs != set(PLACEMENT):
        raise ValueError(
            f"placement/netlist mismatch; missing={sorted(refs-set(PLACEMENT))}, "
            f"extra={sorted(set(PLACEMENT)-refs)}"
        )

    net_names = sorted(set(pin_nets.values()))
    nets: dict[str, pcbnew.NETINFO_ITEM] = {}
    for code, name in enumerate(net_names, 1):
        net = pcbnew.NETINFO_ITEM(board, name, code)
        board.Add(net)
        nets[name] = net

    expected_pads: dict[str, set[str]] = {}
    for ref, pad in pin_nets:
        expected_pads.setdefault(ref, set()).add(pad)

    for component in components:
        ref = component["ref"]
        footprint = load_footprint(component["footprint"])
        footprint.SetReference(ref)
        footprint.SetValue(component["value"])
        footprint.SetPath(pcbnew.KIID_PATH(component["uuid"]))
        place = PLACEMENT[ref]
        footprint.SetPosition(point(place.x, place.y))
        footprint.SetOrientationDegrees(place.angle)
        board.Add(footprint)
        if place.back:
            # KiCad 10 requires the footprint to be on the board before Flip().
            footprint.Flip(footprint.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)

        numbered = {pad.GetNumber() for pad in footprint.Pads() if pad.GetNumber()}
        missing = expected_pads.get(ref, set()) - numbered
        if missing:
            raise ValueError(f"{ref} {component['footprint']} lacks netlist pads {sorted(missing)}")
        for pad in footprint.Pads():
            number = pad.GetNumber()
            net_name = pin_nets.get((ref, number))
            if net_name:
                pad.SetNet(nets[net_name])


def validate_board(board: pcbnew.BOARD, components: list[dict[str, str]], pin_nets: dict[tuple[str, str], str]) -> None:
    actual_refs = {fp.GetReference() for fp in board.GetFootprints()}
    expected_refs = {component["ref"] for component in components}
    if actual_refs != expected_refs:
        raise ValueError("saved board reference set differs from netlist")
    for footprint in board.GetFootprints():
        ref = footprint.GetReference()
        for pad in footprint.Pads():
            expected = pin_nets.get((ref, pad.GetNumber()))
            if expected and pad.GetNetname() != expected:
                raise ValueError(
                    f"net assignment mismatch {ref}.{pad.GetNumber()}: "
                    f"{pad.GetNetname()!r} != {expected!r}"
                )


def main() -> int:
    if pcbnew.GetBuildVersion() != "10.0.6":
        print(f"warning: designed for pcbnew 10.0.6, running {pcbnew.GetBuildVersion()}", file=sys.stderr)
    components, pin_nets = parse_netlist()
    board = pcbnew.BOARD()
    configure_board(board)
    add_outline(board)
    add_status_text(board)
    add_components(board, components, pin_nets)
    validate_board(board, components, pin_nets)
    pcbnew.SaveBoard(str(OUTPUT), board)

    reloaded = pcbnew.LoadBoard(str(OUTPUT))
    validate_board(reloaded, components, pin_nets)
    print(
        f"generated {OUTPUT}: {len(list(reloaded.GetFootprints()))} footprints, "
        f"{len(set(pin_nets.values()))} nets, 4 copper layers, NO_GERBER"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
