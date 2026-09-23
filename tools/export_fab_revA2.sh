#!/usr/bin/env bash
# Export Gerber / drill / CPL only after official KiCad DRC has zero errors
# and zero unconnected items. Never writes FAB_RELEASED on failure.
set -euo pipefail

CHECK_ONLY=0
if [[ $# -gt 1 ]]; then
  echo "usage: $0 [--check-only]" >&2
  exit 64
fi
case "${1:-}" in
  "") ;;
  --check-only) CHECK_ONLY=1 ;;
  -h|--help)
    echo "usage: $0 [--check-only]"
    echo "--check-only runs official ERC/DRC without creating or changing fabrication files."
    exit 0 ;;
  *) echo "unknown option: $1" >&2; exit 64 ;;
esac

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KICAD_CLI="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
if [[ ! -x "$KICAD_CLI" ]]; then
  echo "kicad-cli not found: $KICAD_CLI" >&2
  exit 1
fi
REV="$ROOT/hardware/revA2"
PCB="$REV/smart_apo_common_revA2.kicad_pcb"
DRC_JSON="$REV/drc_revA2_kicad10.json"
OUT="$REV/fab_export"

if [[ ! -f "$PCB" ]]; then
  echo "missing $PCB" >&2
  exit 1
fi

"$KICAD_CLI" sch erc --format json --severity-all \
  -o "$REV/erc_revA2_kicad10.json" "$REV/smart_apo_common_revA2.kicad_sch"
python3 - "$REV/erc_revA2_kicad10.json" <<'PYERC'
import json, sys
report = json.load(open(sys.argv[1]))
violations = [v for sheet in report["sheets"] for v in sheet["violations"]]
if violations:
    print(f"REFUSING export: official ERC has {len(violations)} violations")
    sys.exit(2)
PYERC

"$KICAD_CLI" pcb drc --format json --severity-all --units mm --refill-zones --schematic-parity \
  -o "$DRC_JSON" "$PCB"

python3 - "$DRC_JSON" <<'PY'
import json, sys
from pathlib import Path
report = json.loads(Path(sys.argv[1]).read_text())
errors = [v for v in (report.get("violations") or []) if v.get("severity") == "error"]
unconnected = report.get("unconnected_items") or []
print(f"official DRC errors={len(errors)} unconnected={len(unconnected)} warnings="
      f"{sum(1 for v in (report.get('violations') or []) if v.get('severity')=='warning')}")
parity = report.get("schematic_parity") or []
print(f"schematic parity issues={len(parity)}")
if errors or unconnected or parity:
    print("REFUSING Gerber/drill/CPL export: NOT_FAB_RELEASED")
    sys.exit(2)
PY

if [[ "$CHECK_ONLY" -eq 1 ]]; then
  echo "Official electrical checks passed; check-only mode left fabrication files untouched."
  echo "Warnings and all remaining release gates still require review: NOT_FAB_RELEASED"
  exit 0
fi

mkdir -p "$OUT"
rm -rf "$OUT"/*
"$KICAD_CLI" pcb export gerbers --output "$OUT" --layers \
  "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts" \
  "$PCB"
"$KICAD_CLI" pcb export drill --output "$OUT" --format excellon --excellon-zeros-format decimal \
  --generate-map --map-format gerber "$PCB"
"$KICAD_CLI" pcb export pos --output "$OUT/CPL_revA2_FRONT.csv" --side front --format csv --units mm --use-drill-origin "$PCB"
"$KICAD_CLI" pcb export pos --output "$OUT/CPL_revA2_BACK.csv" --side back --format csv --units mm --use-drill-origin "$PCB"
"$KICAD_CLI" sch export bom --output "$OUT/BOM_revA2_FROM_SCH.csv" \
  --fields "Reference,Value,Footprint,QUANTITY,DNP,Population" \
  --labels "Refs,Value,Footprint,Qty,DNP,Population" "$REV/smart_apo_common_revA2.kicad_sch"
echo "exported candidate fab files to $OUT — still requires independent Gerber review before FAB_RELEASED"
