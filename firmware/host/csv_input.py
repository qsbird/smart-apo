"""Validate numeric voyage columns before any interpolation or filtering."""
import csv
import math
from pathlib import Path


def load_numeric_csv(path: Path, required: tuple[str, ...]) -> dict[str, list[float]]:
    with path.open(newline='') as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise ValueError(f'{path}: duplicate CSV column names')
        missing = set(required) - set(headers)
        if missing:
            raise ValueError(f'{path}: missing columns {sorted(missing)}')
        columns = {name: [] for name in required}
        for row in reader:
            for name in required:
                try:
                    value = float(row[name])
                except (ValueError, TypeError) as exc:
                    raise ValueError(f'{path}: line {reader.line_num}, {name}: expected a number') from exc
                if not math.isfinite(value):
                    raise ValueError(f'{path}: line {reader.line_num}, {name}: expected a finite number')
                columns[name].append(value)
            times = columns['timestamp_us']
            if len(times) > 1 and times[-1] <= times[-2]:
                raise ValueError(f'{path}: line {reader.line_num}: timestamp_us must be strictly increasing')
    if len(columns['timestamp_us']) < 2:
        raise ValueError(f'{path}: at least two samples are required')
    return columns
