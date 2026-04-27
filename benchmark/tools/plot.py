#!/usr/bin/env python3
"""Generate canonical charts from final/results/ data.

Reads result.json files in each canonical result folder, computes per-folder
means across run-NNN, produces a small set of figures saved to final/figures/.
Regenerable — run after promoting a new experiment to final/results/.

Run via the included venv:
  ./tools/setup-charts.sh                    # one-time
  ./.venv/bin/python ./tools/plot.py         # any time data changes
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

# Canonical experiments. (folder, friendly_label, model, arm, language)
EXPERIMENTS = [
    ("ts-multilang",             "Opus / TS",          "Opus",   "inline",  "TypeScript"),
    ("java-multilang",           "Opus / Java",        "Opus",   "inline",  "Java"),
    ("python-multilang",         "Opus / Python",      "Opus",   "inline",  "Python"),
    ("ts-invocation-inline",     "Opus / TS inline",   "Opus",   "inline",  "TypeScript"),
    ("ts-invocation-script",     "Opus / TS script",   "Opus",   "script",  "TypeScript"),
    ("ts-invocation-heredoc",    "Opus / TS heredoc",  "Opus",   "heredoc", "TypeScript"),
    ("java-invocation-inline",   "Opus / Java inline", "Opus",   "inline",  "Java"),
    ("java-invocation-script",   "Opus / Java script", "Opus",   "script",  "Java"),
    ("python-invocation-script", "Opus / Py script",   "Opus",   "script",  "Python"),
    ("ts-inline-sonnet",         "Sonnet / TS inline", "Sonnet", "inline",  "TypeScript"),
    ("ts-script-sonnet",         "Sonnet / TS script", "Sonnet", "script",  "TypeScript"),
    # Modular-monolith spec (added 2026-04-26)
    ("ts-monolith-opus-inline",   "Opus / TS monolith inline",   "Opus",   "inline", "TypeScript"),
    ("ts-monolith-opus-script",   "Opus / TS monolith script",   "Opus",   "script", "TypeScript"),
    ("ts-monolith-sonnet-inline", "Sonnet / TS monolith inline", "Sonnet", "inline", "TypeScript"),
    ("ts-monolith-sonnet-script", "Sonnet / TS monolith script", "Sonnet", "script", "TypeScript"),
]


def session_metrics(result_path: Path) -> dict:
    if not result_path.exists():
        return {}
    d = json.loads(result_path.read_text())
    u = d.get("usage") or {}
    m = d.get("measurement") or {}
    return {
        "output":     int(u.get("output_tokens", 0) or 0),
        "cache_read": int(u.get("cache_read_input_tokens", 0) or 0),
        "cost":       float(d.get("total_cost_usd", 0) or 0),
        "turns":      int(d.get("num_turns", 0) or 0),
        "duration_s": (int(d.get("duration_ms", 0) or 0)) / 1000.0,
        "visible":    int(m.get("measured_visible_output_tokens", 0) or 0),
        "tool_input": int(m.get("measured_tool_input_tokens_estimated", 0) or 0),
        "thinking":   int(m.get("thinking_residual_unmeasured_tokens", 0) or 0),
    }


def folder_means(folder: Path) -> dict:
    runs = sorted(folder.glob("run-*"))
    if not runs:
        return {}
    a_warmup, a_gen, b_baseline = [], [], []
    for r in runs:
        w = session_metrics(r / "a-mcp" / "warmup" / "result.json")
        g = session_metrics(r / "a-mcp" / "gen" / "result.json")
        b = session_metrics(r / "b-baseline" / "result.json")
        if w: a_warmup.append(w)
        if g: a_gen.append(g)
        if b: b_baseline.append(b)

    def mean(xs, k):
        return (sum(x[k] for x in xs) / len(xs)) if xs else 0

    keys = ["output", "cache_read", "cost", "turns", "duration_s",
            "visible", "tool_input", "thinking"]
    return {
        "warmup":   {k: mean(a_warmup, k)   for k in keys},
        "gen":      {k: mean(a_gen, k)      for k in keys},
        "baseline": {k: mean(b_baseline, k) for k in keys},
        "n_runs":   len(runs),
    }


def reduction_pct(a: float, b: float) -> float:
    if not b:
        return 0.0
    return (1 - a / b) * 100


# ─── Charts ────────────────────────────────────────────────────────────────────

def chart_cross_model_reductions(data, out: Path):
    """Reduction-% comparison across model × arm for TypeScript."""
    targets = [
        ("ts-invocation-inline", "Opus inline"),
        ("ts-invocation-script", "Opus script"),
        ("ts-inline-sonnet",     "Sonnet inline"),
        ("ts-script-sonnet",     "Sonnet script"),
    ]
    # cache_read is intentionally NOT here — its Sonnet anomaly stretches the y-axis
    # too far and lives in its own chart (baseline-cache-per-run.png).
    metrics       = ["output",   "cost",  "turns",  "duration_s"]
    metric_labels = ["Output\ntokens", "Cost", "Turns", "Wall-clock"]

    fig, ax = plt.subplots(figsize=(11, 5.8))
    width = 0.19
    x = np.arange(len(metrics))
    colors = ["#2E86AB", "#5DA9C9", "#C73E1D", "#E08566"]

    for i, (folder, label) in enumerate(targets):
        d = data.get(folder, {})
        if not d:
            continue
        reductions = [reduction_pct(d["gen"][m], d["baseline"][m]) for m in metrics]
        offset = (i - 1.5) * width
        bars = ax.bar(x + offset, reductions, width, label=label, color=colors[i])
        for b, v in zip(bars, reductions):
            ax.text(b.get_x() + b.get_width() / 2, v + (1.5 if v >= 0 else -4),
                    f"{v:+.0f}%", ha="center", fontsize=7.5)

    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels)
    ax.set_ylabel("Reduction vs baseline (%, higher = a-mcp better)")
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_title("Cross-model reductions — a-mcp gen vs baseline (TypeScript, N=5)")
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)


def chart_output_decomposition(data, out: Path):
    """Stacked bars: visible / tool_input / thinking per (model, arm) for gen vs baseline."""
    targets = [
        ("ts-invocation-inline", "Opus inline"),
        ("ts-invocation-script", "Opus script"),
        ("ts-inline-sonnet",     "Sonnet inline"),
        ("ts-script-sonnet",     "Sonnet script"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, (key, title) in zip(axes, [("gen", "a-mcp gen"), ("baseline", "baseline")]):
        labels, visible, tool_input, thinking = [], [], [], []
        for folder, label in targets:
            d = data.get(folder, {})
            if not d:
                continue
            s = d[key]
            labels.append(label)
            visible.append(s["visible"])
            tool_input.append(s["tool_input"])
            thinking.append(s["thinking"])
        x = np.arange(len(labels))
        ax.bar(x, visible,    label="visible text",       color="#88C0D0")
        ax.bar(x, tool_input, label="tool_input bytes",   color="#5E81AC", bottom=visible)
        ax.bar(x, thinking,   label="thinking residual",  color="#BF616A",
               bottom=[v + t for v, t in zip(visible, tool_input)])
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha="right")
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("Output tokens (mean across runs)")
    axes[1].legend(loc="upper right", fontsize=9)
    fig.suptitle("Where the output tokens go — visible / tool_input / thinking")
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)


def chart_multilang_topology(data, out: Path):
    """Multilang on Opus inline — TS / Java / Python, four metrics."""
    targets = [
        ("ts-multilang",     "TypeScript"),
        ("java-multilang",   "Java"),
        ("python-multilang", "Python"),
    ]
    metrics = ["output", "cost", "cache_read", "turns"]
    metric_labels = ["Output tokens", "Cost USD", "cache_read", "Turns"]

    fig, axes = plt.subplots(1, 4, figsize=(14, 4.8))
    for ax, m, lbl in zip(axes, metrics, metric_labels):
        a_mcp, baseline, labels = [], [], []
        for folder, lang in targets:
            d = data.get(folder, {})
            if not d:
                continue
            a_mcp.append(d["gen"][m])
            baseline.append(d["baseline"][m])
            labels.append(lang)
        x = np.arange(len(labels))
        w = 0.38
        ax.bar(x - w/2, a_mcp,    w, label="a-mcp gen",  color="#2E86AB")
        ax.bar(x + w/2, baseline, w, label="baseline",   color="#C73E1D")
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_title(lbl)
        ax.grid(axis="y", alpha=0.3)
        if m == "cost":
            ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:.2f}'))
        elif m == "cache_read":
            ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v/1e6:.1f}M" if v >= 1e6 else f"{v/1e3:.0f}k"))
    axes[0].legend(loc="upper right", fontsize=9)
    fig.suptitle("Topology — multilang on Opus 4.7 (inline arm)")
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)


def chart_headline_absolute(data, out: Path):
    """Absolute numbers: traditional Write loop vs MCP inline vs MCP script.

    Three-bar comparison per model — makes the magnitude of the win visible,
    not just the percentage. The reductions chart is the percentage view; this
    is the absolute view.
    """
    # Use ts-invocation-inline / ts-invocation-script for Opus baselines (within-experiment)
    # and ts-inline-sonnet / ts-script-sonnet for Sonnet.
    rows = {
        ("Opus",   "Baseline (Write loop)"): data.get("ts-invocation-inline", {}).get("baseline", {}),
        ("Opus",   "MCP / inline"):           data.get("ts-invocation-inline", {}).get("gen",      {}),
        ("Opus",   "MCP / script"):           data.get("ts-invocation-script", {}).get("gen",      {}),
        ("Sonnet", "Baseline (Write loop)"): data.get("ts-inline-sonnet",     {}).get("baseline", {}),
        ("Sonnet", "MCP / inline"):           data.get("ts-inline-sonnet",     {}).get("gen",      {}),
        ("Sonnet", "MCP / script"):           data.get("ts-script-sonnet",     {}).get("gen",      {}),
    }
    metrics       = ["output",       "cost",     "turns", "duration_s"]
    metric_labels = ["Output tokens","Cost USD", "Turns", "Wall-clock (s)"]

    def fmt(metric, v):
        if v == 0:
            return ""
        if metric == "cost":
            return f"${v:.2f}"
        if metric == "turns":
            return f"{v:.1f}"
        if metric == "duration_s":
            return f"{v:.0f}s"
        if v >= 1000:
            return f"{v/1000:.1f}k"
        return f"{v:.0f}"

    arms = ["Baseline (Write loop)", "MCP / inline", "MCP / script"]
    arm_colors = {
        "Baseline (Write loop)": "#888888",
        "MCP / inline":           "#2E86AB",
        "MCP / script":           "#C73E1D",
    }
    models = ["Opus", "Sonnet"]

    fig, axes = plt.subplots(2, 2, figsize=(11.5, 7.5))
    width = 0.27
    x = np.arange(len(models))

    for ax, m, lbl in zip(axes.flat, metrics, metric_labels):
        for i, arm in enumerate(arms):
            values = [rows[(model, arm)].get(m, 0) for model in models]
            offset = (i - 1) * width
            bars = ax.bar(x + offset, values, width, label=arm, color=arm_colors[arm])
            for b, v in zip(bars, values):
                if v > 0:
                    ax.text(b.get_x() + b.get_width() / 2, v, " " + fmt(m, v),
                            ha="center", va="bottom", fontsize=7.5, rotation=0)
        ax.set_xticks(x)
        ax.set_xticklabels(models)
        ax.set_title(lbl)
        ax.grid(axis="y", alpha=0.3)
        if m == "cost":
            ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:.2f}'))
        # leave headroom for the bar labels
        ymax = max((rows[(model, arm)].get(m, 0) for model in models for arm in arms), default=1)
        ax.set_ylim(0, ymax * 1.15)

    axes[0, 0].legend(loc="upper right", fontsize=9, framealpha=0.9)
    fig.suptitle("MCP vs traditional Write loop — absolute numbers (TypeScript, N=5)")
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)


def chart_cross_shape_reductions(data, out: Path):
    """Side-by-side reduction-% per (model, arm) for DDD vs modular-monolith.
    Tells the 'topology gap reproduces across shapes' story."""
    # Each row: (DDD folder, monolith folder, label, color)
    rows = [
        ("ts-invocation-inline", "ts-monolith-opus-inline",   "Opus / inline",   "#2E86AB"),
        ("ts-invocation-script", "ts-monolith-opus-script",   "Opus / script",   "#5DA9C9"),
        ("ts-inline-sonnet",     "ts-monolith-sonnet-inline", "Sonnet / inline", "#C73E1D"),
        ("ts-script-sonnet",     "ts-monolith-sonnet-script", "Sonnet / script", "#E08566"),
    ]
    metrics       = ["output", "cost", "turns", "duration_s"]
    metric_labels = ["Output\ntokens", "Cost", "Turns", "Wall-clock"]

    fig, axes = plt.subplots(1, 4, figsize=(15, 5.5), sharey=True)
    width = 0.34
    x_pos = np.arange(len(rows))

    for ax, m, lbl in zip(axes, metrics, metric_labels):
        ddd_red = []
        mono_red = []
        labels = []
        for ddd_folder, mono_folder, label, _ in rows:
            d = data.get(ddd_folder, {})
            mo = data.get(mono_folder, {})
            if d:
                ddd_red.append(reduction_pct(d["gen"][m], d["baseline"][m]))
            else:
                ddd_red.append(0)
            if mo:
                mono_red.append(reduction_pct(mo["gen"][m], mo["baseline"][m]))
            else:
                mono_red.append(0)
            labels.append(label)

        ax.bar(x_pos - width/2, ddd_red,  width, label="DDD (simple)", color="#888888")
        ax.bar(x_pos + width/2, mono_red, width, label="Monolith (complex)", color="#2E7D32")
        for i, (a, b) in enumerate(zip(ddd_red, mono_red)):
            ax.text(i - width/2, a + (1.5 if a >= 0 else -4), f"{a:+.0f}%",
                    ha="center", fontsize=7)
            ax.text(i + width/2, b + (1.5 if b >= 0 else -4), f"{b:+.0f}%",
                    ha="center", fontsize=7)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=8.5)
        ax.set_title(lbl)
        ax.axhline(0, color="black", linewidth=0.5)
        ax.grid(axis="y", alpha=0.3)

    axes[0].set_ylabel("Reduction vs baseline (%, higher = a-mcp better)")
    axes[0].legend(loc="upper right", fontsize=9)
    fig.suptitle("Topology gap reproduces across spec shapes — DDD vs modular-monolith")
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)


def chart_baseline_cache_per_run(out: Path):
    """Per-run baseline cache_read across canonical TS runs — exposes the Sonnet cap."""
    targets = [
        ("ts-invocation-inline", "Opus / inline",   "Opus",   "inline"),
        ("ts-inline-sonnet",     "Sonnet / inline", "Sonnet", "inline"),
        ("ts-script-sonnet",     "Sonnet / script", "Sonnet", "script"),
    ]
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    colors  = {"Opus": "#2E86AB", "Sonnet": "#C73E1D"}
    markers = {"inline": "o", "script": "s"}
    for folder, label, model, arm in targets:
        path = RESULTS / folder
        if not path.exists():
            continue
        runs = sorted(path.glob("run-*"))
        ys = []
        for r in runs:
            rj = r / "b-baseline" / "result.json"
            if rj.exists():
                d = json.loads(rj.read_text())
                ys.append((d.get("usage") or {}).get("cache_read_input_tokens", 0))
        xs = list(range(1, len(ys) + 1))
        ax.plot(xs, ys, marker=markers[arm], linewidth=1.5, markersize=11,
                label=label, color=colors[model], alpha=0.85)

    ax.axhline(46054, color="gray", linestyle="--", alpha=0.6, linewidth=1)
    ax.text(5.05, 46054, " 46,054 — system-prompt-only cap",
            va="center", fontsize=8.5, color="gray")
    ax.set_yscale("log")
    ax.set_xlabel("Run index within RUNS=5 batch")
    ax.set_ylabel("Baseline cache_read tokens (log scale)")
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_title("Baseline cache_read per run — Sonnet caps, Opus accumulates\n(why the cost story is model-conditional)")
    ax.legend(loc="upper left", fontsize=9.5, framealpha=0.95)
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)


# ─── Entry point ───────────────────────────────────────────────────────────────

def main():
    FIGURES.mkdir(exist_ok=True)
    data = {}
    skipped = []
    for folder, *_ in EXPERIMENTS:
        path = RESULTS / folder
        if path.exists():
            data[folder] = folder_means(path)
        else:
            skipped.append(folder)

    chart_headline_absolute(data, FIGURES / "headline-absolute.png")
    chart_cross_model_reductions(data, FIGURES / "cross-model-reductions.png")
    chart_cross_shape_reductions(data, FIGURES / "cross-shape-reductions.png")
    chart_output_decomposition(data, FIGURES / "output-decomposition.png")
    chart_multilang_topology(data, FIGURES / "multilang-topology.png")
    chart_baseline_cache_per_run(FIGURES / "baseline-cache-per-run.png")

    print(f"Wrote {len(list(FIGURES.glob('*.png')))} figures to {FIGURES}/")
    for f in sorted(FIGURES.glob("*.png")):
        size_kb = f.stat().st_size // 1024
        print(f"  {f.name}  ({size_kb}KB)")
    if skipped:
        print(f"\nSkipped (folder not present yet): {', '.join(skipped)}")


if __name__ == "__main__":
    main()
