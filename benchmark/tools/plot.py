#!/usr/bin/env python3
"""Render bounded comparisons from corrected evidence, not legacy metric fields."""
import json
import statistics
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class BenchmarkCharts:
    def __init__(self, experiments, output):
        self.experiments = {item["folder"]: item for item in experiments}
        self.output = output

    def rows(self, folder, phase):
        return [row for row in self.experiments[folder]["sessions"] if row["phase"] == phase]

    def mean(self, folder, phase, metric):
        return statistics.mean(row[metric] for row in self.rows(folder, phase))

    def save(self, figure, filename):
        figure.text(.5, .01, "Recorded 2026-04-26 · n=5 per cell · failed judgments included · measurement schema 2",
                    ha="center", fontsize=9, color="#555555")
        figure.tight_layout(rect=(0, .04, 1, .94))
        figure.savefig(self.output / filename, dpi=160, metadata={"Software": "MetaEngine benchmark measurement schema 2"})
        plt.close(figure)

    def absolute(self, folders, labels, metrics, title, filename):
        figure, axes = plt.subplots(1, len(metrics), figsize=(5 * len(metrics), 4.8), squeeze=False)
        for axis, (metric, label) in zip(axes[0], metrics):
            for index, phase in enumerate(["baseline", "generation"]):
                positions = [i + (index - .5) * .36 for i in range(len(folders))]
                values = [self.mean(folder, phase, metric) for folder in folders]
                axis.bar(positions, values, width=.36, label=phase,
                         color=["#777777", "#216E9B"][index])
            axis.set_xticks(range(len(folders)), labels, rotation=20, ha="right")
            axis.set_title(label)
            axis.grid(axis="y", alpha=.2)
            axis.set_axisbelow(True)
        axes[0][0].legend()
        figure.suptitle(title)
        self.save(figure, filename)

    def relative(self, folders, labels, title, filename):
        metrics = [("output_tokens", "Output tokens"), ("assistant_messages", "Assistant messages"),
                   ("tool_calls", "Tool calls"), ("duration_ms", "Duration")]
        figure, axes = plt.subplots(1, len(metrics), figsize=(17, 5))
        for axis, (metric, label) in zip(axes, metrics):
            changes = [100 * (self.mean(folder, "generation", metric) /
                              self.mean(folder, "baseline", metric) - 1) for folder in folders]
            axis.bar(range(len(folders)), changes,
                     color=["#216E9B" if value <= 0 else "#AF4B38" for value in changes])
            axis.set_xticks(range(len(folders)), labels, rotation=30, ha="right")
            axis.axhline(0, color="black", linewidth=.6)
            axis.set_title(label)
            axis.set_ylabel("Change from same-cell baseline (%)")
        figure.suptitle(title + " (negative = less; positive = more)")
        self.save(figure, filename)

    def cache_scatter(self):
        figure, axis = plt.subplots(figsize=(9, 5.5))
        for model, color in [("claude-opus-4-7", "#216E9B"), ("claude-sonnet-4-6", "#AF4B38")]:
            rows = [row for experiment in self.experiments.values()
                    if experiment["model"] == model and experiment["language"] == "typescript"
                    for row in experiment["sessions"] if row["phase"] == "baseline"]
            axis.scatter([row["assistant_messages"] for row in rows],
                         [row["cache_read_input_tokens"] for row in rows], label=model, alpha=.7, color=color)
        axis.set_xlabel("Observed assistant messages per baseline session")
        axis.set_ylabel("Recorded cache-read tokens")
        axis.set_yscale("log")
        axis.legend()
        axis.grid(alpha=.2)
        figure.suptitle("Cache reads alongside message batching; no cache-policy diagnosis")
        self.save(figure, "baseline-cache-per-run.png")

    def render(self):
        self.output.mkdir(exist_ok=True)
        folders = ["ts-invocation-inline", "ts-invocation-script", "ts-inline-sonnet", "ts-script-sonnet"]
        labels = ["Opus inline", "Opus script", "Sonnet inline", "Sonnet script"]
        self.absolute(folders, labels,
                      [("output_tokens", "Output tokens"), ("assistant_messages", "Assistant messages"),
                       ("tool_calls", "Tool calls")],
                      "Each assisted cell beside its own baseline", "headline-absolute.png")
        self.relative(folders, labels, "TypeScript assisted generation", "cross-model-reductions.png")
        self.relative(["ts-monolith-opus-inline", "ts-monolith-opus-script",
                       "ts-monolith-sonnet-inline", "ts-monolith-sonnet-script"], labels,
                      "68-entity modular-monolith generation", "cross-shape-reductions.png")
        self.absolute(["ts-multilang", "java-multilang", "python-multilang"], ["TypeScript", "Java", "Python"],
                      [("assistant_messages", "Assistant messages"), ("tool_calls", "Tool calls"),
                       ("output_tokens", "Output tokens")],
                      "Opus multilang cells; batching varies by run", "multilang-topology.png")
        self.absolute(folders, labels, [("text_characters", "Text characters"),
                                       ("tool_input_characters", "Serialized tool-input characters")],
                      "Observable content sizes; these are not token components", "output-decomposition.png")
        self.cache_scatter()


def main():
    root = Path(__file__).resolve().parent.parent
    measurements = json.loads((root / "results/corrected-results.json").read_text())
    if measurements["measurement_version"] != 2:
        raise ValueError("Unsupported measurement schema")
    BenchmarkCharts(measurements["experiments"], root / "figures").render()


if __name__ == "__main__":
    main()
