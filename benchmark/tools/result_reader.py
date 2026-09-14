"""Read historical evidence independently of legacy derived result.json fields."""
import hashlib
import json


class ResultReader:
    def __init__(self, stream_metrics):
        self.stream_metrics = stream_metrics

    def read_session(self, directory):
        stream_path = directory / "stream.ndjson"
        raw = stream_path.read_bytes()
        result = self.stream_metrics.parse(raw.decode().splitlines())
        stored = json.loads((directory / "result.json").read_text())
        for key in ["usage", "num_turns", "duration_ms", "total_cost_usd"]:
            if result[key] != stored[key]:
                raise ValueError(f"Stored {key} differs from stream in {directory}")
        usage = result["usage"]
        observed = result["observations"]
        return {
            "output_tokens": usage["output_tokens"],
            "input_tokens": usage["input_tokens"],
            "cache_creation_input_tokens": usage["cache_creation_input_tokens"],
            "cache_read_input_tokens": usage["cache_read_input_tokens"],
            "recorded_cost_usd": result["total_cost_usd"],
            "duration_ms": result["duration_ms"],
            "claude_num_turns": result["num_turns"],
            **{key: value for key, value in observed.items() if key != "version"},
            "stream_sha256": hashlib.sha256(raw).hexdigest(),
        }

    def collect(self, root):
        records = []
        runs = sorted(root.glob("run-*"))
        if not runs:
            raise ValueError(f"No runs in {root}")
        for run in runs:
            for phase, relative, variant in [
                ("warmup", "a-mcp/warmup", "a-mcp"),
                ("generation", "a-mcp/gen", "a-mcp"),
                ("baseline", "b-baseline", "b-baseline"),
            ]:
                judge = json.loads((run / variant / "judge.json").read_text())
                records.append({
                    "run": run.name,
                    "phase": phase,
                    "verdict": judge["verdict"] if phase != "warmup" else None,
                    **self.read_session(run / relative),
                })
        return records

