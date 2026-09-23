"""One-to-one overlap scoring for disjoint event intervals; no signal processing."""
import math


def event_ranges(values):
    ranges = []
    start = None
    for i, value in enumerate(values):
        if value and start is None:
            start = i
        elif not value and start is not None:
            ranges.append((start, i))
            start = None
    if start is not None:
        ranges.append((start, len(values)))
    return ranges


def event_metrics(y, pred, duration_s):
    if not math.isfinite(duration_s) or duration_s <= 0:
        raise ValueError('event metrics require a finite positive duration')
    if len(y) != len(pred):
        raise ValueError('truth and prediction must share the same sample grid')
    truth, found = event_ranges(y), event_ranges(pred)
    i = j = matched = 0
    # Both lists contain sorted, non-overlapping half-open intervals. Matching
    # the earliest overlapping pair gives maximum cardinality without reuse.
    while i < len(truth) and j < len(found):
        a, b = truth[i]
        c, d = found[j]
        if b <= c:
            i += 1
        elif d <= a:
            j += 1
        else:
            matched += 1
            i += 1
            j += 1
    missed = len(truth) - matched
    false = len(found) - matched
    precision = matched / len(found) if found else 0.0
    recall = matched / len(truth) if truth else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {'event_f1': f1, 'precision': precision, 'recall': recall,
            'false_events_per_hour': false * 3600.0 / duration_s,
            'truth_events': len(truth), 'detected_events': len(found),
            'matched_events': matched, 'missed_events': missed, 'false_events': false,
            'matching_method': 'one_to_one_overlap_v2'}
