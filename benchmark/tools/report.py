"""Render an experiment's observed measurements and their limits."""
import statistics


class BenchmarkReport:
    def render(self, name, records):
        groups = {phase: [r for r in records if r["phase"] == phase]
                  for phase in ["generation", "baseline", "warmup"]}
        lines = [
            "# MetaEngine MCP — Benchmark Summary", "",
            f"Experiment: `{name}`. Means [min–max]; all recorded runs, including failed judgments.", "",
            "Regenerated from original streams with measurement schema 2. Historical result.json files",
            "remain unchanged; their legacy visible/thinking decomposition must not be used.", "",
            "## Generation with a prepared brief", "",
            "The assisted generation session receives the separate warm-up's brief in its prompt.",
            "This measures a prepared workflow; it does not simulate training or guarantee future cache state.", "",
            "| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for phase, rows in groups.items():
            passes = "—" if phase == "warmup" else f"{sum(r['verdict'] == 'pass' for r in rows)}/{len(rows)}"
            values = [self.format(rows, key, 1 if key in ["assistant_messages", "tool_calls"] else 0)
                      for key in ["assistant_messages", "tool_calls", "output_tokens", "cache_read_input_tokens"]]
            lines.append(f"| {phase} | {len(rows)} | " + " | ".join(values) + f" | {passes} |")
        lines += ["", "## Duration and recorded API-equivalent cost", "",
                  "These are the original result event's duration and cost fields. Cost is a dated",
                  "API-price calculation, not a subscription bill or a measure of subscription allowance.", "",
                  "| Session | Duration ms | Recorded cost USD |", "| --- | --- | --- |"]
        for phase, rows in groups.items():
            lines.append(f"| {phase} | {self.format(rows, 'duration_ms')} | {self.format(rows, 'recorded_cost_usd', 4)} |")
        totals = [{key: warmup[key] + generation[key] for key in ["output_tokens", "duration_ms", "recorded_cost_usd"]}
                  for warmup, generation in zip(groups["warmup"], groups["generation"])]
        lines += ["", "Warm-up plus generation, per paired run:", "",
                  f"- Output tokens: {self.format(totals, 'output_tokens')}",
                  f"- Summed session duration ms: {self.format(totals, 'duration_ms')}",
                  f"- Recorded cost USD: {self.format(totals, 'recorded_cost_usd', 4)}", "",
                  "## Observable content size", "",
                  "Characters count text blocks and Python's sorted-key JSON serialization of tool input",
                  "(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.",
                  "Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.", "",
                  "| Session | Text characters | Tool-input characters |", "| --- | --- | --- |"]
        for phase, rows in groups.items():
            lines.append(f"| {phase} | {self.format(rows, 'text_characters')} | {self.format(rows, 'tool_input_characters')} |")
        lines += ["", "## Per-run message and call counts", "",
                  "`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may",
                  "share one message. It is a trace-observed response count, not a count of invisible retries.",
                  "In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.", "",
                  "| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |",
                  "| --- | --- | --- | --- | --- | --- | --- |"]
        for row in records:
            lines.append(f"| {row['run']} | {row['phase']} | {row['claude_num_turns']} | {row['assistant_messages']} | {row['tool_calls']} | {row['cache_read_input_tokens']:,} | {row['verdict'] or '—'} |")
        lines += ["", "## Caveats", "",
                  "- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.",
                  "- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.",
                  "- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.",
                  "- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.",
                  "- A pass checks the compiler and the checked-in structural judge, not runtime semantics.",
                  "- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.",
                  "- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.", ""]
        return "\n".join(lines)

    def format(self, rows, key, decimals=0):
        values = [row[key] for row in rows]
        return f"{statistics.mean(values):,.{decimals}f} [{min(values):,.{decimals}f}–{max(values):,.{decimals}f}]"
