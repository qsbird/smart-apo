#!/usr/bin/env python3
"""Decode Smart Apo UART recovery frames to CSV.

Frame: A5 5A | version | payload_len | payload | crc16_ccitt(version..payload) BE
Payload is packed little-endian smart_apo_sample_t from firmware/mcu.

Default CSV keeps raw counts. --autotune awa|uw writes only the columns
autotune.py requires, using the same candidate scales as sensors.h.
Autotune rejects missing channels, bad sample CRC and nonmonotonic timestamps.
UW export requires measured slope AND zero offset; raw CSV preserves counts/flags.
"""

from __future__ import annotations

import argparse
import math
import struct
import sys
from pathlib import Path

SYNC = b"\xA5\x5A"
SAMPLE = struct.Struct("<IHhhhhhhiihHHH")
VOYAGE_HEADER = struct.Struct("<IIBBBBI")
DATALOG_MAGIC = 0x41504F32
RAW_HEADER = (
    "timestamp_us,sequence,ax_raw,ay_raw,az_raw,gx_raw,gy_raw,gz_raw,"
    "pressure_raw,tension_raw,temperature,battery_mv,flags,crc16"
)
AUTOTUNE_AWA = "timestamp_us,ax,ay,az,gx,gy,gz,pressure"
AUTOTUNE_UW = AUTOTUNE_AWA + ",tension_gf"

# Match firmware/mcu/include/sensors.h / DS13317 FS_MODE.
ACCEL_FS_G = 4.0
GYRO_FS_DPS = 500.0
PRESS_LSB_PER_HPA_AWA = 4096.0  # mode 1, 1260 hPa
PRESS_LSB_PER_HPA_UW = 2048.0   # mode 2, 4060 hPa; required for ~15 m
# ST lsm6dso_reg.c: fs4 = 0.122 mg/LSB; fs500 = 17.50 mdps/LSB.
ACCEL_LSB = 0.000122
GYRO_LSB = 0.01750
SAMPLE_FLAG_IMU_OK = 1 << 1
SAMPLE_FLAG_PRESS_OK = 1 << 2
SAMPLE_FLAG_STRAIN_OK = 1 << 3


def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def decode_frames(blob: bytes) -> list[tuple[int, bytes]]:
    frames = []
    i = 0
    while i + 4 < len(blob):
        if blob[i:i+2] != SYNC:
            i += 1
            continue
        version, size = blob[i+2:i+4]
        expected_size = {1: SAMPLE.size, 2: VOYAGE_HEADER.size}.get(version)
        end = i + 4 + size + 2
        if size != expected_size or end > len(blob):
            i += 1
            continue
        if int.from_bytes(blob[end-2:end], 'big') != crc16_ccitt(blob[i+2:end-2]):
            i += 1
            continue
        frames.append((version, blob[i+4:end-2]))
        i = end
    return frames


def decode_bytes(blob: bytes) -> list[tuple]:
    rows = []
    for version, payload in decode_frames(blob):
        if version != 1:
            continue
        row = SAMPLE.unpack(payload)
        if not rows or rows[-1] != row:
            rows.append(row)
    return rows


def validate_capture_header(blob: bytes, underwater: bool, *, allow_headerless=False):
    frames = decode_frames(blob)
    headers = [VOYAGE_HEADER.unpack(payload) for version, payload in frames if version == 2]
    if not headers:
        if allow_headerless:
            return None  # Explicit legacy declaration, not verified metadata.
        raise ValueError('missing voyage header; legacy capture needs explicit --allow-headerless')
    if frames[0][0] != 2:
        raise ValueError('voyage header must precede all sample frames')
    header = headers[0]
    if any(other != header for other in headers[1:]):
        raise ValueError('conflicting voyage headers; do not combine captures')
    magic, _hash, variant, imu_hz, press_hz, fs_mode, _start = header
    if magic != DATALOG_MAGIC or variant not in (0, 1):
        raise ValueError('unsupported voyage header')
    if (imu_hz, press_hz, fs_mode) != ((104, 50, 0) if variant == 0 else (208, 100, 1)):
        raise ValueError('voyage sensor configuration does not match supported variant')
    if variant != int(underwater):
        raise ValueError('requested variant conflicts with voyage header')
    return header


def format_raw(row: tuple) -> str:
    return ",".join(str(v) for v in row)


def validate_autotune_row(row: tuple, underwater: bool) -> None:
    required = SAMPLE_FLAG_IMU_OK | SAMPLE_FLAG_PRESS_OK
    if underwater:
        required |= SAMPLE_FLAG_STRAIN_OK
    flags = row[-2]
    if flags & required != required:
        raise ValueError("missing valid sensor channels (flags); use raw export until explicit resampling is implemented")
    if not underwater and flags & SAMPLE_FLAG_STRAIN_OK:
        raise ValueError("strain-valid sample conflicts with requested AWA variant")
    if crc16_ccitt(SAMPLE.pack(*row)[:-2]) != row[-1]:
        raise ValueError("sample CRC mismatch; raw export remains available for diagnosis")


def format_autotune(row: tuple, underwater: bool, tension_lsb_per_gf: float,
                    tension_zero_counts: float | None = None, *,
                    timestamp_us: int | None = None) -> str:
    validate_autotune_row(row, underwater)
    if underwater and (not math.isfinite(tension_lsb_per_gf) or tension_lsb_per_gf == 0
                       or tension_zero_counts is None or not math.isfinite(tension_zero_counts)):
        raise ValueError("UW needs finite nonzero --tension-lsb-per-gf and finite --tension-zero-counts from calibration")
    ts, _seq, ax, ay, az, gx, gy, gz, press, tension, _t, _bat, _flags, _crc = row
    fields = [
        f"{ts if timestamp_us is None else timestamp_us}.0",
        f"{ax * ACCEL_LSB:.9g}",
        f"{ay * ACCEL_LSB:.9g}",
        f"{az * ACCEL_LSB:.9g}",
        f"{gx * GYRO_LSB:.9g}",
        f"{gy * GYRO_LSB:.9g}",
        f"{gz * GYRO_LSB:.9g}",
        f"{press / (PRESS_LSB_PER_HPA_UW if underwater else PRESS_LSB_PER_HPA_AWA):.9g}",
    ]
    if underwater:
        gf = (tension - tension_zero_counts) / tension_lsb_per_gf
        fields.append(f"{gf:.9g}")
    return ",".join(fields)


def format_autotune_rows(rows: list[tuple], underwater: bool, slope: float,
                         zero: float | None = None, *, unwrap_timestamps: bool = False,
                         max_sample_gap_us: int | None = None) -> list[str]:
    if not rows:
        raise ValueError("no valid UART frames")
    if unwrap_timestamps:
        if (type(max_sample_gap_us) is not int
                or not 0 < max_sample_gap_us < (1 << 31)):
            raise ValueError("timestamp unwrap requires explicit max sample gap in 1..2147483647 us")
    elif max_sample_gap_us is not None:
        raise ValueError("max sample gap requires explicit timestamp unwrap")
    if not unwrap_timestamps and any(right[0] <= left[0] for left, right in zip(rows, rows[1:])):
        raise ValueError("timestamps must strictly increase; wrap/reset needs explicit reconstruction")
    if any(right[1] != ((left[1] + 1) & 0xFFFF) for left, right in zip(rows, rows[1:])):
        raise ValueError("sample sequence gap/reorder; dropped UART frames need recovery before autotune")
    timestamps = [rows[0][0]]
    for left, right in zip(rows, rows[1:]):
        delta = (right[0] - left[0]) & 0xFFFFFFFF
        if unwrap_timestamps and not 0 < delta <= max_sample_gap_us:
            raise ValueError("ambiguous timestamp delta: duplicate/backward/reset or declared max sample gap exceeded")
        timestamps.append(timestamps[-1] + delta)
    # Validate CRC on the original uint32 payload; never rewrite the record itself.
    return [format_autotune(row, underwater, slope, zero, timestamp_us=ts)
            for row, ts in zip(rows, timestamps)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binfile")
    parser.add_argument("-o", "--output", help="CSV path; default stdout")
    parser.add_argument(
        "--autotune",
        choices=("awa", "uw"),
        help="write only autotune.py columns (awa or underwater)",
    )
    parser.add_argument(
        "--tension-lsb-per-gf",
        type=float,
        default=0.0,
        help="signed NAU7802 counts per gram-force from beam calibration; nonzero required for UW",
    )
    parser.add_argument("--tension-zero-counts", type=float, default=None,
                        help="measured unloaded bridge offset; explicitly required for UW")
    parser.add_argument("--unwrap-timestamps", action="store_true",
                        help="declare one uninterrupted boot with bounded adjacent intervals; expand uint32 time for autotune")
    parser.add_argument("--max-sample-gap-us", type=int,
                        help="required with --unwrap-timestamps: known maximum adjacent interval, 1..2147483647 us")
    parser.add_argument("--allow-headerless", action="store_true",
                        help="explicit legacy variant declaration when no voyage header exists; does not verify configuration")
    args = parser.parse_args()
    if args.allow_headerless and not args.autotune:
        parser.error("--allow-headerless applies only to --autotune")
    if not args.autotune and (args.unwrap_timestamps or args.max_sample_gap_us is not None):
        parser.error("timestamp reconstruction requires --autotune; raw export preserves wire timestamps")
    blob = Path(args.binfile).read_bytes()
    rows = decode_bytes(blob)
    if args.autotune:
        header = AUTOTUNE_UW if args.autotune == "uw" else AUTOTUNE_AWA
        try:
            validate_capture_header(blob, args.autotune == "uw", allow_headerless=args.allow_headerless)
            body = format_autotune_rows(rows, args.autotune == "uw",
                                        args.tension_lsb_per_gf, args.tension_zero_counts,
                                        unwrap_timestamps=args.unwrap_timestamps,
                                        max_sample_gap_us=args.max_sample_gap_us)
        except ValueError as exc:
            print(f"autotune export refused: {exc}", file=sys.stderr)
            return 2  # output path is untouched on validation failure
    else:
        header = RAW_HEADER
        body = [format_raw(r) for r in rows]
    text = "\n".join([header, *body]) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        sys.stdout.write(text)
    print(f"decoded {len(rows)} samples", file=sys.stderr)
    return 0 if rows else 2


if __name__ == "__main__":
    raise SystemExit(main())
