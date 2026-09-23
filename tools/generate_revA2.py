#!/usr/bin/env python3
"""Generate the independent Rev.A2 schematic and project libraries.

Rev.A1 is imported only as a data source.  Every output is written below
hardware/revA2 so the archived Rev.A1 deliverables cannot be overwritten.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import csv
import uuid

ROOT = Path(__file__).resolve().parents[1]
HW = ROOT / "hardware"
REV = HW / "revA2"
LIB = REV / "smart_apo_revA2.kicad_sym"
OUT = REV / "smart_apo_common_revA2.kicad_sch"

MCU_PIN_NAMES = {
    1: "PB7/PB8", 2: "PB9/PC14-OSC32_IN", 3: "PC15-OSC32_OUT", 4: "VDD/VDDA",
    5: "VSS/VSSA", 6: "PF2-NRST", 7: "PA0", 8: "PA1", 9: "PA2", 10: "PA3",
    11: "PA4", 12: "PA5", 13: "PA6", 14: "PA7", 15: "PB0/PB1/PB2/PA8",
    16: "PA11[PA9]", 17: "PA12[PA10]", 18: "PA13", 19: "PA15/PA14-BOOT0",
    20: "PB3/PB4/PB5/PB6",
}

MCU_PIN_NETS = {
    1: "I2C_SDA", 2: "LSE_IN", 3: "LSE_OUT", 4: "3V3", 5: "GND", 6: "NRST",
    7: "IMU_INT", 8: "VBAT_SENSE", 9: "UART_TX", 10: "UART_RX", 11: "FLASH_CS",
    12: "SPI_SCK", 13: "SPI_MISO", 14: "SPI_MOSI", 15: "LED_GATE", 16: "REED_WAKE",
    17: "STRAIN_DRDY", 18: "SWDIO", 19: "SWCLK", 20: "I2C_SCL",
}

SYMBOLS = {
    "MCU20": [MCU_PIN_NAMES[index] for index in range(1, 21)],
    "IMU14": ["SDO/SA0", "SDx", "SCx", "INT1", "VDDIO", "GND", "GND", "VDD",
              "INT2", "OCS_AUX", "SDO_AUX", "CS", "SCL", "SDA"],
    "PRESS7": ["SDA", "SA0", "SCL", "INT_DRDY", "GND", "VDD", "PAD2LID"],
    "ADC16": ["REFP", "VIN1N", "VIN1P", "VIN2N", "VIN2P", "VBG", "REFN", "AVSS",
              "DVSS", "XIN", "XOUT", "DRDY", "SCLK", "SDIO", "DVDD", "AVDD/LDO"],
    "FLASH8": ["/CS", "DO/IO1", "/WP/IO2", "GND", "DI/IO0", "CLK", "/HOLD/IO3", "VCC"],
    "CHARGER5": ["STAT", "VSS", "VBAT", "VDD", "PROG"],
    "LDO5": ["IN", "GND", "EN", "NC", "OUT"],
    "MOS3": ["G", "S", "D"],
    "PASSIVE2": ["1", "2"],
    "CONN6": ["E+", "E-", "S+", "S-", "A+", "A-"],
    "CONN7": ["GND", "CHARGE_IN", "SWDIO", "SWCLK", "UART_TX", "UART_RX", "NRST"],
}


PIN_TYPES = {
    "MCU20": [
        "bidirectional", "input", "output", "power_in", "power_in",
        "input", "bidirectional", "bidirectional", "bidirectional", "bidirectional",
        "bidirectional", "bidirectional", "bidirectional", "bidirectional", "bidirectional",
        "bidirectional", "bidirectional", "bidirectional", "bidirectional", "bidirectional",
    ],
    "IMU14": [
        "input", "passive", "input", "output", "power_in", "power_in", "power_in",
        "power_in", "no_connect", "no_connect", "passive", "input", "input", "bidirectional",
    ],
    "PRESS7": ["bidirectional", "input", "input", "no_connect", "power_in", "power_in", "passive"],
    "ADC16": [
        "input", "input", "input", "input", "input", "output", "input", "power_in",
        "power_in", "no_connect", "no_connect", "output", "input", "bidirectional", "power_in", "power_out",
    ],
    "FLASH8": ["input", "output", "input", "power_in", "bidirectional", "input", "input", "power_in"],
    "CHARGER5": ["tri_state", "power_in", "power_out", "power_in", "input"],
    "LDO5": ["power_in", "power_in", "input", "no_connect", "power_out"],
    "MOS3": ["input", "passive", "passive"],
    "PASSIVE2": ["passive", "passive"],
    "CONN6": ["passive"] * 6,
    "CONN7": ["power_out", "power_out", "passive", "passive", "passive", "passive", "passive"],
}


def symbol_text(name: str, pins: list[str]) -> str:
    nleft = (len(pins) + 1) // 2
    nright = len(pins) - nleft
    rows = max(nleft, nright)
    half_h = max(3.81, (rows - 1) * 1.27 / 2 + 1.27)
    half_w = 7.62 if len(pins) > 8 else 5.08
    lines = [
        f'  (symbol "{name}"',
        '    (pin_names (offset 0.762))',
        '    (exclude_from_sim no)', '    (in_bom yes)', '    (on_board yes)',
        f'    (property "Reference" "U" (at 0 {half_h + 1.27:.3f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Value" "{name}" (at 0 {-half_h - 1.27:.3f} 0) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        '    (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        '    (property "Description" "Smart Apo Rev.A2 reviewed electrical pin types" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        f'    (symbol "{name}_0_1"',
        f'      (rectangle (start {-half_w:.3f} {half_h:.3f}) (end {half_w:.3f} {-half_h:.3f})',
        '        (stroke (width 0) (type default)) (fill (type background))))',
        f'    (symbol "{name}_1_1"',
    ]
    for index, (pin_name, pin_type) in enumerate(zip(pins, PIN_TYPES[name]), 1):
        if index <= nleft:
            y = (nleft - 1) * 1.27 / 2 - (index - 1) * 1.27
            x, rotation = -half_w - 2.54, 0
        else:
            offset = index - nleft - 1
            y = -(nright - 1) * 1.27 / 2 + offset * 1.27
            x, rotation = half_w + 2.54, 180
        lines += [
            f'      (pin {pin_type} line (at {x:.3f} {y:.3f} {rotation}) (length 2.54)',
            f'        (name "{pin_name}" (effects (font (size 1.0 1.0))))',
            f'        (number "{index}" (effects (font (size 1.0 1.0)))))',
        ]
    lines += ['    )', '  )']
    return "\n".join(lines)


def rev_a1_hashes() -> dict[str, str]:
    hashes = {}
    for path in sorted(ROOT.rglob("*revA1*")):
        if path.is_file() and REV not in path.parents:
            hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def write_project_tables() -> None:
    (REV / "sym-lib-table").write_text(
        '(sym_lib_table\n  (lib (name "SmartApoRevA2")(type "KiCad")(uri "${KIPRJMOD}/smart_apo_revA2.kicad_sym")(options "")(descr "Rev.A2 reviewed project symbols"))\n)\n'
    )
    (REV / "fp-lib-table").write_text(
        '(fp_lib_table\n  (lib (name "SmartApoRevA2")(type "KiCad")(uri "${KIPRJMOD}/SmartApoRevA2.pretty")(options "")(descr "Rev.A2 project footprints"))\n)\n'
    )


def extract_balanced(text: str, start: int) -> tuple[str, int]:
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[start:index + 1], index + 1
    raise ValueError("unbalanced KiCad S-expression")


def type_embedded_symbols(source: str) -> str:
    for name, types in PIN_TYPES.items():
        marker = f'(symbol "smart_apo_symbols:{name}"'
        start = source.index(marker)
        block, end = extract_balanced(source, start)
        if block.count("(pin passive line") != len(types):
            raise ValueError(f"{name}: unexpected pin count in Rev.A1 schematic")
        pin_types = iter(types)
        block = re.sub(
            r"\(pin passive line",
            lambda _match: f"(pin {next(pin_types)} line",
            block,
        )
        source = source[:start] + block + source[end:]
    return source


def shift_off_grid_symbol(source: str, reference: str, symbol_name: str, delta_y: float = 0.635) -> str:
    """Move one symbol and its pin-attached labels onto the 1.27 mm grid."""
    reference_marker = f'(property "Reference" "{reference}"'
    reference_pos = source.index(reference_marker)
    placed_start = source.rfind("\n\t(symbol\n", 0, reference_pos) + 2
    placed_block, placed_end = extract_balanced(source, placed_start)
    placement = re.search(r"\(at (-?[0-9.]+) (-?[0-9.]+) (-?[0-9.]+)\)", placed_block)
    if not placement:
        raise ValueError(f"{reference}: placement not found")
    center_x, center_y, rotation = map(float, placement.groups())
    if rotation != 0:
        raise ValueError(f"{reference}: unsupported rotation {rotation}")

    embedded_marker = f'(symbol "smart_apo_symbols:{symbol_name}"'
    embedded_start = source.index(embedded_marker)
    embedded_block, _ = extract_balanced(source, embedded_start)
    local_pins = [
        (float(match.group(1)), float(match.group(2)))
        for match in re.finditer(
            r"\(pin passive line\s*\(at (-?[0-9.]+) (-?[0-9.]+) [-0-9.]+\)",
            embedded_block,
        )
    ]
    endpoints = {(round(center_x + x, 6), round(center_y - y, 6)) for x, y in local_pins}

    def shift_at(match: re.Match[str]) -> str:
        return f"(at {match.group(1)} {float(match.group(2)) + delta_y:.6g}"

    shifted_block = re.sub(r"\(at (-?[0-9.]+) (-?[0-9.]+)", shift_at, placed_block)
    source = source[:placed_start] + shifted_block + source[placed_end:]

    def shift_endpoint(match: re.Match[str]) -> str:
        x, y = float(match.group(1)), float(match.group(2))
        if (round(x, 6), round(y, 6)) in endpoints:
            return f"(at {match.group(1)} {y + delta_y:.6g}"
        return match.group(0)

    return re.sub(r"\(at (-?[0-9.]+) (-?[0-9.]+)", shift_endpoint, source)


def align_odd_symbol_pin_grid(source: str, symbol_name: str, reference: str) -> str:
    """Move half-grid pins in odd-count symbols and their labels onto the grid."""
    embedded_marker = f'(symbol "smart_apo_symbols:{symbol_name}"'
    embedded_start = source.index(embedded_marker)
    embedded_block, embedded_end = extract_balanced(source, embedded_start)
    pin_pattern = re.compile(
        r"(\(pin passive line\s*\(at )(-?[0-9.]+) (-?[0-9.]+) (-?[0-9.]+)(\))"
    )
    pins = list(pin_pattern.finditer(embedded_block))
    local_changes: list[tuple[float, float, float]] = []
    for pin in pins:
        x, old_y = float(pin.group(2)), float(pin.group(3))
        scaled = old_y / 1.27
        new_y = old_y + 0.635 if abs(scaled - round(scaled)) > 1e-6 else old_y
        local_changes.append((x, old_y, new_y))

    change_iter = iter(local_changes)

    def replace_pin(match: re.Match[str]) -> str:
        _x, _old_y, new_y = next(change_iter)
        return f"{match.group(1)}{match.group(2)} {new_y:.6g} {match.group(4)}{match.group(5)}"

    embedded_block = pin_pattern.sub(replace_pin, embedded_block)
    source = source[:embedded_start] + embedded_block + source[embedded_end:]

    reference_pos = source.index(f'(property "Reference" "{reference}"')
    placed_start = source.rfind("\n\t(symbol\n", 0, reference_pos) + 2
    placed_block, _ = extract_balanced(source, placed_start)
    placement = re.search(r"\(at (-?[0-9.]+) (-?[0-9.]+) (-?[0-9.]+)\)", placed_block)
    if not placement or float(placement.group(3)) != 0:
        raise ValueError(f"{reference}: unsupported placement for pin-grid alignment")
    center_x, center_y = float(placement.group(1)), float(placement.group(2))
    endpoint_map = {
        (round(center_x + x, 6), round(center_y - old_y, 6)): center_y - new_y
        for x, old_y, new_y in local_changes
        if old_y != new_y
    }

    def shift_annotation(match: re.Match[str]) -> str:
        x, y = float(match.group(1)), float(match.group(2))
        new_y = endpoint_map.get((round(x, 6), round(y, 6)))
        if new_y is None:
            return match.group(0)
        return f"(at {match.group(1)} {new_y:.6g}"

    return re.sub(r"\(at (-?[0-9.]+) (-?[0-9.]+)", shift_annotation, source)


def replace_label_with_no_connect(source: str, label: str) -> str:
    marker = f'(label "{label}"'
    start = source.index(marker)
    block, end = extract_balanced(source, start)
    position = re.search(r"\(at (-?[0-9.]+) (-?[0-9.]+)", block)
    uuid = re.search(r'\(uuid "([^"]+)"\)', block)
    if not position or not uuid:
        raise ValueError(f"{label}: label position or UUID missing")
    replacement = (
        f'(no_connect\n\t\t(at {position.group(1)} {position.group(2)})\n'
        f'\t\t(uuid "{uuid.group(1)}")\n\t)'
    )
    return source[:start] + replacement + source[end:]


def rename_embedded_pins(source: str, symbol_name: str, pin_names: dict[int, str]) -> str:
    marker = f'(symbol "smart_apo_symbols:{symbol_name}"'
    start = source.index(marker)
    block, end = extract_balanced(source, start)
    replacements = []
    for match in re.finditer(r"\(pin passive line", block):
        pin_block, pin_end = extract_balanced(block, match.start())
        number_match = re.search(r'\(number "([0-9]+)"', pin_block)
        if not number_match:
            raise ValueError(f"{symbol_name}: pin number missing")
        number = int(number_match.group(1))
        new_pin = re.sub(r'\(name "[^"]+"', f'(name "{pin_names[number]}"', pin_block, count=1)
        replacements.append((match.start(), pin_end, new_pin))
    for pin_start, pin_end, new_pin in reversed(replacements):
        block = block[:pin_start] + new_pin + block[pin_end:]
    return source[:start] + block + source[end:]


def relabel_symbol_pins(source: str, reference: str, symbol_name: str, pin_nets: dict[int, str]) -> str:
    reference_pos = source.index(f'(property "Reference" "{reference}"')
    placed_start = source.rfind("\n\t(symbol\n", 0, reference_pos) + 2
    placed_block, _ = extract_balanced(source, placed_start)
    placement = re.search(r"\(at (-?[0-9.]+) (-?[0-9.]+) (-?[0-9.]+)\)", placed_block)
    if not placement or float(placement.group(3)) != 0:
        raise ValueError(f"{reference}: unsupported placement for net relabel")
    center_x, center_y = float(placement.group(1)), float(placement.group(2))

    marker = f'(symbol "smart_apo_symbols:{symbol_name}"'
    embedded_start = source.index(marker)
    embedded_block, _ = extract_balanced(source, embedded_start)
    endpoints = {}
    for match in re.finditer(r"\(pin passive line", embedded_block):
        pin_block, _ = extract_balanced(embedded_block, match.start())
        at_match = re.search(r"\(at (-?[0-9.]+) (-?[0-9.]+) [-0-9.]+\)", pin_block)
        number_match = re.search(r'\(number "([0-9]+)"', pin_block)
        if not at_match or not number_match:
            raise ValueError(f"{symbol_name}: pin geometry missing")
        number = int(number_match.group(1))
        x = center_x + float(at_match.group(1))
        y = center_y - float(at_match.group(2))
        endpoints[(round(x, 6), round(y, 6))] = number

    replacements = []
    relabeled = set()
    for match in re.finditer(r"\n\t\(label ", source):
        label_start = match.start() + 2
        label_block, label_end = extract_balanced(source, label_start)
        at_match = re.search(r"\(at (-?[0-9.]+) (-?[0-9.]+)", label_block)
        if not at_match:
            continue
        key = (round(float(at_match.group(1)), 6), round(float(at_match.group(2)), 6))
        number = endpoints.get(key)
        if number is None:
            continue
        new_label = re.sub(r'^\(label "[^"]+"', f'(label "{pin_nets[number]}"', label_block, count=1)
        replacements.append((label_start, label_end, new_label))
        relabeled.add(number)
    if relabeled != set(pin_nets):
        raise ValueError(f"{reference}: labels missing for pins {sorted(set(pin_nets) - relabeled)}")
    for label_start, label_end, new_label in reversed(replacements):
        source = source[:label_start] + new_label + source[label_end:]
    return source


def add_flash_cs_pullup(source: str) -> str:
    """Clone R11 as deterministic R12 between 3V3 and FLASH_CS."""
    reference_pos = source.index('(property "Reference" "R11"')
    start = source.rfind("\n\t(symbol\n", 0, reference_pos) + 2
    block, end = extract_balanced(source, start)

    def shift_x(match: re.Match[str]) -> str:
        return f"(at {float(match.group(1)) + 35.56:.6g} {match.group(2)}"

    clone = re.sub(r"\(at (-?[0-9.]+) (-?[0-9.]+)", shift_x, block)
    clone = clone.replace('"R11"', '"R12"')

    def replace_uuid(match: re.Match[str]) -> str:
        deterministic = uuid.uuid5(uuid.NAMESPACE_URL, f"smart-apo-revA2-R12-{match.group(1)}")
        return f'(uuid "{deterministic}")'

    clone = re.sub(r'\(uuid "([^"]+)"\)', replace_uuid, clone)
    source = source[:end] + "\n\t" + clone + source[end:]

    label_insert = source.index("\n\t(no_connect")
    labels = """
	(label "3V3"
		(at 107.95 252.73 180)
		(effects (font (size 0.8 0.8)) (justify left bottom))
		(uuid "b6e7890f-f92e-5960-9c21-30e495e56e8d")
	)
	(label "FLASH_CS"
		(at 123.19 252.73 0)
		(effects (font (size 0.8 0.8)) (justify right bottom))
		(uuid "aa0c5cd4-511b-527a-a2b3-0fda60d26ca6")
	)
"""
    return source[:label_insert] + labels + source[label_insert:]


DIVIDER_VALUES = {"R4": "180k", "R5": "60.4k"}


def update_divider_values(source: str) -> str:
    """Update only instance value fields; never rebuild the current board."""
    for reference, value in DIVIDER_VALUES.items():
        pattern = (r'(\(property "Reference" "' + reference +
                   r'"(?:(?!\(property "Reference").)*?\(property "Value" ")[^"]+(")')
        source, count = re.subn(pattern, lambda match: match[1] + value + match[2], source, flags=re.S)
        if count != 1:
            raise ValueError(f"{reference}: expected exactly one instance value")
    return source


def build() -> dict:
    REV.mkdir(parents=True, exist_ok=True)
    (REV / "SmartApoRevA2.pretty").mkdir(exist_ok=True)

    source = (HW / "smart_apo_common_revA1.kicad_sch").read_text()
    for symbol_name, reference in {
        "MOS3": "Q1",
        "CHARGER5": "U6",
        "LDO5": "U7",
        "CONN7": "J2",
        "PRESS7": "U3",
    }.items():
        source = align_odd_symbol_pin_grid(source, symbol_name, reference)
    for reference, symbol_name in {
        "U1": "MCU20",
        "U5": "FLASH8",
        "U4": "ADC16",
    }.items():
        source = shift_off_grid_symbol(source, reference, symbol_name)
    source = relabel_symbol_pins(source, "U1", "MCU20", MCU_PIN_NETS)
    source = rename_embedded_pins(source, "MCU20", MCU_PIN_NAMES)
    source = add_flash_cs_pullup(source)
    source = replace_label_with_no_connect(source, "CHG_STAT")
    source = type_embedded_symbols(source)
    source = source.replace("smart_apo_symbols:", "SmartApoRevA2:")
    source = source.replace("Rev.A1", "Rev.A2").replace("revA1", "revA2")
    source = source.replace(
        "Package_LGA:LGA-14_2.5x3mm_P0.5mm",
        "SmartApoRevA2:LGA-14_3x2.5mm_P0.5mm_LSM6DSO",
    )
    source = source.replace(
        "Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y",
        "SmartApoRevA2:LGA-14_3x2.5mm_P0.5mm_LSM6DSO",
    )
    source = source.replace(
        "Package_DFN_QFN:WSON-8-1EP_6x8mm_P1.27mm",
        "SmartApoRevA2:WSON-8_W25Q256JV_8x6mm_AN0000009",
    )
    source = source.replace(
        "SmartApo:CCLGA-7_LPS28DFW",
        "SmartApoRevA2:LPS28DFW_CCLGA-7L",
    )
    source = source.replace(
        "Connector_Wire:SolderWire-1sqmm_1x02_P3.9mm_D1.4mm_OD2.7mm",
        "SmartApoRevA2:BATTERY_WIRE_PADS",
    )
    source = source.replace("SmartApo:POGO_7x1.27mm", "SmartApoRevA2:POGO_7x1.27mm")
    source = source.replace("SmartApo:PAD_6x1.27mm", "SmartApoRevA2:PAD_6x1.27mm")
    source = source.replace(
        "Button_Switch_SMD:SW_SPST_MK16",
        "SmartApoRevA2:REED_CT05_COMPACT",
    )
    source = update_divider_values(source)
    OUT.write_text(source)

    # Build the project library from the exact embedded definitions so KiCad's
    # rescue/cache comparison sees identical symbol data.
    body = ['(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor)']
    for name in SYMBOLS:
        marker = f'(symbol "SmartApoRevA2:{name}"'
        start = source.index(marker)
        block, _ = extract_balanced(source, start)
        body.append(block.replace(f'"SmartApoRevA2:{name}"', f'"{name}"', 1))
    body.append(')')
    LIB.write_text("\n".join(body) + "\n")

    # Preserve both assembly variants while keeping the existing placement data
    # explicitly reference-only until the Rev.A2 PCB is rebuilt.
    for source_name, output_name in {
        "BOM_revA1_JLCPCB.csv": "BOM_revA2_WORKING.csv",
        "ASSEMBLY_VARIANTS_revA1.csv": "ASSEMBLY_VARIANTS_revA2.csv",
        "pin_net_review_revA1.csv": "pin_net_review_revA2.csv",
        "CPL_revA1.csv": "CPL_revA1_REFERENCE_ONLY.csv",
    }.items():
        (REV / output_name).write_text((HW / source_name).read_text())

    pin_review = REV / "pin_net_review_revA2.csv"
    with pin_review.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
        fieldnames = list(rows[0])
    for row in rows:
        if row["Reference"] == "U1":
            number = int(row["Pin"])
            row["Pin name"] = MCU_PIN_NAMES[number]
            row["Net"] = MCU_PIN_NETS[number]
    with pin_review.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    bom_path = REV / "BOM_revA2_WORKING.csv"
    with bom_path.open(newline="") as stream:
        bom_rows = list(csv.DictReader(stream))
        bom_fields = list(bom_rows[0])
    for row in bom_rows:
        if row["Designator"] in DIVIDER_VALUES:
            row["Comment"] = DIVIDER_VALUES[row["Designator"]] + " 1%"
        if row["Designator"] == "U5":
            row["Footprint"] = "WSON-8_8x6mm_P1.27"
            row["Notes"] = "Winbond AN0000009 p21 PCB land; C5334276 catalog MPN matches; incoming lot and carrier remain unverified"
        if "C14" in row["Designator"].split():
            row["Notes"] += "; C14 tolerance <=20% (startup RC guard)"
    insert_at = next(index for index, row in enumerate(bom_rows) if row["Designator"] == "R11") + 1
    bom_rows.insert(insert_at, {
        "Comment": "10k 1%", "Designator": "R12", "Footprint": "0402", "LCSC Part #": "",
        "Manufacturer Part": "Generic thick film", "AWA Qty": "1", "UNDERWATER Qty": "1",
        "Assembly": "SMT", "Notes": "W25Q256 /CS reset-state pullup",
    })
    with bom_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=bom_fields)
        writer.writeheader()
        writer.writerows(bom_rows)

    variants_path = REV / "ASSEMBLY_VARIANTS_revA2.csv"
    variant_text = variants_path.read_text().replace(
        "R1 R2 R3 R4 R5 R10 R11,",
        "R1 R2 R3 R4 R5 R10 R11 R12,",
    )
    variants_path.write_text(variant_text)

    with (REV / "revA1_baseline_sha256.json").open("w") as stream:
        json.dump(rev_a1_hashes(), stream, indent=2, sort_keys=True)
        stream.write("\n")

    write_project_tables()
    report = {
        "revision": "A2",
        "source_revision": "A1_read_only",
        "components": source.count("\n\t(symbol\n"),
        "typed_symbol_pins": sum(map(len, PIN_TYPES.values())),
        "project_symbol_library": str(LIB),
        "official_erc": "PENDING_KICAD10_RERUN_AFTER_GENERATION",
        "pcb_status": "PENDING_REBUILD_FROM_REVIEWED_SCHEMATIC",
        "circuit_changes": "CORRECTED_STM32_TSSOP20_PINOUT_AND_ADDED_FLASH_CS_PULLUP",
    }
    (REV / "generation_report_revA2.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
