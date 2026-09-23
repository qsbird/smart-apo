#!/usr/bin/env python3
"""PARKED maze router. Do not use as the production routing path.

Historical grid/maze runs created more shorts than they closed unconnected
pads (official DRC 2026-09-09: 380 errors / 73 unconnected). The 5-round
abandon rule applies. Use tools/route_explicit_revA2.py instead.

This file is kept only as a record of the failed approach.

Run with KiCad's bundled Python::

    PYTHONHOME=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9 \
      /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
      tools/route_pcb_revA2.py
"""

from __future__ import annotations

import heapq
import math
import sys
from collections import defaultdict
from pathlib import Path

try:
    import wx

    _wx_app = wx.App(False)
    import pcbnew
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "pcbnew is unavailable; run this script with KiCad 10's bundled Python"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "revA2" / "smart_apo_common_revA2.kicad_pcb"

TRACK_W = 0.15
POWER_W = 0.30
VIA_D = 0.60
VIA_DRILL = 0.30
CLEAR = 0.15
GRID = 0.05
EDGE = 0.35
BOARD_W = 12.0
BOARD_H = 35.0

ROUTE_ORDER = [
    "AIN_P_FILT",
    "AIN_N_FILT",
    "BRIDGE_A+",
    "BRIDGE_A-",
    "BRIDGE_S+",
    "BRIDGE_S-",
    "BRIDGE_E+",
    "VBG",
    "LSE_IN",
    "LSE_OUT",
    "I2C_SDA",
    "I2C_SCL",
    "STRAIN_DRDY",
    "IMU_INT",
    "SWDIO",
    "SWCLK",
    "UART_TX",
    "UART_RX",
    "NRST",
    "LED_GATE",
    "LED_A",
    "LED_K",
    "REED_WAKE",
    "VBAT_SENSE",
    "SPI_SCK",
    "SPI_MISO",
    "SPI_MOSI",
    "FLASH_CS",
    "CHG_PROG",
    "CHARGE_IN",
]

PLANE_NETS = {"GND", "3V3", "VBAT"}
SKIP_PREFIX = "unconnected-"
F_LAYER, B_LAYER = 0, 1
LAYER_ID = {F_LAYER: pcbnew.F_Cu, B_LAYER: pcbnew.B_Cu}


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(x), mm(y))


def net_key(name: str) -> str:
    return name.lstrip("/")


def inside_board(x: float, y: float, margin: float = EDGE) -> bool:
    if x < margin or x > BOARD_W - margin or y < margin or y > BOARD_H - margin:
        return False
    chamfer = 2.0 + margin * math.sqrt(2.0)
    if x + y < chamfer:
        return False
    if (BOARD_W - x) + y < chamfer:
        return False
    if (BOARD_W - x) + (BOARD_H - y) < chamfer:
        return False
    if x + (BOARD_H - y) < chamfer:
        return False
    return True


def inset_outline(margin: float = 0.40) -> list[tuple[float, float]]:
    c = 2.0 + margin * math.sqrt(2.0) / 2.0
    return [
        (c, margin),
        (BOARD_W - c, margin),
        (BOARD_W - margin, c),
        (BOARD_W - margin, BOARD_H - c),
        (BOARD_W - c, BOARD_H - margin),
        (c, BOARD_H - margin),
        (margin, BOARD_H - c),
        (margin, c),
    ]


def find_net(board: pcbnew.BOARD, name: str) -> pcbnew.NETINFO_ITEM:
    net = board.FindNet("/" + name) or board.FindNet(name)
    if net is None:
        raise KeyError(name)
    return net


def add_zone(board: pcbnew.BOARD, layer: int, net_name: str, outline: list[tuple[float, float]], priority: int = 0) -> pcbnew.ZONE:
    zone = pcbnew.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNet(find_net(board, net_name))
    zone.SetAssignedPriority(priority)
    zone.SetLocalClearance(mm(CLEAR))
    zone.SetMinThickness(mm(0.20))
    zone.SetThermalReliefGap(mm(0.20))
    zone.SetThermalReliefSpokeWidth(mm(0.20))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    zone.Outline().NewOutline()
    for x, y in outline:
        zone.Outline().Append(mm(x), mm(y))
    board.Add(zone)
    return zone


def add_planes(board: pcbnew.BOARD) -> None:
    full = inset_outline(0.40)
    vbat = [
        (0.40, 26.40),
        (11.60, 26.40),
        (11.60, 32.84),
        (9.84, 34.60),
        (2.16, 34.60),
        (0.40, 32.84),
    ]
    v3 = [
        (2.16, 0.40),
        (9.84, 0.40),
        (11.60, 2.16),
        (11.60, 26.10),
        (0.40, 26.10),
        (0.40, 2.16),
    ]
    add_zone(board, pcbnew.In1_Cu, "GND", full, 0)
    add_zone(board, pcbnew.F_Cu, "GND", full, 0)
    add_zone(board, pcbnew.B_Cu, "GND", full, 0)
    add_zone(board, pcbnew.In2_Cu, "3V3", v3, 0)
    add_zone(board, pcbnew.In2_Cu, "VBAT", vbat, 1)


def pad_rect(pad: pcbnew.PAD) -> tuple[float, float, float, float]:
    box = pad.GetBoundingBox()
    return (
        pcbnew.ToMM(box.GetLeft()),
        pcbnew.ToMM(box.GetRight()),
        pcbnew.ToMM(box.GetTop()),
        pcbnew.ToMM(box.GetBottom()),
    )


def pad_layer(pad: pcbnew.PAD) -> int | None:
    on_f = pad.IsOnLayer(pcbnew.F_Cu)
    on_b = pad.IsOnLayer(pcbnew.B_Cu)
    if on_f and not on_b:
        return F_LAYER
    if on_b and not on_f:
        return B_LAYER
    return None  # through-hole or both


class Occupancy:
    def __init__(self) -> None:
        self.nx = int(round(BOARD_W / GRID)) + 1
        self.ny = int(round(BOARD_H / GRID)) + 1
        self.blocked = [set(), set()]
        self.via_blocked: set[tuple[int, int]] = set()

    def to_cell(self, x: float, y: float) -> tuple[int, int]:
        return int(round(x / GRID)), int(round(y / GRID))

    def from_cell(self, cx: int, cy: int) -> tuple[float, float]:
        return cx * GRID, cy * GRID

    def mark_rect(self, layer: int | None, x0: float, x1: float, y0: float, y1: float, inflate: float) -> None:
        gx0 = max(0, int(math.floor((min(x0, x1) - inflate) / GRID)))
        gx1 = min(self.nx - 1, int(math.ceil((max(x0, x1) + inflate) / GRID)))
        gy0 = max(0, int(math.floor((min(y0, y1) - inflate) / GRID)))
        gy1 = min(self.ny - 1, int(math.ceil((max(y0, y1) + inflate) / GRID)))
        layers = [F_LAYER, B_LAYER] if layer is None else [layer]
        for layer_i in layers:
            bucket = self.blocked[layer_i]
            for gx in range(gx0, gx1 + 1):
                for gy in range(gy0, gy1 + 1):
                    bucket.add((gx, gy))

    def mark_circle(self, layer: int | None, x: float, y: float, radius: float) -> None:
        r2 = radius * radius
        gx0 = max(0, int(math.floor((x - radius) / GRID)))
        gx1 = min(self.nx - 1, int(math.ceil((x + radius) / GRID)))
        gy0 = max(0, int(math.floor((y - radius) / GRID)))
        gy1 = min(self.ny - 1, int(math.ceil((y + radius) / GRID)))
        layers = [F_LAYER, B_LAYER] if layer is None else [layer]
        for gx in range(gx0, gx1 + 1):
            for gy in range(gy0, gy1 + 1):
                px, py = self.from_cell(gx, gy)
                if (px - x) ** 2 + (py - y) ** 2 <= r2:
                    for layer_i in layers:
                        self.blocked[layer_i].add((gx, gy))
                    self.via_blocked.add((gx, gy))

    def clear_rect(self, layer: int, x0: float, x1: float, y0: float, y1: float, inflate: float) -> None:
        gx0 = max(0, int(math.floor((min(x0, x1) - inflate) / GRID)))
        gx1 = min(self.nx - 1, int(math.ceil((max(x0, x1) + inflate) / GRID)))
        gy0 = max(0, int(math.floor((min(y0, y1) - inflate) / GRID)))
        gy1 = min(self.ny - 1, int(math.ceil((max(y0, y1) + inflate) / GRID)))
        bucket = self.blocked[layer]
        for gx in range(gx0, gx1 + 1):
            for gy in range(gy0, gy1 + 1):
                bucket.discard((gx, gy))


def collect_pads(board: pcbnew.BOARD) -> dict[str, list[pcbnew.PAD]]:
    pads: dict[str, list[pcbnew.PAD]] = defaultdict(list)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            name = net_key(pad.GetNetname() or "")
            if name:
                pads[name].append(pad)
    return pads


def seed_occupancy(board: pcbnew.BOARD, current_net: str | None = None) -> Occupancy:
    occ = Occupancy()
    inflate = CLEAR + TRACK_W / 2
    for gx in range(occ.nx):
        for gy in range(occ.ny):
            x, y = occ.from_cell(gx, gy)
            if not inside_board(x, y):
                occ.blocked[F_LAYER].add((gx, gy))
                occ.blocked[B_LAYER].add((gx, gy))
                occ.via_blocked.add((gx, gy))
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            name = net_key(pad.GetNetname() or "")
            if current_net and name == current_net:
                continue
            x0, x1, y0, y1 = pad_rect(pad)
            occ.mark_rect(pad_layer(pad), x0, x1, y0, y1, inflate)
        if fp.GetReference() == "U3":
            pos = fp.GetPosition()
            cx, cy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            occ.mark_rect(F_LAYER, cx - 1.40, cx + 1.40, cy - 1.40, cy + 1.40, CLEAR)
            occ.mark_circle(None, cx, cy, 1.55)
    for track in board.GetTracks():
        net = net_key(track.GetNetname() or "")
        if current_net and net == current_net:
            continue
        if track.GetClass() == "PCB_VIA":
            pos = track.GetPosition()
            occ.mark_circle(None, pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y), VIA_D / 2 + CLEAR + TRACK_W / 2)
        else:
            layer = F_LAYER if track.GetLayer() == pcbnew.F_Cu else B_LAYER
            start, end = track.GetStart(), track.GetEnd()
            occ.mark_rect(
                layer,
                pcbnew.ToMM(start.x),
                pcbnew.ToMM(end.x),
                pcbnew.ToMM(start.y),
                pcbnew.ToMM(end.y),
                inflate,
            )
    if current_net:
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if net_key(pad.GetNetname() or "") != current_net:
                    continue
                layer = pad_layer(pad)
                if layer is None:
                    continue
                x0, x1, y0, y1 = pad_rect(pad)
                occ.clear_rect(layer, x0, x1, y0, y1, TRACK_W / 2)
    return occ


def pad_anchor(pad: pcbnew.PAD) -> tuple[int, float, float]:
    pos = pad.GetPosition()
    x, y = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
    layer = pad_layer(pad)
    if layer is None:
        layer = F_LAYER
    return layer, x, y


def pad_cells(occ: Occupancy, pad: pcbnew.PAD) -> list[tuple[int, int, int]]:
    layer, x, y = pad_anchor(pad)
    x0, x1, y0, y1 = pad_rect(pad)
    cells: list[tuple[int, int, int]] = []
    gx0 = max(0, int(math.floor(min(x0, x1) / GRID)))
    gx1 = min(occ.nx - 1, int(math.ceil(max(x0, x1) / GRID)))
    gy0 = max(0, int(math.floor(min(y0, y1) / GRID)))
    gy1 = min(occ.ny - 1, int(math.ceil(max(y0, y1) / GRID)))
    for gx in range(gx0, gx1 + 1):
        for gy in range(gy0, gy1 + 1):
            if (gx, gy) not in occ.blocked[layer]:
                cells.append((layer, gx, gy))
    if not cells:
        cx, cy = occ.to_cell(x, y)
        cells.append((layer, cx, cy))
    return cells


def astar(
    occ: Occupancy,
    starts: list[tuple[int, int, int]],
    goals: list[tuple[int, int, int]],
) -> list[tuple[int, int, int]] | None:
    goal_set = set(goals)
    goal_xy = [(g[0], g[1], g[2]) for g in goals]

    def heuristic(state: tuple[int, int, int]) -> float:
        return min(
            abs(state[1] - g[1]) + abs(state[2] - g[2]) + (0 if state[0] == g[0] else 8)
            for g in goal_xy
        )

    frontier: list[tuple[float, int, tuple[int, int, int]]] = []
    counter = 0
    came: dict[tuple[int, int, int], tuple[int, int, int] | None] = {}
    cost: dict[tuple[int, int, int], float] = {}
    for start_state in starts:
        came[start_state] = None
        cost[start_state] = 0.0
        heapq.heappush(frontier, (heuristic(start_state), counter, start_state))
        counter += 1
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while frontier:
        _, _, current = heapq.heappop(frontier)
        if current in goal_set:
            path = [current]
            while came[path[-1]] is not None:
                path.append(came[path[-1]])  # type: ignore[arg-type]
            path.reverse()
            return path
        layer, cx, cy = current
        for dx, dy in moves:
            nxt = (layer, cx + dx, cy + dy)
            if nxt[1] < 0 or nxt[1] >= occ.nx or nxt[2] < 0 or nxt[2] >= occ.ny:
                continue
            if (nxt[1], nxt[2]) in occ.blocked[layer]:
                continue
            new_cost = cost[current] + 1
            if nxt not in cost or new_cost < cost[nxt]:
                cost[nxt] = new_cost
                came[nxt] = current
                counter += 1
                heapq.heappush(frontier, (new_cost + heuristic(nxt), counter, nxt))
        other = 1 - layer
        via_state = (other, cx, cy)
        if (cx, cy) not in occ.via_blocked and (cx, cy) not in occ.blocked[other]:
            new_cost = cost[current] + 6
            if via_state not in cost or new_cost < cost[via_state]:
                cost[via_state] = new_cost
                came[via_state] = current
                counter += 1
                heapq.heappush(frontier, (new_cost + heuristic(via_state), counter, via_state))
    return None


def commit_path(board: pcbnew.BOARD, occ: Occupancy, net: pcbnew.NETINFO_ITEM, path: list[tuple[int, int, int]], width: float) -> None:
    segments: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = []
    for prev, cur in zip(path, path[1:]):
        if prev[0] == cur[0]:
            if segments and segments[-1][0][0] == prev[0] and segments[-1][1] == prev:
                start = segments[-1][0]
                if start[1] == cur[1] or start[2] == cur[2]:
                    segments[-1] = (start, cur)
                    continue
            segments.append((prev, cur))
        else:
            x, y = occ.from_cell(cur[1], cur[2])
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(point(x, y))
            via.SetWidth(mm(VIA_D))
            via.SetDrill(mm(VIA_DRILL))
            via.SetViaType(pcbnew.VIATYPE_THROUGH)
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            via.SetNet(net)
            board.Add(via)
            occ.mark_circle(None, x, y, VIA_D / 2 + CLEAR + TRACK_W / 2)
    for start, end in segments:
        if start[1] == end[1] and start[2] == end[2]:
            continue
        x0, y0 = occ.from_cell(start[1], start[2])
        x1, y1 = occ.from_cell(end[1], end[2])
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(point(x0, y0))
        track.SetEnd(point(x1, y1))
        track.SetWidth(mm(width))
        track.SetLayer(LAYER_ID[start[0]])
        track.SetNet(net)
        board.Add(track)
        occ.mark_rect(start[0], x0, x1, y0, y1, CLEAR + width / 2)


def route_net(board: pcbnew.BOARD, pads: list[pcbnew.PAD], net: pcbnew.NETINFO_ITEM, width: float) -> bool:
    if len(pads) < 2:
        return True
    before = set(id(item) for item in board.GetTracks())
    occ = seed_occupancy(board, net_key(net.GetNetname()))
    cells = [pad_cells(occ, pad) for pad in pads]
    anchors = [pad_anchor(pad) for pad in pads]
    connected = {0}
    success = True
    while len(connected) < len(pads):
        best = None
        best_pair = None
        for i in connected:
            for j, anchor in enumerate(anchors):
                if j in connected:
                    continue
                dist = abs(anchors[i][1] - anchor[1]) + abs(anchors[i][2] - anchor[2])
                if best is None or dist < best:
                    best = dist
                    best_pair = (i, j)
        assert best_pair is not None
        src, dst = best_pair
        path = astar(occ, cells[src], cells[dst])
        if path is None:
            success = False
            break
        commit_path(board, occ, net, path, width)
        connected.add(dst)
        cells[src] = cells[src] + path[-3:]
        cells[dst] = cells[dst] + path[-3:]
    if not success:
        for item in list(board.GetTracks()):
            if id(item) not in before and net_key(item.GetNetname() or "") == net_key(net.GetNetname()):
                board.Remove(item)
        return False
    tie_pads(board, pads, net, width)
    return True


def add_track(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, x0: float, y0: float, x1: float, y1: float, layer: int, width: float = TRACK_W) -> None:
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(point(x0, y0))
    track.SetEnd(point(x1, y1))
    track.SetWidth(mm(width))
    track.SetLayer(layer)
    track.SetNet(net)
    board.Add(track)


def tie_pads(board: pcbnew.BOARD, pads: list[pcbnew.PAD], net: pcbnew.NETINFO_ITEM, width: float) -> None:
    """Snap a short stub from each pad center to the nearest same-net copper."""
    copper: list[tuple[int, float, float]] = []
    for track in board.GetTracks():
        if net_key(track.GetNetname() or "") != net_key(net.GetNetname()):
            continue
        if track.GetClass() == "PCB_VIA":
            pos = track.GetPosition()
            copper.append((F_LAYER, pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)))
            copper.append((B_LAYER, pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)))
        else:
            layer = F_LAYER if track.GetLayer() == pcbnew.F_Cu else B_LAYER
            for pt in (track.GetStart(), track.GetEnd()):
                copper.append((layer, pcbnew.ToMM(pt.x), pcbnew.ToMM(pt.y)))
    for pad in pads:
        layer, x, y = pad_anchor(pad)
        best = None
        best_d = 0.80
        for cl, cx, cy in copper:
            if cl != layer:
                continue
            dist = math.hypot(cx - x, cy - y)
            if dist < best_d:
                best_d = dist
                best = (cx, cy)
        if best and best_d > 0.02:
            add_track(board, net, x, y, best[0], y, LAYER_ID[layer], width)
            if abs(y - best[1]) > 0.02:
                add_track(board, net, best[0], y, best[0], best[1], LAYER_ID[layer], width)


def add_via(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, x: float, y: float) -> None:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(x, y))
    via.SetWidth(mm(VIA_D))
    via.SetDrill(mm(VIA_DRILL))
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(net)
    board.Add(via)


def pad_of(pads: list[pcbnew.PAD], ref: str, number: str) -> pcbnew.PAD:
    for pad in pads:
        if pad.GetParentFootprint().GetReference() == ref and pad.GetNumber() == number:
            return pad
    raise KeyError(f"{ref}.{number}")


def route_from_point(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, start: tuple[int, float, float], pads: list[pcbnew.PAD], width: float) -> bool:
    occ = seed_occupancy(board, net_key(net.GetNetname()))
    start_cell = (start[0], *occ.to_cell(start[1], start[2]))
    for pad in pads:
        path = astar(occ, [start_cell], pad_cells(occ, pad))
        if path is None:
            return False
        commit_path(board, occ, net, path, width)
        start_cell = path[-1]
    return True


def route_spi_fanout(board: pcbnew.BOARD, pads_by_net: dict[str, list[pcbnew.PAD]]) -> list[str]:
    """Escape the back-side WSON on the board edges, then drop to F.Cu."""
    still: list[str] = []

    def manhattan(net: pcbnew.NETINFO_ITEM, points: list[tuple[float, float]], layer: int) -> None:
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            if abs(x0 - x1) > 0.01 and abs(y0 - y1) > 0.01:
                add_track(board, net, x0, y0, x1, y0, layer)
                add_track(board, net, x1, y0, x1, y1, layer)
            elif abs(x0 - x1) > 0.01 or abs(y0 - y1) > 0.01:
                add_track(board, net, x0, y0, x1, y1, layer)

    jobs = {
        "FLASH_CS": ("U5", "1", 11.30, [("R12", "2"), ("U1", "11")]),
        "SPI_MISO": ("U5", "2", 11.05, [("U1", "13")]),
        "SPI_SCK": ("U5", "6", 1.20, [("U1", "12")]),
        "SPI_MOSI": ("U5", "5", 1.45, [("U1", "14")]),
    }
    for name, (ref, pin, via_x, targets) in jobs.items():
        if name not in pads_by_net:
            continue
        net = find_net(board, name)
        pads = pads_by_net[name]
        back = pad_of(pads, ref, pin)
        _, bx, by = pad_anchor(back)
        manhattan(net, [(bx, by), (via_x, by)], pcbnew.B_Cu)
        add_via(board, net, via_x, by)
        points = [(via_x, by)]
        for tref, tpin in targets:
            _, tx, ty = pad_anchor(pad_of(pads, tref, tpin))
            points.append((via_x, ty))
            points.append((tx, ty))
        manhattan(net, points, pcbnew.F_Cu)
        print(f"routed {name} via explicit SPI fanout")
    return still


def route_i2c_scl(board: pcbnew.BOARD, pads_by_net: dict[str, list[pcbnew.PAD]]) -> list[str]:
    if "I2C_SCL" not in pads_by_net:
        return []
    net = find_net(board, "I2C_SCL")
    pads = pads_by_net["I2C_SCL"]
    pts = {f"{pad.GetParentFootprint().GetReference()}.{pad.GetNumber()}": pad_anchor(pad)[1:] for pad in pads}

    def manhattan(points: list[tuple[float, float]]) -> None:
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            if abs(x0 - x1) > 0.01 and abs(y0 - y1) > 0.01:
                add_track(board, net, x0, y0, x1, y0, pcbnew.F_Cu)
                add_track(board, net, x1, y0, x1, y1, pcbnew.F_Cu)
            elif abs(x0 - x1) > 0.01 or abs(y0 - y1) > 0.01:
                add_track(board, net, x0, y0, x1, y1, pcbnew.F_Cu)

    u3 = pts["U3.3"]
    u2 = pts["U2.13"]
    r2 = pts["R2.1"]
    u1 = pts["U1.20"]
    u4 = pts["U4.13"]
    bus_y = max(u3[1] + 0.55, u2[1])
    manhattan([u3, (u3[0], bus_y), (u2[0], bus_y), u2])
    manhattan([(u3[0], bus_y), (r2[0], bus_y), r2])
    manhattan([r2, (u1[0], r2[1]), u1])
    manhattan([u1, (u1[0], u4[1]), u4])
    print("routed I2C_SCL via explicit spine")
    return []


def add_power_vias(board: pcbnew.BOARD, pads_by_net: dict[str, list[pcbnew.PAD]]) -> int:
    count = 0
    used: list[tuple[float, float]] = []
    occ = seed_occupancy(board)

    def occupied(x: float, y: float) -> bool:
        cx, cy = occ.to_cell(x, y)
        return (cx, cy) in occ.via_blocked or (cx, cy) in occ.blocked[F_LAYER] or (cx, cy) in occ.blocked[B_LAYER]

    def place(net_name: str, x: float, y: float) -> bool:
        if not inside_board(x, y, EDGE + VIA_D / 2):
            return False
        if occupied(x, y):
            return False
        for ux, uy in used:
            if (ux - x) ** 2 + (uy - y) ** 2 < 0.80**2:
                return False
        if 4.4 <= x <= 7.6 and 0.4 <= y <= 3.6:
            return False
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(point(x, y))
        via.SetWidth(mm(VIA_D))
        via.SetDrill(mm(VIA_DRILL))
        via.SetViaType(pcbnew.VIATYPE_THROUGH)
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        via.SetNet(find_net(board, net_name))
        board.Add(via)
        used.append((x, y))
        occ.mark_circle(None, x, y, VIA_D / 2 + CLEAR + TRACK_W / 2)
        return True

    offsets = [(0.80, 0.0), (-0.80, 0.0), (0.0, 0.80), (0.0, -0.80), (0.65, 0.65), (-0.65, 0.65)]
    for net_name in ("3V3", "VBAT"):
        for pad in pads_by_net.get(net_name, []):
            _, x, y = pad_anchor(pad)
            for dx, dy in offsets:
                if place(net_name, x + dx, y + dy):
                    count += 1
                    break
    for x, y in (
        (1.6, 9.5),
        (10.4, 9.5),
        (1.6, 16.5),
        (10.4, 16.5),
        (1.6, 23.5),
        (10.4, 23.5),
        (6.0, 27.5),
        (3.0, 11.5),
        (9.0, 11.5),
    ):
        if place("GND", x, y):
            count += 1
    return count


def fill_zones(board: pcbnew.BOARD) -> None:
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())


def update_status(board: pcbnew.BOARD, routed: int, failed: list[str]) -> None:
    status = "ROUTING_CANDIDATE_NO_GERBER" if not failed else "PARTIAL_ROUTING_NO_GERBER"
    props = pcbnew.MAP_STRING_STRING()
    for key, value in {
        "REVISION": "Rev.A2",
        "RELEASE_STATUS": status,
        "BOARD_SIZE": "12x35x1.0mm",
        "STACKUP_INTENT": "F.Cu / In1.GND / In2.POWER / B.Cu",
        "ROUTED_SIGNAL_NETS": str(routed),
        "UNROUTED_SIGNAL_NETS": ",".join(failed),
    }.items():
        props[key] = value
    board.SetProperties(props)
    for drawing in board.GetDrawings():
        if drawing.GetClass() == "PCB_TEXT":
            text = drawing.GetText()
            if "NO GERBER" in text or "PLACEMENT ONLY" in text:
                drawing.SetText(f"SMART APO Rev.A2 | {status.replace('_', ' ')}")


def main() -> int:
    if not BOARD_PATH.exists():
        raise SystemExit(f"missing placement board {BOARD_PATH}; run generate_pcb_revA2.py first")
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    if pcbnew.GetBuildVersion() != "10.0.6":
        print(f"warning: designed for pcbnew 10.0.6, running {pcbnew.GetBuildVersion()}", file=sys.stderr)

    # regenerate from a clean placement board each run
    existing_tracks = list(board.GetTracks())
    existing_zones = list(board.Zones())
    for item in existing_tracks + existing_zones:
        board.Remove(item)

    add_planes(board)
    pads_by_net = collect_pads(board)

    failed: list[str] = []
    routed = 0
    pending = list(ROUTE_ORDER)
    for attempt in range(1):
        still: list[str] = []
        for name in pending:
            pads = pads_by_net.get(name, [])
            if len(pads) < 2:
                continue
            if attempt == 0 and name in failed:
                continue
            net = find_net(board, name)
            width = POWER_W if name in {"CHARGE_IN"} else TRACK_W
            if route_net(board, pads, net, width):
                routed += 1
                print(f"routed {name} ({len(pads)} pads)")
            else:
                still.append(name)
                print(f"FAILED {name} ({len(pads)} pads)")
        failed = still
        pending = still
        if not failed:
            break
        print(f"retry remaining: {failed}")

    if failed:
        spi_failed = [name for name in failed if name.startswith("SPI") or name == "FLASH_CS"]
        other_failed = [name for name in failed if name not in spi_failed]
        if spi_failed:
            other_failed = other_failed + route_spi_fanout(board, {name: pads_by_net[name] for name in spi_failed})
        if "I2C_SCL" in other_failed:
            other_failed = [n for n in other_failed if n != "I2C_SCL"] + route_i2c_scl(board, pads_by_net)
        failed = other_failed
        routed = sum(1 for name in ROUTE_ORDER if name not in failed and len(pads_by_net.get(name, [])) >= 2)

    via_count = add_power_vias(board, pads_by_net)
    try:
        fill_zones(board)
    except Exception as exc:
        print(f"zone fill failed: {exc}")
    update_status(board, routed, failed)
    pcbnew.Refresh() if hasattr(pcbnew, "Refresh") else None
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(
        f"saved {BOARD_PATH}: routed {routed}/{routed + len(failed)} signal nets, "
        f"{via_count} power/stitch vias, failed={failed or 'none'}"
    )
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
