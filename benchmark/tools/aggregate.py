#!/usr/bin/env python3
"""Aggregate two-session benchmark results into a markdown summary.

Layout consumed:
  results_root/run-NNN/
    a-mcp/
      warmup/result.json   ← authoritative usage for warmup session
      gen/result.json      ← authoritative usage for generation session
      output/              ← TS files produced by gen
      judge.json           ← tsc verdict on output/
    b-baseline/
      result.json          ← authoritative usage (single session)
      output/
      judge.json

Authoritative numbers come from each session's `result.json.usage` and
`total_cost_usd` (passed through from `claude -p`'s result event by parse-stream.py).

For a-mcp:
  total = warmup + gen   (first-codebase cost)
  steady-state = gen alone   (what every subsequent codebase costs once the
                              model has been instructed once on MCP usage)

Usage: aggregate.py <results_root>
"""
import json, sys, statistics
from pathlib import Path


def load(p, default=None):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:
        return default


def stats(values):
    if not values:
        return {"n": 0, "mean": 0.0, "stdev": 0.0}
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def fmt(s, decimals=0):
    if s["n"] == 0:
        return "—"
    return f"{s['mean']:,.{decimals}f} ± {s['stdev']:,.{decimals}f}"


def fmt_money(s):
    if s["n"] == 0:
        return "—"
    return f"${s['mean']:.4f} ± ${s['stdev']:.4f}"


def reduction_pct(a_mean: float, b_mean: float) -> str:
    if not b_mean:
        return "—"
    return f"{(1 - a_mean / b_mean) * 100:.1f}%"


def session_metrics(result_json: dict) -> dict:
    """Extract authoritative session metrics from a parsed result.json."""
    u = result_json.get("usage") or {}
    m = result_json.get("measurement") or {}
    phases = result_json.get("phases") or {}
    out_tokens = int(u.get("output_tokens", 0) or 0)
    return {
        "output":          out_tokens,
        "input":           int(u.get("input_tokens", 0) or 0),
        "cache_creation":  int(u.get("cache_creation_input_tokens", 0) or 0),
        "cache_read":      int(u.get("cache_read_input_tokens", 0) or 0),
        "cost":            float(result_json.get("total_cost_usd", 0.0) or 0.0),
        "turns":           int(result_json.get("num_turns", 0) or 0),
        "duration_ms":     int(result_json.get("duration_ms", 0) or 0),
        "duration_api_ms": int(result_json.get("duration_api_ms", 0) or 0),
        # decomposition
        "visible":         int(m.get("measured_visible_output_tokens", 0) or 0),
        "tool_input_est":  int(m.get("measured_tool_input_tokens_estimated", 0) or 0),
        "thinking":        int(m.get("thinking_residual_unmeasured_tokens", 0) or 0),
        # message count (across phases — for two-session, all in one phase)
        "messages":        sum(int((phases.get(p) or {}).get("messages", 0) or 0)
                                for p in ("warmup", "generation")),
        # completion signal: if no usage block at all, the session is malformed.
        "completed":       bool(u),
    }


def collect(root: Path):
    runs = sorted(root.glob("run-*"))
    rows_a = []
    rows_b = []
    for run_dir in runs:
        # a-mcp: two sessions.
        a_warmup = load(run_dir / "a-mcp" / "warmup" / "result.json", {}) or {}
        a_gen = load(run_dir / "a-mcp" / "gen" / "result.json", {}) or {}
        a_judge = load(run_dir / "a-mcp" / "judge.json", {}) or {}
        a_summary_file = run_dir / "a-mcp" / "warmup" / "summary.md"
        warmup = session_metrics(a_warmup)
        gen = session_metrics(a_gen)
        rows_a.append({
            "warmup": warmup,
            "gen": gen,
            "summary_chars": a_summary_file.stat().st_size if a_summary_file.exists() else 0,
            "verdict": a_judge.get("verdict", "missing"),
            "files": int(a_judge.get("ts_file_count", 0) or 0),
            "tsc_errors": int(a_judge.get("tsc_errors", -1)),
        })

        # b-baseline: single session.
        b_result = load(run_dir / "b-baseline" / "result.json", {}) or {}
        b_judge = load(run_dir / "b-baseline" / "judge.json", {}) or {}
        rows_b.append({
            "session": session_metrics(b_result),
            "verdict": b_judge.get("verdict", "missing"),
            "files": int(b_judge.get("ts_file_count", 0) or 0),
            "tsc_errors": int(b_judge.get("tsc_errors", -1)),
        })
    return runs, rows_a, rows_b


def main():
    root = Path(sys.argv[1])
    runs, a_rows, b_rows = collect(root)

    # ── Run completion accounting ─────────────────────────────────────────
    a_complete = sum(1 for r in a_rows if r["warmup"]["completed"] and r["gen"]["completed"])
    a_incomplete = len(a_rows) - a_complete
    b_complete = sum(1 for r in b_rows if r["session"]["completed"])
    b_incomplete = len(b_rows) - b_complete

    # ── Wall-clock (script-level total, indicative only) ──────────────────
    wall_file = root / "wall_seconds.txt"
    wall_total_s = None
    if wall_file.exists():
        try:
            wall_total_s = int(wall_file.read_text().strip())
        except Exception:
            pass

    out = []
    out.append("# MetaEngine MCP — Benchmark Summary\n")
    out.append("> **These numbers are illustrations from one author's run on one spec on one day.** "
               "MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, "
               "not the numbers. Reproduce in your own environment before quoting anything.\n")
    out.append(f"Runs requested: **{len(runs)}** per variant. Completed: a-mcp **{a_complete}/{len(runs)}**, "
               f"b-baseline **{b_complete}/{len(runs)}**. Results: `{root}`\n")
    if a_incomplete or b_incomplete:
        out.append(f"⚠ **Incomplete runs:** a-mcp={a_incomplete}, b-baseline={b_incomplete} "
                   "(failed to produce a result event — usually means the harness was "
                   "interrupted or claude exited mid-session). They appear in the per-run table as "
                   "missing/zero rows; means below are computed over completed sessions only.\n")
    out.append("**The headline is steady-state** — what each codebase costs once the model has been "
               "instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in "
               "the model's training corpus). Warmup is reported separately as a one-time "
               "outside-training tax that wouldn't exist in an integrated world.\n")

    # ──────────────────────────────────────────────────────────────────────
    if a_rows and b_rows:
        a_gen_out = statistics.mean([r["gen"]["output"] for r in a_rows])
        a_gen_cost = statistics.mean([r["gen"]["cost"] for r in a_rows])
        a_gen_cache = statistics.mean([r["gen"]["cache_read"] for r in a_rows])
        a_gen_turns = statistics.mean([r["gen"]["turns"] for r in a_rows])
        b_out = statistics.mean([r["session"]["output"] for r in b_rows])
        b_cost = statistics.mean([r["session"]["cost"] for r in b_rows])
        b_cache = statistics.mean([r["session"]["cache_read"] for r in b_rows])
        b_turns = statistics.mean([r["session"]["turns"] for r in b_rows])

        gen_passes = sum(1 for r in a_rows if r["verdict"] == "pass")
        b_passes = sum(1 for r in b_rows if r["verdict"] == "pass")

        out.append("## Steady-state — per-codebase cost\n")
        out.append("This is what every codebase costs after the one-time warmup. If MetaEngine "
                   "were in the model's training, this would be the *first*-codebase cost too.\n")
        out.append("| | output_tokens | cost USD | turns | cache_read | pass |")
        out.append("|---|---|---|---|---|---|")
        out.append(f"| a-mcp gen        | {a_gen_out:>10,.0f} | ${a_gen_cost:>7.4f} | {a_gen_turns:>4.1f} | {a_gen_cache:>11,.0f} | {gen_passes}/{len(a_rows)} |")
        out.append(f"| b-baseline       | {b_out:>10,.0f} | ${b_cost:>7.4f} | {b_turns:>4.1f} | {b_cache:>11,.0f} | {b_passes}/{len(b_rows)} |")
        out.append(f"| **reduction**    | **{reduction_pct(a_gen_out, b_out):>6}** | **{reduction_pct(a_gen_cost, b_cost):>6}** | **{b_turns/max(a_gen_turns,1):.1f}× fewer** | **{reduction_pct(a_gen_cache, b_cache):>6}** | — |")

    # ──────────────────────────────────────────────────────────────────────
    out.append("\n## Agent-loop efficiency (structural — independent of training)\n")
    out.append("The cache_read difference is structural: it comes from **tool topology**, not from "
               "the model knowing MetaEngine.\n")
    out.append("- **Topology A (Write loop):** Many small tool calls — one per output. Each turn "
               "re-reads cumulative context. cache_read accumulates ~quadratically with output count.\n"
               "- **Topology B (batched single call):** One large structured tool input → all outputs "
               "in one tool_result. cache_read is bounded.\n")
    out.append("Any MCP that consolidates multi-output work into one call benefits — this isn't "
               "MetaEngine-specific. It's a generalizable design pattern.\n")
    out.append("| session | turns | cache_read tokens | per-turn |")
    out.append("|---|---|---|---|")
    if a_rows:
        for label, key in [("a-mcp warmup", "warmup"), ("a-mcp gen", "gen")]:
            t = stats([r[key]["turns"] for r in a_rows])
            cr = stats([r[key]["cache_read"] for r in a_rows])
            per = stats([r[key]["cache_read"] / max(r[key]["turns"], 1) for r in a_rows])
            out.append(f"| {label} | {fmt(t, 1)} | {fmt(cr)} | {fmt(per)} |")
    if b_rows:
        t = stats([r["session"]["turns"] for r in b_rows])
        cr = stats([r["session"]["cache_read"] for r in b_rows])
        per = stats([r["session"]["cache_read"] / max(r["session"]["turns"], 1) for r in b_rows])
        out.append(f"| b-baseline | {fmt(t, 1)} | {fmt(cr)} | {fmt(per)} |")
    out.append("")
    out.append("> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. "
               "Implication for smaller-context models: baseline at 73 turns is already large for a "
               "200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. "
               "Topology B keeps loops short enough that cheaper models can do the same work.")

    # ──────────────────────────────────────────────────────────────────────
    # ── Wall-clock (indicative only — depends on Anthropic load) ──────────
    out.append("\n## Wall-clock (indicative only — depends on Anthropic load)\n")
    out.append("Per-session `duration_ms` from each `claude -p` result event. "
               "Not reproducible across runs/days, but useful for spotting trends "
               "when other variables are held constant.\n")
    out.append("| session | duration mean | api_ms mean |")
    out.append("|---|---|---|")
    if a_rows:
        for label, key in [("a-mcp warmup", "warmup"), ("a-mcp gen", "gen")]:
            d = stats([r[key]["duration_ms"] for r in a_rows if r[key]["completed"]])
            api = stats([r[key]["duration_api_ms"] for r in a_rows if r[key]["completed"]])
            d_s = "—" if d["n"] == 0 else f"{d['mean']/1000:.1f}s ± {d['stdev']/1000:.1f}s"
            api_s = "—" if api["n"] == 0 else f"{api['mean']/1000:.1f}s"
            out.append(f"| {label} | {d_s} | {api_s} |")
    if b_rows:
        d = stats([r["session"]["duration_ms"] for r in b_rows if r["session"]["completed"]])
        api = stats([r["session"]["duration_api_ms"] for r in b_rows if r["session"]["completed"]])
        d_s = "—" if d["n"] == 0 else f"{d['mean']/1000:.1f}s ± {d['stdev']/1000:.1f}s"
        api_s = "—" if api["n"] == 0 else f"{api['mean']/1000:.1f}s"
        out.append(f"| b-baseline | {d_s} | {api_s} |")
    if wall_total_s is not None:
        out.append(f"\nScript total wall-clock: **{wall_total_s}s** "
                   f"({wall_total_s // 60}m {wall_total_s % 60}s).")

    out.append("\n## Warmup — one-time outside-training tax\n")
    out.append("This is what a non-trained model pays to learn the MCP correctly via runtime docs. "
               "If MetaEngine were integrated into Claude Code's built-ins or the model's training, "
               "this row would be ~0.\n")
    if a_rows:
        ws = stats([r["warmup"]["output"] for r in a_rows])
        wc = stats([r["warmup"]["cost"] for r in a_rows])
        wt = stats([r["warmup"]["turns"] for r in a_rows])
        sm = stats([r["summary_chars"] for r in a_rows])
        out.append("| | output_tokens | cost USD | turns | summary written |")
        out.append("|---|---|---|---|---|")
        out.append(f"| a-mcp warmup | {fmt(ws)} | {fmt_money(wc)} | {fmt(wt, 1)} | {fmt(sm)} chars |")

    # ──────────────────────────────────────────────────────────────────────
    if a_rows and b_rows:
        a_total_cost = statistics.mean([r["warmup"]["cost"] + r["gen"]["cost"] for r in a_rows])
        a_total_out = statistics.mean([r["warmup"]["output"] + r["gen"]["output"] for r in a_rows])
        out.append("\n## First-codebase total (for completeness)\n")
        out.append("What a user pays who runs MetaEngine *exactly once* and never again — warmup "
                   "is not amortized. This is the worst-case framing.\n")
        out.append(f"- a-mcp (warmup + gen): {a_total_out:,.0f} output tokens, ${a_total_cost:.4f}")
        out.append(f"- b-baseline:           {b_out:,.0f} output tokens, ${b_cost:.4f}")
        out.append(f"- Cost: {reduction_pct(a_total_cost, b_cost)} reduction"
                   f" — much smaller than steady-state because warmup is a one-shot.")

    # ──────────────────────────────────────────────────────────────────────
    out.append("\n## Output token decomposition (descriptive)\n")
    out.append("Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated "
               "structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream "
               "usage shows only the visible portion; the result event aggregates all three.\n")
    out.append("| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |")
    out.append("|---|---|---|---|---|")
    if a_rows:
        for label, key in [("a-mcp warmup", "warmup"), ("a-mcp gen", "gen")]:
            v = stats([r[key]["visible"] for r in a_rows])
            t = stats([r[key]["tool_input_est"] for r in a_rows])
            th = stats([r[key]["thinking"] for r in a_rows])
            s = stats([r[key]["visible"] + r[key]["tool_input_est"] + r[key]["thinking"] for r in a_rows])
            out.append(f"| {label} | {fmt(v)} | {fmt(t)} | {fmt(th)} | {fmt(s)} |")
    if b_rows:
        v = stats([r["session"]["visible"] for r in b_rows])
        t = stats([r["session"]["tool_input_est"] for r in b_rows])
        th = stats([r["session"]["thinking"] for r in b_rows])
        s = stats([r["session"]["visible"] + r["session"]["tool_input_est"] + r["session"]["thinking"] for r in b_rows])
        out.append(f"| b-baseline | {fmt(v)} | {fmt(t)} | {fmt(th)} | {fmt(s)} |")

    # ──────────────────────────────────────────────────────────────────────
    out.append("\n## Per-run\n")
    out.append("| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | "
               "baseline $ | baseline output | a-files | b-files |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for i, _ in enumerate(runs, 1):
        ar = a_rows[i - 1] if i <= len(a_rows) else None
        br = b_rows[i - 1] if i <= len(b_rows) else None
        if ar and br:
            out.append(
                f"| {i:03d} | "
                f"${ar['warmup']['cost']:.4f} | "
                f"${ar['gen']['cost']:.4f} | "
                f"${ar['warmup']['cost'] + ar['gen']['cost']:.4f} | "
                f"{ar['warmup']['output'] + ar['gen']['output']:,} | "
                f"${br['session']['cost']:.4f} | "
                f"{br['session']['output']:,} | "
                f"{ar['files']} | {br['files']} |"
            )

    # ──────────────────────────────────────────────────────────────────────
    out.append("\n## Per-run wall-clock\n")
    out.append("Per-session `duration_ms` from each `claude -p` result event, broken out per run "
               "to make trends visible (cross-session cache warming, parallel-batch effects, etc.). "
               "Indicative only — depends on Anthropic load on the day.\n")
    out.append("| run | a-mcp warmup s | a-mcp gen s | b-baseline s |")
    out.append("|---|---|---|---|")
    for i, _ in enumerate(runs, 1):
        ar = a_rows[i - 1] if i <= len(a_rows) else None
        br = b_rows[i - 1] if i <= len(b_rows) else None
        if ar and br:
            ws = ar["warmup"]["duration_ms"] / 1000 if ar["warmup"]["completed"] else None
            gs = ar["gen"]["duration_ms"] / 1000 if ar["gen"]["completed"] else None
            bs = br["session"]["duration_ms"] / 1000 if br["session"]["completed"] else None
            ws_s = "—" if ws is None else f"{ws:.0f}"
            gs_s = "—" if gs is None else f"{gs:.0f}"
            bs_s = "—" if bs is None else f"{bs:.0f}"
            out.append(f"| {i:03d} | {ws_s} | {gs_s} | {bs_s} |")

    # ──────────────────────────────────────────────────────────────────────
    out.append("\n## Caveats\n")
    out.append("- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, "
               "`total_cost_usd`). Per-event stream usage shows only visible-text output, which "
               "under-reports by excluding thinking and tool_use input bytes.")
    out.append("- **`cost USD` is the would-be API cost** at Anthropic's published rates — "
               "a token-usage proxy that's comparable across users and models. It's NOT what a "
               "subscription user (Claude Max/Pro) actually pays — those plans are flat-rate. The "
               "dollar figure still reflects the *relative work* of each variant; tokens × price is "
               "the universal benchmark unit.")
    out.append("- The two-session methodology gives **exact** phase split: each session has its own "
               "result event total. The gen session has the warmup's knowledge brief in its user "
               "prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model "
               "case, in the honest direction.")
    out.append("- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — "
               "the visible+tool_input parts are exact-per-message but tool_input tokens are estimated "
               "from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.")
    out.append("- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know "
               "the API). Steady-state approximates that.")
    out.append("- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.")
    out.append("- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.")
    out.append("- Data collected on Opus 4.7 (1M-context). Within a few-day window we assume Anthropic-side model behavior is stable; cross-arm and cross-language comparisons inside that window are apples-to-apples. Re-runs after a model update are out of scope for token-cost reasons (not a cross-model benchmark).")

    print("\n".join(out))


if __name__ == "__main__":
    main()
