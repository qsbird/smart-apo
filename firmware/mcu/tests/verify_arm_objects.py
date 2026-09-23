"""Inspect genuine ELF ARM object headers and unresolved cross-object symbols.
Does not link, and does not claim final addresses, startup or hardware success.
"""
import hashlib
import json
import pathlib
import struct
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[1]
nm = sys.argv[1] if len(sys.argv) > 1 else "llvm-nm"
results = []
for variant in (0, 1):
    objects = sorted((root / f"build-arm/variant{variant}").glob("*/*.o"))
    assert len(objects) == 10, (variant, len(objects))
    defined, undefined = set(), set()
    entries = []
    for obj in objects:
        data = obj.read_bytes()
        assert data[:6] == b"\x7fELF\x01\x01", obj
        e_type, machine = struct.unpack_from("<HH", data, 16)
        assert (e_type, machine) == (1, 40), (obj, e_type, machine)
        output = subprocess.check_output([nm, "--format=posix", str(obj)], text=True)
        for line in output.splitlines():
            fields = line.split()
            if len(fields) >= 2:
                (undefined if fields[1] == "U" else defined).add(fields[0])
        entries.append({"file": str(obj.relative_to(root)), "sha256": hashlib.sha256(data).hexdigest(),
                        "format": "ELF32 little-endian", "type": "REL", "machine": "ARM"})
    unresolved = sorted(undefined - defined)
    expected = {"_ebss", "_edata", "_estack", "_sbss", "_sdata", "_sidata",
                "__aeabi_uidiv", "__aeabi_lmul", "__aeabi_uldivmod"}
    assert set(unresolved) == expected, unresolved
    results.append({"variant": variant, "objects": entries,
                    "unresolved_after_cross_object_matching": unresolved})
print(json.dumps({"status": "ARM_OBJECTS_ONLY_NOT_LINKED", "results": results}, indent=2))
