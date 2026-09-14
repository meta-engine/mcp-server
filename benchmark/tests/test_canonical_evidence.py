"""Check the correction against historical traces, without modifying them."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from recompute import Recompute
from report import BenchmarkReport
from result_reader import ResultReader
from stream_metrics import StreamMetrics


class CanonicalEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1] / "results"
        self.reader = ResultReader(StreamMetrics())

    def test_sonnet_batched_writes_and_opus_sequential_writes_remain_distinct(self):
        sonnet = self.reader.read_session(self.root / "ts-inline-sonnet/run-001/b-baseline")
        self.assertEqual((73, 3, 72), tuple(sonnet[key] for key in
                         ["claude_num_turns", "assistant_messages", "tool_calls"]))
        opus = self.reader.read_session(self.root / "ts-multilang/run-003/b-baseline")
        self.assertEqual((73, 73, 72), tuple(opus[key] for key in
                         ["claude_num_turns", "assistant_messages", "tool_calls"]))

    def test_all_225_sessions_and_reports_recompute_exactly(self):
        expected = Recompute(self.reader, BenchmarkReport()).artifacts(self.root)
        for path, content in expected.items():
            with self.subTest(path=path.name):
                self.assertEqual(content, path.read_text())
        corrected = json.loads(expected[self.root / "corrected-results.json"])
        self.assertEqual(15, len(corrected["experiments"]))
        self.assertEqual(225, sum(len(e["sessions"]) for e in corrected["experiments"]))

    def test_failed_judgments_are_included_in_reports(self):
        records = self.reader.collect(self.root / "ts-invocation-script")
        report = BenchmarkReport().render("script", records)
        self.assertIn("4/5", report)
        self.assertIn("4,691 [3,247–5,742]", report)
        self.assertIn("failed judgments", report)


if __name__ == "__main__":
    unittest.main()
