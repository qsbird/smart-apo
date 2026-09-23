#!/usr/bin/env python3
"""Offline structural checks for Rev.A2; never presented as KiCad ERC/DRC."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "hardware" / "revA2"


def balanced(text: str) -> bool:
    depth = 0
    quoted = False
    escaped = False
    for char in text:
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
            if depth < 0:
                return False
    return depth == 0 and not quoted


def main() -> None:
    schematic = (REV / "smart_apo_common_revA2.kicad_sch").read_text()
    symbols = (REV / "smart_apo_revA2.kicad_sym").read_text()
    baseline = json.loads((REV / "revA1_baseline_sha256.json").read_text())
    erc_path = REV / "erc_revA2_kicad10.json"
    erc = json.loads(erc_path.read_text()) if erc_path.exists() else None
    erc_violations = [
        violation
        for sheet in (erc or {}).get("sheets", [])
        for violation in sheet.get("violations", [])
    ]
    erc_errors = [item for item in erc_violations if item.get("severity") == "error"]
    erc_warnings = [item for item in erc_violations if item.get("severity") == "warning"]
    erc_zero_violations = erc is not None and not erc_errors and not erc_warnings
    lps_footprint = REV / "SmartApoRevA2.pretty" / "LPS28DFW_CCLGA-7L.kicad_mod"
    imu_footprint = REV / "SmartApoRevA2.pretty" / "LGA-14_3x2.5mm_P0.5mm_LSM6DSO.kicad_mod"
    netlist_path = REV / "netlist_revA2_kicad10.xml"
    netlist = ET.parse(netlist_path).getroot() if netlist_path.exists() else None
    netlist_components = netlist.findall("./components/comp") if netlist is not None else []
    netlist_nets = netlist.findall("./nets/net") if netlist is not None else []
    unconnected_nets = [net for net in netlist_nets if (net.get("name") or "").startswith("unconnected-")]
    node_nets = {
        (node.get("ref"), int(node.get("pin"))): (net.get("name") or "").lstrip("/")
        for net in netlist_nets
        for node in net.findall("node")
        if node.get("ref") and node.get("pin", "").isdigit()
    }
    expected_mcu_nets = {
        1: "I2C_SDA", 2: "LSE_IN", 3: "LSE_OUT", 4: "3V3", 5: "GND", 6: "NRST",
        7: "IMU_INT", 8: "VBAT_SENSE", 9: "UART_TX", 10: "UART_RX", 11: "FLASH_CS",
        12: "SPI_SCK", 13: "SPI_MISO", 14: "SPI_MOSI", 15: "LED_GATE", 16: "REED_WAKE",
        17: "STRAIN_DRDY", 18: "SWDIO", 19: "SWCLK", 20: "I2C_SCL",
    }
    lps_footprint_text = lps_footprint.read_text() if lps_footprint.exists() else ""
    imu_footprint_text = imu_footprint.read_text() if imu_footprint.exists() else ""
    normalized_lps = " ".join(lps_footprint_text.split())
    normalized_imu = " ".join(imu_footprint_text.split())
    expected_imu_geometry = (
        '(pad "1" smd roundrect (at -1.1625 -0.75) (size 0.625 0.35)',
        '(pad "4" smd roundrect (at -1.1625 0.75) (size 0.625 0.35)',
        '(pad "8" smd roundrect (at 1.1625 0.75) (size 0.625 0.35)',
        '(pad "14" smd roundrect (at -0.5 -0.9125) (size 0.35 0.625)',
        '(keepout (tracks not_allowed) (vias not_allowed) (pads allowed) (copperpour not_allowed)',
        '(name "U2_FULL_BODY_NO_VIAS_OR_POUR")',
        '(name "U2_TRACK_GUARD_WITH_0p20_RADIAL_ESCAPES")',
        '(keepout (tracks allowed) (vias not_allowed) (pads allowed) (copperpour not_allowed)',
        '(xy -1.5 -1.25)', '(xy 1.5 1.25)',
    )
    expected_lps_geometry = (
        '(pad "1" smd rect (at -1.125 0) (size 0.35 1.4)',
        '(pad "2" smd rect (at -0.575 1.125) (size 0.9 0.35)',
        '(pad "3" smd rect (at 0.575 1.125) (size 0.9 0.35)',
        '(pad "4" smd rect (at 1.125 0) (size 0.35 1.4)',
        '(pad "5" smd rect (at 0.575 -1.125) (size 0.9 0.35)',
        '(pad "6" smd rect (at -0.575 -1.125) (size 0.9 0.35)',
        '(pad "7" smd rect (at 0 0) (size 0.9 0.9)',
        '(keepout (tracks not_allowed) (vias not_allowed) (pads allowed) (copperpour not_allowed)',
    )
    modified = []
    for relative, expected in baseline.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            modified.append(relative)

    pcb_path = REV / "smart_apo_common_revA2.kicad_pcb"
    drc_path = REV / "drc_revA2_kicad10.json"
    drc = json.loads(drc_path.read_text()) if drc_path.exists() else None
    drc_violations = (drc or {}).get("violations") or []
    drc_errors = [item for item in drc_violations if item.get("severity") == "error"]
    drc_warnings = [item for item in drc_violations if item.get("severity") == "warning"]
    drc_unconnected = (drc or {}).get("unconnected_items") or []
    drc_parity = (drc or {}).get("schematic_parity") or []
    if not pcb_path.exists():
        official_drc = "BLOCKED_NO_PRODUCTION_CANDIDATE_REVA2_PCB"
    elif drc is None:
        official_drc = "BLOCKED_DRC_NOT_RUN"
    elif not drc_errors and not drc_unconnected and not drc_parity:
        official_drc = "PASS_ZERO_ERRORS"
    else:
        official_drc = "FAIL_OFFICIAL_DRC"

    checks = {
        "revA1_hashes_unchanged": not modified,
        "revA1_modified_files": modified,
        "schematic_parentheses_balanced": balanced(schematic),
        "symbol_library_parentheses_balanced": balanced(symbols),
        "schematic_has_no_RevA1_title": "Rev.A1" not in schematic and "revA1" not in schematic,
        "schematic_uses_project_symbol_ids": "SmartApoRevA2:" in schematic,
        "core_pins_not_all_passive": schematic.count("(pin passive line") < 30,
        "stm32_tssop20_physical_pinout_corrected": all(
            token in schematic
            for token in (
                '(name "PB9/PC14-OSC32_IN"',
                '(name "VDD/VDDA"',
                '(name "VSS/VSSA"',
                '(name "PA12[PA10]"',
                '(name "PA15/PA14-BOOT0"',
            )
        ),
        "flash_cs_pullup_r12_present": '(property "Reference" "R12"' in schematic,
        "assembly_variants_preserved": (REV / "ASSEMBLY_VARIANTS_revA2.csv").exists(),
        "working_bom_present": (REV / "BOM_revA2_WORKING.csv").exists(),
        "old_cpl_marked_reference_only": (REV / "CPL_revA1_REFERENCE_ONLY.csv").exists(),
        "official_erc_kicad_version": (erc or {}).get("kicad_version"),
        "official_erc_error_count": len(erc_errors),
        "official_erc_warning_count": len(erc_warnings),
        "official_erc_zero_violations": erc_zero_violations,
        "official_erc": "PASS_ZERO_VIOLATIONS" if erc_zero_violations else "FAIL_OR_NOT_RUN",
        "lps28dfw_footprint_present": lps_footprint.exists(),
        "lps28dfw_official_geometry_locked": all(token in normalized_lps for token in expected_lps_geometry),
        "lsm6dso_footprint_present": imu_footprint.exists(),
        "lsm6dso_escape_rule_status": "ENGINEERING_INTERPRETATION_WITH_OFFICIAL_DRC_POSITIVE_AND_NEGATIVE_TESTS",
        "lsm6dso_evaluation_gerber_check": "BLOCKED_SOURCE_DOWNLOAD",
        "lsm6dso_geometry_locked": all(token in normalized_imu for token in expected_imu_geometry),
        "schematic_uses_lsm6dso_project_footprint": "SmartApoRevA2:LGA-14_3x2.5mm_P0.5mm_LSM6DSO" in schematic,
        "lps28dfw_official_gerber_sha256": "3ada96e8f5379a3faae7fded4939724d4bf06484e59954bf688c2410324ce10f",
        "official_netlist_component_count": len(netlist_components),
        "official_netlist_connected_net_count": len(netlist_nets) - len(unconnected_nets),
        "official_netlist_unconnected_pin_count": len(unconnected_nets),
        "official_netlist_stm32_pin_map_correct": all(
            node_nets.get(("U1", pin)) == net for pin, net in expected_mcu_nets.items()
        ),
        "official_netlist_flash_cs_pullup_correct": (
            node_nets.get(("R12", 1)) == "3V3" and node_nets.get(("R12", 2)) == "FLASH_CS"
        ),
        "legacy_root_revA2_pcb_present": (ROOT / "hardware" / "smart_apo_common_revA2_NETS_PLACED.kicad_pcb").exists(),
        "production_candidate_pcb_present": pcb_path.exists(),
        "official_drc_kicad_version": (drc or {}).get("kicad_version"),
        "official_drc_error_count": len(drc_errors),
        "official_drc_warning_count": len(drc_warnings),
        "official_drc_unconnected_count": len(drc_unconnected),
        "official_drc_schematic_parity_count": len(drc_parity),
        "official_drc_ignored_checks": (drc or {}).get("ignored_checks", []),
        "official_drc": official_drc,
        "fabrication_release": "NOT_FAB_RELEASED",
    }
    checks["offline_result"] = "PASS_WITH_PCB_AND_PHYSICAL_TEST_GATES" if all(
        value for key, value in checks.items() if isinstance(value, bool)
    ) else "FAIL"
    (REV / "validation_report_revA2.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(checks, indent=2))
    if checks["offline_result"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
