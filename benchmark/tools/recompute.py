#!/usr/bin/env python3
"""Recompute canonical reports without running an agent or modifying raw evidence."""
import argparse
import json
from pathlib import Path
from report import BenchmarkReport
from result_reader import ResultReader
from stream_metrics import StreamMetrics


class Recompute:
    def __init__(self, reader, report):
        self.reader = reader
        self.report = report

    def artifacts(self, root):
        canonical = json.loads((root / "canonical.json").read_text())
        experiments = []
        files = {}
        for config in canonical:
            records = self.reader.collect(root / config["folder"])
            experiments.append({**config, "sessions": records})
            files[root / config["folder"] / "summary.md"] = self.report.render(config["folder"], records)
        # One line per session keeps the correction reviewable; raw streams and result.json are immutable.
        lines = ['{"measurement_version": 2, "experiments": [']
        for i, experiment in enumerate(experiments):
            metadata = {key: value for key, value in experiment.items() if key != "sessions"}
            lines.append(json.dumps(metadata)[:-1] + ', "sessions": [')
            lines += [json.dumps(row, sort_keys=True) + ("," if j < len(experiment["sessions"]) - 1 else "")
                      for j, row in enumerate(experiment["sessions"])]
            lines.append("]}" + ("," if i < len(experiments) - 1 else ""))
        lines.append("]}")
        files[root / "corrected-results.json"] = "\n".join(lines) + "\n"
        return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent / "results"
    artifacts = Recompute(ResultReader(StreamMetrics()), BenchmarkReport()).artifacts(root)
    for path, content in artifacts.items():
        if args.check:
            if path.read_text() != content:
                raise ValueError(f"Derived evidence drift: {path}")
        else:
            path.write_text(content)
    print(f"{'Verified' if args.check else 'Regenerated'} {len(artifacts)} evidence artifacts; raw sessions unchanged.")


if __name__ == "__main__":
    main()
