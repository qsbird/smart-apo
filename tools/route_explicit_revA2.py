#!/usr/bin/env python3
"""Explicit manhattan router for Rev.A2. Maze autorouting is parked.

This script is a production *candidate* router. Official KiCad DRC must still
be zero before any fabrication export.
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
EDGE = 0.40
BOARD_W = 12.0
BOARD_H = 35.0

# Document order from CONTEXT_HANDOFF stage B.
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

F_LAYER, B_LAYER = 0, 1
LAYER_ID = {F_LAYER: pcbnew.F_Cu, B_LAYER: pcbnew.B_Cu}


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(x), mm(y))


def net_key(name: str) -> str:
    return name.lstrip("/")


def snap(value: float) -> float:
    return round(value / GRID) * GRID


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


def pad_layer(pad: pcbnew.PAD) -> int:
    if pad.IsOnLayer(pcbnew.B_Cu) and not pad.IsOnLayer(pcbnew.F_Cu):
        return B_LAYER
    return F_LAYER


def pad_xy(pad: pcbnew.PAD) -> tuple[float, float]:
    pos = pad.GetPosition()
    return pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)


def pad_of(pads: list[pcbnew.PAD], ref: str, number: str) -> pcbnew.PAD:
    for pad in pads:
        parent = pad.GetParentFootprint()
        if parent and parent.GetReference() == ref and pad.GetNumber() == number:
            return pad
    raise KeyError(f"{ref}.{number}")


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

    def segment_clear(self, layer: int, x0: float, y0: float, x1: float, y1: float, inflate: float) -> bool:
        if not inside_board(x0, y0) or not inside_board(x1, y1):
            return False
        steps = max(1, int(math.hypot(x1 - x0, y1 - y0) / GRID))
        bucket = self.blocked[layer]
        for i in range(steps + 1):
            t = i / steps
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            gx0 = max(0, int(math.floor((x - inflate) / GRID)))
            gx1 = min(self.nx - 1, int(math.ceil((x + inflate) / GRID)))
            gy0 = max(0, int(math.floor((y - inflate) / GRID)))
            gy1 = min(self.ny - 1, int(math.ceil((y + inflate) / GRID)))
            for gx in range(gx0, gx1 + 1):
                for gy in range(gy0, gy1 + 1):
                    if (gx, gy) in bucket:
                        return False
        return True

    def via_clear(self, x: float, y: float) -> bool:
        if not inside_board(x, y, EDGE + VIA_D / 2):
            return False
        cx, cy = self.to_cell(x, y)
        if (cx, cy) in self.via_blocked:
            return False
        radius = VIA_D / 2 + CLEAR
        gx0 = max(0, int(math.floor((x - radius) / GRID)))
        gx1 = min(self.nx - 1, int(math.ceil((x + radius) / GRID)))
        gy0 = max(0, int(math.floor((y - radius) / GRID)))
        gy1 = min(self.ny - 1, int(math.ceil((y + radius) / GRID)))
        r2 = radius * radius
        for gx in range(gx0, gx1 + 1):
            for gy in range(gy0, gy1 + 1):
                px, py = self.from_cell(gx, gy)
                if (px - x) ** 2 + (py - y) ** 2 <= r2:
                    if (gx, gy) in self.blocked[F_LAYER] or (gx, gy) in self.blocked[B_LAYER]:
                        return False
                    if (gx, gy) in self.via_blocked:
                        return False
        return True


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
    keepout = {
        "U3": (1.40, 1.40),
        "U2": (1.25, 1.50),
    }
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            name = net_key(pad.GetNetname() or "")
            if current_net and name == current_net:
                continue
            box = pad.GetBoundingBox()
            occ.mark_rect(
                pad_layer(pad),
                pcbnew.ToMM(box.GetLeft()),
                pcbnew.ToMM(box.GetRight()),
                pcbnew.ToMM(box.GetTop()),
                pcbnew.ToMM(box.GetBottom()),
                inflate,
            )
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
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref not in keepout or fp.IsFlipped():
            continue
        pos = fp.GetPosition()
        cx, cy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        hx, hy = keepout[ref]
        occ.mark_rect(F_LAYER, cx - hx, cx + hx, cy - hy, cy + hy, CLEAR)
    if current_net:
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if net_key(pad.GetNetname() or "") != current_net:
                    continue
                box = pad.GetBoundingBox()
                occ.clear_rect(
                    pad_layer(pad),
                    pcbnew.ToMM(box.GetLeft()),
                    pcbnew.ToMM(box.GetRight()),
                    pcbnew.ToMM(box.GetTop()),
                    pcbnew.ToMM(box.GetBottom()),
                    0.05,
                )
    return occ


def add_track(board: pcbnew.BOARD, occ: Occupancy, net: pcbnew.NETINFO_ITEM, x0: float, y0: float, x1: float, y1: float, layer: int, width: float) -> None:
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(point(x0, y0))
    track.SetEnd(point(x1, y1))
    track.SetWidth(mm(width))
    track.SetLayer(LAYER_ID[layer])
    track.SetNet(net)
    board.Add(track)
    occ.mark_rect(layer, x0, x1, y0, y1, CLEAR + width / 2)


def add_via(board: pcbnew.BOARD, occ: Occupancy, net: pcbnew.NETINFO_ITEM, x: float, y: float) -> None:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(x, y))
    via.SetWidth(mm(VIA_D))
    via.SetDrill(mm(VIA_DRILL))
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(net)
    board.Add(via)
    occ.mark_circle(None, x, y, VIA_D / 2 + CLEAR + TRACK_W / 2)


def try_path(occ: Occupancy, layer: int, points: list[tuple[float, float]], width: float) -> bool:
    inflate = CLEAR + width / 2 - 0.04
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if abs(x0 - x1) < 0.01 and abs(y0 - y1) < 0.01:
            continue
        if not occ.segment_clear(layer, x0, y0, x1, y1, inflate):
            return False
    return True


def commit_path(board: pcbnew.BOARD, occ: Occupancy, net: pcbnew.NETINFO_ITEM, layer: int, points: list[tuple[float, float]], width: float) -> None:
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if abs(x0 - x1) < 0.01 and abs(y0 - y1) < 0.01:
            continue
        add_track(board, occ, net, x0, y0, x1, y1, layer, width)


def manhattan_variants(a: tuple[float, float], b: tuple[float, float]) -> list[list[tuple[float, float]]]:
    ax, ay = snap(a[0]), snap(a[1])
    bx, by = snap(b[0]), snap(b[1])
    variants = [
        [(ax, ay), (bx, ay), (bx, by)],
        [(ax, ay), (ax, by), (bx, by)],
    ]
    mid_x = snap((ax + bx) / 2)
    mid_y = snap((ay + by) / 2)
    variants.append([(ax, ay), (mid_x, ay), (mid_x, by), (bx, by)])
    variants.append([(ax, ay), (ax, mid_y), (bx, mid_y), (bx, by)])
    for x in (1.10, 2.20, 9.80, 10.90):
        variants.append([(ax, ay), (x, ay), (x, by), (bx, by)])
    for y in (8.80, 19.20, 26.80, 33.10):
        variants.append([(ax, ay), (ax, y), (bx, y), (bx, by)])
    unique: list[list[tuple[float, float]]] = []
    seen: set[tuple[tuple[float, float], ...]] = set()
    for path in variants:
        key = tuple(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def find_via_site(occ: Occupancy, near: tuple[float, float]) -> tuple[float, float] | None:
    x0, y0 = snap(near[0]), snap(near[1])
    for radius in (0.0, 0.40, 0.80, 1.20, 1.60):
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            x, y = snap(x0 + dx * radius), snap(y0 + dy * radius)
            if occ.via_clear(x, y):
                return x, y
    for x in [1.0, 1.4, 10.6, 11.0, 2.0, 10.0]:
        for y in [y0, y0 - 0.8, y0 + 0.8]:
            if occ.via_clear(x, y):
                return snap(x), snap(y)
    return None


def pad_cells(occ: Occupancy, layer: int, x: float, y: float) -> list[tuple[int, int, int]]:
    cells: list[tuple[int, int, int]] = []
    for dx in (-0.15, 0.0, 0.15):
        for dy in (-0.15, 0.0, 0.15):
            cx, cy = occ.to_cell(x + dx, y + dy)
            if 0 <= cx < occ.nx and 0 <= cy < occ.ny and (cx, cy) not in occ.blocked[layer]:
                cells.append((layer, cx, cy))
    if not cells:
        cells.append((layer, *occ.to_cell(x, y)))
    return cells


def astar(occ: Occupancy, starts: list[tuple[int, int, int]], goals: list[tuple[int, int, int]]) -> list[tuple[int, int, int]] | None:
    goal_set = set(goals)
    frontier: list[tuple[float, int, tuple[int, int, int]]] = []
    counter = 0
    came: dict[tuple[int, int, int], tuple[int, int, int] | None] = {}
    cost: dict[tuple[int, int, int], float] = {}

    def heuristic(state: tuple[int, int, int]) -> float:
        return min(
            abs(state[1] - g[1]) + abs(state[2] - g[2]) + (0 if state[0] == g[0] else 10)
            for g in goals
        )

    for start in starts:
        came[start] = None
        cost[start] = 0.0
        heapq.heappush(frontier, (heuristic(start), counter, start))
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
        x, y = occ.from_cell(cx, cy)
        if occ.via_clear(x, y) and (cx, cy) not in occ.blocked[other]:
            new_cost = cost[current] + 8
            if via_state not in cost or new_cost < cost[via_state]:
                cost[via_state] = new_cost
                came[via_state] = current
                counter += 1
                heapq.heappush(frontier, (new_cost + heuristic(via_state), counter, via_state))
    return None


def commit_astar(board: pcbnew.BOARD, occ: Occupancy, net: pcbnew.NETINFO_ITEM, path: list[tuple[int, int, int]], width: float) -> None:
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
            add_via(board, occ, net, x, y)
    for start, end in segments:
        if start[1] == end[1] and start[2] == end[2]:
            continue
        x0, y0 = occ.from_cell(start[1], start[2])
        x1, y1 = occ.from_cell(end[1], end[2])
        add_track(board, occ, net, x0, y0, x1, y1, start[0], width)


def connect_two(
    board: pcbnew.BOARD,
    occ: Occupancy,
    net: pcbnew.NETINFO_ITEM,
    a: tuple[int, float, float],
    b: tuple[int, float, float],
    width: float,
) -> bool:
    if a[0] == b[0]:
        for path in manhattan_variants((a[1], a[2]), (b[1], b[2])):
            if try_path(occ, a[0], path, width):
                commit_path(board, occ, net, a[0], path, width)
                return True
    else:
        candidates = [
            find_via_site(occ, ((a[1] + b[1]) / 2, (a[2] + b[2]) / 2)),
            find_via_site(occ, (a[1], a[2])),
            find_via_site(occ, (b[1], b[2])),
            find_via_site(occ, (1.20, a[2])),
            find_via_site(occ, (10.80, a[2])),
        ]
        for site in candidates:
            if site is None:
                continue
            for path_a in manhattan_variants((a[1], a[2]), site):
                if not try_path(occ, a[0], path_a, width):
                    continue
                for path_b in manhattan_variants(site, (b[1], b[2])):
                    if try_path(occ, b[0], path_b, width) and occ.via_clear(*site):
                        commit_path(board, occ, net, a[0], path_a, width)
                        add_via(board, occ, net, *site)
                        commit_path(board, occ, net, b[0], path_b, width)
                        return True
    starts = pad_cells(occ, a[0], a[1], a[2])
    goals = pad_cells(occ, b[0], b[1], b[2])
    path = astar(occ, starts, goals)
    if path:
        commit_astar(board, occ, net, path, width)
        return True
    return False


def endpoints(pads: list[pcbnew.PAD]) -> list[tuple[int, float, float]]:
    return [(pad_layer(pad), *pad_xy(pad)) for pad in pads]


def route_net_explicit(board: pcbnew.BOARD, pads: list[pcbnew.PAD], net: pcbnew.NETINFO_ITEM, width: float) -> bool:
    if len(pads) < 2:
        return True
    occ = seed_occupancy(board, net_key(net.GetNetname()))
    pts = endpoints(pads)
    connected = {0}
    while len(connected) < len(pts):
        best = None
        pair = None
        for i in connected:
            for j, pt in enumerate(pts):
                if j in connected:
                    continue
                dist = abs(pts[i][1] - pt[1]) + abs(pts[i][2] - pt[2])
                if best is None or dist < best:
                    best = dist
                    pair = (i, j)
        assert pair is not None
        src, dst = pair
        if not connect_two(board, occ, net, pts[src], pts[dst], width):
            return False
        connected.add(dst)
        occ = seed_occupancy(board, net_key(net.GetNetname()))
    return True


def collect_pads(board: pcbnew.BOARD) -> dict[str, list[pcbnew.PAD]]:
    pads: dict[str, list[pcbnew.PAD]] = defaultdict(list)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            name = net_key(pad.GetNetname() or "")
            if name:
                pads[name].append(pad)
    return pads


def via_loose(board: pcbnew.BOARD, x: float, y: float) -> bool:
    if not inside_board(x, y, EDGE + VIA_D / 2):
        return False
    if 4.55 <= x <= 7.45 and 0.95 <= y <= 3.85:
        return False
    if 1.00 <= x <= 3.60 and 5.05 <= y <= 8.15:
        return False
    for track in board.GetTracks():
        if track.GetClass() != "PCB_VIA":
            continue
        pos = track.GetPosition()
        if (pcbnew.ToMM(pos.x) - x) ** 2 + (pcbnew.ToMM(pos.y) - y) ** 2 < 0.85**2:
            return False
    return True


def force_track(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, x0: float, y0: float, x1: float, y1: float, layer: int, width: float = TRACK_W) -> None:
    if abs(x0 - x1) < 0.01 and abs(y0 - y1) < 0.01:
        return
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(point(x0, y0))
    track.SetEnd(point(x1, y1))
    track.SetWidth(mm(width))
    track.SetLayer(LAYER_ID[layer])
    track.SetNet(net)
    board.Add(track)


def force_via(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, x: float, y: float) -> None:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(x, y))
    via.SetWidth(mm(VIA_D))
    via.SetDrill(mm(VIA_DRILL))
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(net)
    board.Add(via)


def force_manhattan(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, a: tuple[float, float], b: tuple[float, float], layer: int) -> None:
    ax, ay = a
    bx, by = b
    force_track(board, net, ax, ay, bx, ay, layer)
    force_track(board, net, bx, ay, bx, by, layer)


def route_priority_buses(board: pcbnew.BOARD, pads_by_net: dict[str, list[pcbnew.PAD]]) -> list[str]:
    """PARKED. Forced manhattan without occupancy checks raised official DRC
    from 84 to 328 errors (shorts 68, keepout 12, mask bridges 167).
    """
    del board, pads_by_net
    return []


def force_connect(board: pcbnew.BOARD, pads_by_net: dict[str, list[pcbnew.PAD]], name: str, pairs: list[tuple[str, str, str, str]]) -> bool:
    if name not in pads_by_net:
        return True
    net = find_net(board, name)
    pads = pads_by_net[name]
    occ = seed_occupancy(board, name)
    for a_ref, a_pin, b_ref, b_pin in pairs:
        a = pad_of(pads, a_ref, a_pin)
        b = pad_of(pads, b_ref, b_pin)
        if not connect_two(board, occ, net, (pad_layer(a), *pad_xy(a)), (pad_layer(b), *pad_xy(b)), TRACK_W):
            return False
        occ = seed_occupancy(board, name)
    print(f"routed {name} via leftover explicit pairs")
    return True


def route_leftovers(board: pcbnew.BOARD, pads_by_net: dict[str, list[pcbnew.PAD]], failed: list[str]) -> list[str]:
    jobs = {
        "I2C_SCL": [("U3", "3", "U2", "13"), ("U2", "13", "R2", "1"), ("R2", "1", "U1", "20"), ("U1", "20", "U4", "13")],
        "IMU_INT": [("U2", "4", "U1", "7")],
        "BRIDGE_S+": [("J3", "3", "U4", "1")],
        "BRIDGE_S-": [("J3", "4", "U4", "7")],
        "BRIDGE_E+": [("J3", "1", "U4", "16"), ("U4", "16", "C6", "1")],
        "NRST": [("U1", "6", "C17", "1"), ("C17", "1", "R11", "2"), ("U1", "6", "J2", "7")],
        "VBAT_SENSE": [("U1", "8", "C14", "1"), ("C14", "1", "R4", "2"), ("R4", "2", "R5", "1")],
        "CHARGE_IN": [("U6", "4", "C11", "1"), ("C11", "1", "J2", "2")],
        "FLASH_CS": [("U5", "1", "R12", "2"), ("R12", "2", "U1", "11")],
        "SPI_MISO": [("U5", "2", "U1", "13")],
        "SPI_MOSI": [("U5", "5", "U1", "14")],
    }
    still: list[str] = []
    for name in failed:
        if name in jobs and force_connect(board, pads_by_net, name, jobs[name]):
            continue
        still.append(name)
    return still


def add_power_vias(board: pcbnew.BOARD, pads_by_net: dict[str, list[pcbnew.PAD]]) -> int:
    count = 0
    used: list[tuple[float, float]] = []

    def blocked_keepout(x: float, y: float) -> bool:
        return (4.6 <= x <= 7.4 and 1.0 <= y <= 3.8) or (1.05 <= x <= 3.55 and 5.1 <= y <= 8.1)

    def place(net_name: str, x: float, y: float) -> bool:
        x, y = snap(x), snap(y)
        if not inside_board(x, y, EDGE + VIA_D / 2):
            return False
        if blocked_keepout(x, y):
            return False
        for ux, uy in used:
            if (ux - x) ** 2 + (uy - y) ** 2 < 0.90**2:
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
        return True

    # Sparse stitch only. Pad-adjacent 0.60 vias on this 12 mm board caused a
    # DRC regression (67 -> 149 errors) and are parked.
    for x, y in (
        (1.7, 10.2),
        (10.3, 12.8),
        (1.7, 16.8),
        (10.3, 19.8),
        (1.7, 22.8),
        (6.0, 27.8),
    ):
        if place("GND", x, y):
            count += 1
    return count


def update_status(board: pcbnew.BOARD, routed: int, failed: list[str]) -> None:
    status = "EXPLICIT_ROUTING_NO_GERBER" if not failed else "PARTIAL_EXPLICIT_ROUTING_NO_GERBER"
    props = pcbnew.MAP_STRING_STRING()
    for key, value in {
        "REVISION": "Rev.A2",
        "RELEASE_STATUS": status,
        "BOARD_SIZE": "12x35x1.0mm",
        "STACKUP_INTENT": "F.Cu / In1.GND / In2.POWER / B.Cu",
        "VIA_RULE": "0.60/0.30",
        "ROUTED_SIGNAL_NETS": str(routed),
        "UNROUTED_SIGNAL_NETS": ",".join(failed),
        "ROUTER": "explicit_manhattan_maze_parked",
    }.items():
        props[key] = value
    board.SetProperties(props)
    for drawing in board.GetDrawings():
        if drawing.GetClass() == "PCB_TEXT":
            text = drawing.GetText()
            if "NO GERBER" in text or "PLACEMENT" in text or "ROUTING" in text:
                drawing.SetText(f"SMART APO Rev.A2 | {status.replace('_', ' ')}")


def main() -> int:
    if not BOARD_PATH.exists():
        raise SystemExit(f"missing placement board {BOARD_PATH}; run generate_pcb_revA2.py first")
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    if pcbnew.GetBuildVersion() != "10.0.6":
        print(f"warning: designed for pcbnew 10.0.6, running {pcbnew.GetBuildVersion()}", file=sys.stderr)

    for item in list(board.GetTracks()) + list(board.Zones()):
        board.Remove(item)

    add_planes(board)
    pads_by_net = collect_pads(board)

    # Forced edge buses without clearance checks (route_priority_buses)
    # parked after DRC 84 -> 328. Occupancy-checked routing only.
    routed = 0
    failed: list[str] = []
    for name in ROUTE_ORDER:
        pads = pads_by_net.get(name, [])
        if len(pads) < 2:
            continue
        net = find_net(board, name)
        width = POWER_W if name in {"CHARGE_IN"} else TRACK_W
        if route_net_explicit(board, pads, net, width):
            routed += 1
            print(f"routed {name} ({len(pads)} pads)")
        else:
            failed.append(name)
            print(f"FAILED {name} ({len(pads)} pads)")

    leftover = route_leftovers(board, pads_by_net, failed)
    recovered = [name for name in failed if name not in leftover]
    routed += len(recovered)
    failed = leftover

    via_count = add_power_vias(board, pads_by_net)
    try:
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
    except Exception as exc:
        print(f"zone fill failed: {exc}")
    update_status(board, routed, failed)
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(
        f"saved {BOARD_PATH}: routed {routed}/{routed + len(failed)} signal nets, "
        f"{via_count} power/stitch vias, failed={failed or 'none'}"
    )
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
