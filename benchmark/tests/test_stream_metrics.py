"""Regression coverage for the incorrect turn and token interpretations."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from stream_metrics import StreamMetrics


class StreamMetricsTests(unittest.TestCase):
    def setUp(self):
        self.parser = StreamMetrics()

    def message(self, message_id, content, event_id, output_tokens=72):
        return {"type": "assistant", "uuid": event_id, "message": {
            "id": message_id, "content": content, "usage": {"output_tokens": output_tokens}}}

    def result(self, turns=3):
        return {"type": "result", "num_turns": turns, "usage": {"output_tokens": 500}}

    def parse(self, events):
        return self.parser.parse(json.dumps(event) for event in events)

    def test_many_writes_share_one_response_and_do_not_become_visible_tokens(self):
        writes = [{"type": "tool_use", "id": f"write-{i}", "input": {"content": "class X {}"}}
                  for i in range(71)]
        events = [self.message("batch", [write], str(i)) for i, write in enumerate(writes)]
        parsed = self.parse(events + [self.result(72)])
        self.assertEqual(1, parsed["observations"]["assistant_messages"])
        self.assertEqual(71, parsed["observations"]["tool_calls"])
        self.assertEqual(0, parsed["observations"]["text_characters"])
        self.assertEqual(72, parsed["num_turns"])
        self.assertEqual(500, parsed["usage"]["output_tokens"])
        self.assertNotIn("thinking_residual_unmeasured_tokens", parsed["observations"])

    def test_separate_responses_and_content_blocks_are_counted_independently(self):
        events = [self.message("read", [{"type": "text", "text": "Read"}], "text"),
                  self.message("read", [{"type": "tool_use", "id": "read-1", "input": {"path": "a"}}], "tool"),
                  self.message("done", [{"type": "text", "text": "DONE"}], "done")]
        observed = self.parse(events + [self.result()])["observations"]
        self.assertEqual(2, observed["assistant_messages"])
        self.assertEqual(1, observed["tool_calls"])
        self.assertEqual(8, observed["text_characters"])
        self.assertEqual(len(json.dumps({"path": "a"}, sort_keys=True)), observed["tool_input_characters"])

    def test_repeated_events_and_tool_ids_do_not_inflate_observations(self):
        event = self.message("a", [{"type": "text", "text": "Once"},
                                  {"type": "tool_use", "id": "t", "input": {}}], "same")
        observed = self.parse([event, event, self.result()])["observations"]
        self.assertEqual(4, observed["text_characters"])
        self.assertEqual(1, observed["tool_calls"])

    def test_missing_result_fails_instead_of_becoming_a_zero_cost_run(self):
        with self.assertRaisesRegex(ValueError, "complete session"):
            self.parse([self.message("a", [], "a")])

    def test_invalid_json_and_multiple_results_fail(self):
        with self.assertRaises(json.JSONDecodeError):
            self.parser.parse(["broken"])
        with self.assertRaisesRegex(ValueError, "Multiple result"):
            self.parse([self.result(), self.result()])


if __name__ == "__main__":
    unittest.main()
