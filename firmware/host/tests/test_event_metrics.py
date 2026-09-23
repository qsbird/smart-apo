"""Event scoring independent of filtering, calibration and physical data."""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'event_metrics.py'
spec = importlib.util.spec_from_file_location('apo_event_metrics', MODULE)
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)


class EventMetricsTests(unittest.TestCase):
    def test_one_alarm_cannot_claim_two_truth_events(self):
        m = metrics.event_metrics([1, 0, 1], [1, 1, 1], 3)
        self.assertEqual(m['matched_events'], 1)
        self.assertEqual(m['recall'], .5)
        self.assertEqual(m['precision'], 1)

    def test_duplicate_alarms_count_as_false_events(self):
        m = metrics.event_metrics([1, 1, 1], [1, 0, 1], 3)
        self.assertEqual(m['matched_events'], 1)
        self.assertEqual(m['precision'], .5)
        self.assertEqual(m['false_events_per_hour'], 1200)

    def test_adjacent_intervals_do_not_overlap(self):
        m = metrics.event_metrics([1, 0], [0, 1], 2)
        self.assertEqual(m['matched_events'], 0)
        self.assertEqual(m['event_f1'], 0)

    def test_invalid_duration_and_mismatched_streams_rejected(self):
        for duration in [0, -1, float('nan'), float('inf')]:
            with self.assertRaises(ValueError):metrics.event_metrics([1], [1], duration)
        with self.assertRaises(ValueError):metrics.event_metrics([1], [1, 0], 1)

    def test_exhaustive_short_streams_match_maximum_one_to_one_assignment(self):
        def optimum(truth, found):
            def visit(i, used):
                if i == len(truth):return 0
                a, b = truth[i]
                choices = [visit(i+1, used)]
                for j, (c, d) in enumerate(found):
                    if j not in used and max(a, c) < min(b, d):
                        choices.append(1 + visit(i+1, used | {j}))
                return max(choices)
            return visit(0, set())
        for a in range(64):
            y = [bool(a & (1 << i)) for i in range(6)]
            for b in range(64):
                pred = [bool(b & (1 << i)) for i in range(6)]
                expected = optimum(metrics.event_ranges(y), metrics.event_ranges(pred))
                got = metrics.event_metrics(y, pred, 6)
                self.assertEqual(got['matched_events'], expected, (a,b))
                self.assertEqual(got['false_events'], got['detected_events']-expected)
                self.assertEqual(got['missed_events'], got['truth_events']-expected)


if __name__ == '__main__':unittest.main()
